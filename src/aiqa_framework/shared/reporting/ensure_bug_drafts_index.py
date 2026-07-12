"""Finalize helper: guarantee test-output/ai/bug-drafts/index.html exists —
green executions render the "No pending drafts" state instead of a missing
folder. Invoked by the qa-agent finalize step:

    uv run python -m aiqa_framework.shared.reporting.ensure_bug_drafts_index
"""

from aiqa_framework.shared.reporting.bug_draft_writer import ensure_bug_drafts_index

if __name__ == "__main__":
    ensure_bug_drafts_index()
    print("[bug-draft] index ensured at test-output/ai/bug-drafts/index.html")
