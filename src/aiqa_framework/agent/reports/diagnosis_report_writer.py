"""Write test-output/ai/diagnosis.md from a RunDiagnosis."""

from __future__ import annotations

from pathlib import Path

from aiqa_framework.agent.schemas.diagnosis import RunDiagnosis
from aiqa_framework.agent.utils.paths import ai_qa_out_dir


def write_diagnosis_md(diag: RunDiagnosis) -> Path:
    lines = [
        f"# Failure diagnosis — run `{diag.run_id}`",
        "",
        f"- Provider: **{diag.provider_name}**{' (dry-run/deterministic)' if diag.dry_run else ''}",
        f"- Total failures: **{diag.total_failures}**",
        f"- Clusters: **{len(diag.clusters)}**",
        "",
    ]
    for c in sorted(diag.clusters, key=lambda x: x.count, reverse=True):
        lines += [
            f"## {c.sample_title} ×{c.count}  ·  _{c.category}_",
            f"- Error: `{c.error_message}`",
            f"- Diagnosis: {c.summary}",
            "",
        ]
    path = ai_qa_out_dir() / "diagnosis.md"
    path.write_text("\n".join(lines))
    return path
