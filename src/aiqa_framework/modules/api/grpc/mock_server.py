"""In-process mock gRPC server (port of mock-server.ts). Requires generated
stubs (``poe proto-gen``).

Special inputs the sample specs rely on:
  - player_id "unknown"  -> GetBalance NOT_FOUND
  - player_id "slow"     -> GetBalance delays 0.5s (trips a short deadline)
  - PlaceBet without auth metadata -> UNAUTHENTICATED
  - PlaceBet amount <= 0           -> INVALID_ARGUMENT
  - PlaceBet amount  > 1000        -> FAILED_PRECONDITION
"""

from __future__ import annotations

import os
import sys
import time
from concurrent import futures

import grpc

# Generated stubs (poe proto-gen) live in ./generated and use a bare
# ``import game_pb2``; put that dir on sys.path BEFORE importing them.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "generated"))

import game_pb2  # type: ignore  # noqa: E402
import game_pb2_grpc  # type: ignore  # noqa: E402

STARTING_BALANCE = 1000


class GameServicer(game_pb2_grpc.GameServiceServicer):
    def GetBalance(self, request, context):
        if request.player_id == "unknown":
            context.abort(grpc.StatusCode.NOT_FOUND, "player not found")
        if request.player_id == "slow":
            time.sleep(0.5)
        return game_pb2.BalanceResponse(
            player_id=request.player_id, balance=STARTING_BALANCE, currency="USD"
        )

    def PlaceBet(self, request, context):
        md = dict(context.invocation_metadata())
        if "authorization" not in md:
            context.abort(grpc.StatusCode.UNAUTHENTICATED, "missing auth token")
        if request.amount <= 0:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "amount must be > 0")
        if request.amount > STARTING_BALANCE:
            context.abort(grpc.StatusCode.FAILED_PRECONDITION, "insufficient funds")
        return game_pb2.PlaceBetResponse(
            bet_id="bet-1", accepted=True, balance_after=STARTING_BALANCE - request.amount
        )

    def StreamGameState(self, request, context):
        for i, phase in enumerate(["betting", "dealing", "result"]):
            yield game_pb2.GameStateEvent(
                table_id=request.table_id, phase=phase, sequence=i + 1, payload="{}"
            )

    def SendActions(self, request_iterator, context):
        total = 0
        count = 0
        for action in request_iterator:
            total += action.amount
            count += 1
        return game_pb2.RoundSummary(
            round_id="round-1", total_staked=total, net_result=-total, action_count=count
        )

    def PlayLive(self, request_iterator, context):
        for action in request_iterator:
            yield game_pb2.GameStateEvent(
                table_id="live-1", phase="ack", sequence=action.amount, payload=action.action
            )


def start_grpc_mock(port: int = 0) -> tuple[grpc.Server, int]:
    """Start the mock on ``port`` (0 = ephemeral). Returns (server, bound_port)."""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=8))
    game_pb2_grpc.add_GameServiceServicer_to_server(GameServicer(), server)
    bound = server.add_insecure_port(f"0.0.0.0:{port}")
    server.start()
    return server, bound


if __name__ == "__main__":
    srv, bound_port = start_grpc_mock(int(os.environ.get("GRPC_PORT", "50051")))
    print(f"[grpc-mock] casino GameService mock listening on 0.0.0.0:{bound_port}")
    srv.wait_for_termination()
