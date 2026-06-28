"""SAMPLE gRPC spec — casino GameService over the in-process mock (port of
sample.grpc.spec.ts). Covers every RPC type + deadlines + metadata auth +
typed STATUS CODES. Requires generated stubs (``poe proto-gen``).
"""

from __future__ import annotations

import grpc
import pytest

from aiqa_framework.config.tags import TAGS, jira, tags


@tags(TAGS.GRPC, TAGS.REGRESSION, TAGS.P0)
@jira("PROJ-GRPC-1")
def test_get_balance(game_client) -> None:
    res = game_client.get_balance("p-1")
    assert res.player_id == "p-1"
    assert res.balance == 1000
    assert res.currency == "USD"


@tags(TAGS.GRPC, TAGS.REGRESSION, TAGS.P1)
@jira("PROJ-GRPC-1")
def test_unknown_player_not_found(game_client) -> None:
    with pytest.raises(grpc.RpcError) as exc:
        game_client.get_balance("unknown")
    assert exc.value.code() == grpc.StatusCode.NOT_FOUND


@tags(TAGS.GRPC, TAGS.REGRESSION, TAGS.P1)
@jira("PROJ-GRPC-1")
def test_short_deadline_trips_deadline_exceeded(game_client) -> None:
    with pytest.raises(grpc.RpcError) as exc:
        game_client.get_balance("slow", deadline=0.1)
    assert exc.value.code() == grpc.StatusCode.DEADLINE_EXCEEDED


@tags(TAGS.GRPC, TAGS.REGRESSION, TAGS.P0)
@jira("PROJ-GRPC-1")
def test_place_bet_without_auth_unauthenticated(game_client_no_auth) -> None:
    with pytest.raises(grpc.RpcError) as exc:
        game_client_no_auth.place_bet("p-1", "r-1", 50, "red")
    assert exc.value.code() == grpc.StatusCode.UNAUTHENTICATED


@tags(TAGS.GRPC, TAGS.REGRESSION, TAGS.P1)
@jira("PROJ-GRPC-1")
def test_place_bet_validation_status_codes(game_client) -> None:
    with pytest.raises(grpc.RpcError) as exc:
        game_client.place_bet("p-1", "r-1", 0, "red")
    assert exc.value.code() == grpc.StatusCode.INVALID_ARGUMENT

    with pytest.raises(grpc.RpcError) as exc:
        game_client.place_bet("p-1", "r-1", 5000, "red")
    assert exc.value.code() == grpc.StatusCode.FAILED_PRECONDITION

    ok = game_client.place_bet("p-1", "r-1", 200, "red")
    assert ok.accepted is True
    assert ok.balance_after == 800


@tags(TAGS.GRPC, TAGS.REGRESSION, TAGS.P1)
@jira("PROJ-GRPC-1")
def test_server_streaming(game_client) -> None:
    events = game_client.stream_game_state("t-7")
    assert [e.phase for e in events] == ["betting", "dealing", "result"]
    assert all(e.table_id == "t-7" for e in events)


@tags(TAGS.GRPC, TAGS.REGRESSION, TAGS.P2)
@jira("PROJ-GRPC-1")
def test_client_streaming(game_client) -> None:
    summary = game_client.send_actions(
        [
            {"player_id": "p-1", "action": "bet", "amount": 100},
            {"player_id": "p-1", "action": "bet", "amount": 150},
        ]
    )
    assert summary.action_count == 2
    assert summary.total_staked == 250


@tags(TAGS.GRPC, TAGS.REGRESSION, TAGS.P2)
@jira("PROJ-GRPC-1")
def test_bidirectional(game_client) -> None:
    events = game_client.play_live(
        [
            {"player_id": "p-1", "action": "hit", "amount": 1},
            {"player_id": "p-1", "action": "stand", "amount": 2},
        ]
    )
    assert len(events) == 2
    assert all(e.phase == "ack" for e in events)
