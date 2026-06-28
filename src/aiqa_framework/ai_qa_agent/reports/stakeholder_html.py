"""Self-contained stakeholder HTML report (Jinja2) — test-output/ai/test-report.html."""

from __future__ import annotations

from pathlib import Path

from jinja2 import Template

from aiqa_framework.ai_qa_agent.schemas.diagnosis import RunDiagnosis
from aiqa_framework.ai_qa_agent.utils.paths import ai_qa_out_dir

_TEMPLATE = Template(
    """<!doctype html><html><head><meta charset="utf-8">
<title>AI QA Report — {{ run_id }}</title>
<style>
 body{font-family:system-ui,Arial,sans-serif;margin:2rem;color:#1f2937}
 h1{font-size:1.4rem} .pill{display:inline-block;padding:.2rem .6rem;border-radius:999px;font-weight:600}
 .ok{background:#dcfce7;color:#166534}.bad{background:#fee2e2;color:#991b1b}
 table{border-collapse:collapse;width:100%;margin-top:1rem}
 th,td{border:1px solid #e5e7eb;padding:.5rem .6rem;text-align:left;font-size:.9rem}
 th{background:#f3f4f6} code{background:#f3f4f6;padding:.1rem .3rem;border-radius:4px}
</style></head><body>
<h1>AI QA Agent report <small>run {{ run_id }}</small></h1>
<p>Provider: <b>{{ provider }}</b>{{ ' (deterministic)' if dry_run else '' }} ·
   Total failures: <span class="pill {{ 'ok' if total==0 else 'bad' }}">{{ total }}</span></p>
{% if clusters %}
<table><thead><tr><th>Test</th><th>×</th><th>Category</th><th>Error</th><th>Diagnosis</th></tr></thead><tbody>
{% for c in clusters %}<tr><td>{{ c.sample_title }}</td><td>{{ c.count }}</td><td>{{ c.category }}</td>
<td><code>{{ c.error_message }}</code></td><td>{{ c.summary }}</td></tr>{% endfor %}
</tbody></table>
{% else %}<p class="pill ok">✅ No failures.</p>{% endif %}
</body></html>"""
)


def write_stakeholder_html(diag: RunDiagnosis) -> Path:
    html = _TEMPLATE.render(
        run_id=diag.run_id,
        provider=diag.provider_name,
        dry_run=diag.dry_run,
        total=diag.total_failures,
        clusters=sorted(diag.clusters, key=lambda c: c.count, reverse=True),
    )
    path = ai_qa_out_dir() / "test-report.html"
    path.write_text(html)
    return path
