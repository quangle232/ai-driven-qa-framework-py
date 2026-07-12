"""Bug DRAFT writer — the human-approval side of the failure → Jira flow
(port of core/jira/bug-draft-writer.ts).

A final-attempt failure never files a Jira bug directly (see the root
``conftest.py`` hook, ``JIRA_AUTO_BUG`` gate). Instead this module records the
draft twice:

- ``<slug>.json`` — machine-readable, what the qa-agent reads to file the bug
  via the Jira MCP AFTER the user approves it;
- ``<slug>.html`` — self-contained page for humans: summary, parent story,
  reproduction command, error, and any image evidence embedded as base64
  (portable — survives copying the file anywhere).

It also regenerates ``bug-drafts/index.html`` listing every pending draft.
Never raises — draft writing is best-effort and must not break teardown.

Ensure the index exists (also after an all-green run):

    uv run python -m aiqa_framework.shared.reporting.ensure_bug_drafts_index
"""

from __future__ import annotations

import base64
import html
import json
import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

BUG_DRAFTS_DIR = Path("test-output/ai/bug-drafts")

_MIME_BY_SUFFIX = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg"}


@dataclass
class BugDraftInput:
    parent_story_key: str
    summary: str
    description: str
    spec_file: str
    test_title: str
    #: Command that reproduces the failure locally.
    repro_command: str
    #: Where screenshots / traces of the failed test land (hint for humans).
    output_dir: str
    #: Image files present at teardown time (embedded as base64).
    images: list[Path] = field(default_factory=list)
    #: Jira base URL to render the story link; empty -> plain text key.
    jira_base_url: str = ""


def _slugify(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:60]
    return slug or "failure"


def _image_data_uri(path: Path) -> str | None:
    try:
        mime = _MIME_BY_SUFFIX.get(path.suffix.lower())
        if not mime or not path.is_file():
            return None
        return f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode()}"
    except Exception as err:  # noqa: BLE001 — embedding is best-effort
        print(f'[bug-draft] could not embed image "{path}": {err}')
        return None


def _render_draft_html(draft: BugDraftInput, recorded_at: str) -> str:
    esc = html.escape
    embedded = [(p.name, uri) for p in draft.images if (uri := _image_data_uri(p))]
    evidence = (
        "\n".join(
            f'<figure><figcaption>{esc(name)}</figcaption><img src="{uri}" alt="{esc(name)}"></figure>'
            for name, uri in embedded
        )
        if embedded
        else (
            '<p class="muted">No screenshot was available at teardown time — open the test '
            f"output folder for screenshots / traces:<br><code>{esc(draft.output_dir)}</code></p>"
        )
    )
    base = draft.jira_base_url.rstrip("/")
    story_cell = (
        f'<a href="{esc(base)}/browse/{esc(draft.parent_story_key)}">{esc(draft.parent_story_key)}</a>'
        if base
        else esc(draft.parent_story_key)
    )
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Bug draft — {esc(draft.summary)}</title>
<style>
  body {{ font-family: -apple-system, Segoe UI, sans-serif; margin: 2rem auto; max-width: 900px; padding: 0 1rem; color: #172b4d; }}
  h1 {{ font-size: 1.3rem; }} h2 {{ font-size: 1.05rem; margin-top: 1.6rem; }}
  .banner {{ background: #fffae6; border: 1px solid #ffe380; border-radius: 6px; padding: .7rem 1rem; }}
  table {{ border-collapse: collapse; margin-top: .8rem; }} td {{ padding: .25rem .8rem .25rem 0; vertical-align: top; }}
  td:first-child {{ color: #6b778c; white-space: nowrap; }}
  pre {{ background: #f4f5f7; border-radius: 6px; padding: 1rem; overflow-x: auto; white-space: pre-wrap; }}
  code {{ background: #f4f5f7; padding: .1rem .3rem; border-radius: 4px; }}
  figure {{ margin: 1rem 0; }} img {{ max-width: 100%; border: 1px solid #dfe1e6; border-radius: 6px; }}
  figcaption {{ color: #6b778c; font-size: .85rem; margin-bottom: .3rem; }}
  .muted {{ color: #6b778c; }}
</style>
</head>
<body>
<p class="banner">📝 <strong>DRAFT — not filed to Jira.</strong> Review it; the qa-agent files the bug
(deduped, linked to the story) only after explicit approval.</p>
<h1>{esc(draft.summary)}</h1>
<table>
  <tr><td>Parent story</td><td>{story_cell}</td></tr>
  <tr><td>Spec file</td><td><code>{esc(draft.spec_file)}</code></td></tr>
  <tr><td>Test</td><td>{esc(draft.test_title)}</td></tr>
  <tr><td>Recorded</td><td>{esc(recorded_at)}</td></tr>
</table>
<h2>Steps to reproduce</h2>
<ol>
  <li>Check out the branch with the spec above.</li>
  <li>Run: <pre>{esc(draft.repro_command)}</pre></li>
  <li>The failing assertion and its context are below; screenshots / traces live in the test output folder.</li>
</ol>
<h2>Error</h2>
<pre>{esc(draft.description)}</pre>
<h2>Evidence</h2>
{evidence}
</body>
</html>
"""


def _regenerate_index() -> None:
    entries = []
    for f in sorted(BUG_DRAFTS_DIR.glob("*.json")):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            entries.append(
                {
                    "html": f.with_suffix(".html").name,
                    "summary": data.get("summary", f.name),
                    "story": data.get("parentStoryKey", ""),
                    "recordedAt": data.get("recordedAt", ""),
                }
            )
        except Exception as err:  # noqa: BLE001 — a bad draft must not break the index
            print(f"[bug-draft] unreadable draft {f.name} (skipped from index): {err}")

    esc = html.escape
    rows = (
        "\n".join(
            f'<li><a href="{e["html"]}">{esc(e["summary"])}</a> '
            f'<span class="muted">— {esc(e["story"])} · {esc(e["recordedAt"])}</span></li>'
            for e in entries
        )
        if entries
        else '<li class="muted">No pending drafts 🎉</li>'
    )
    (BUG_DRAFTS_DIR / "index.html").write_text(
        f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>Bug drafts — pending human approval</title>
<style>body{{font-family:-apple-system,Segoe UI,sans-serif;margin:2rem auto;max-width:800px;padding:0 1rem;color:#172b4d}}
.muted{{color:#6b778c}}li{{margin:.4rem 0}}</style></head>
<body><h1>📝 Bug drafts — pending human approval</h1>
<p class="muted">Written by the failure hook (conftest.py). Nothing here has been filed to Jira.</p>
<ul>
{rows}
</ul></body></html>
""",
        encoding="utf-8",
    )


def write_bug_draft(draft: BugDraftInput) -> str | None:
    """Write ``<slug>.json`` + ``<slug>.html`` and refresh the index.

    Returns the html path (str) or None on failure. Never raises.
    """
    try:
        BUG_DRAFTS_DIR.mkdir(parents=True, exist_ok=True)
        recorded_at = datetime.now(UTC).isoformat(timespec="seconds")
        slug = _slugify(draft.test_title)

        (BUG_DRAFTS_DIR / f"{slug}.json").write_text(
            json.dumps(
                {
                    "parentStoryKey": draft.parent_story_key,
                    "summary": draft.summary,
                    "description": draft.description,
                    "specFile": draft.spec_file,
                    "reproCommand": draft.repro_command,
                    "outputDir": draft.output_dir,
                    "evidenceImages": [p.name for p in draft.images],
                    "recordedAt": recorded_at,
                    "status": "draft-awaiting-human-approval",
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        html_path = BUG_DRAFTS_DIR / f"{slug}.html"
        html_path.write_text(_render_draft_html(draft, recorded_at), encoding="utf-8")
        _regenerate_index()
        return str(html_path)
    except Exception as err:  # noqa: BLE001 — must not break teardown
        print(f"[bug-draft] failed to write bug draft: {err}")
        return None


def ensure_bug_drafts_index() -> None:
    """Guarantee ``bug-drafts/index.html`` exists — even after an all-green run."""
    try:
        BUG_DRAFTS_DIR.mkdir(parents=True, exist_ok=True)
        _regenerate_index()
    except Exception as err:  # noqa: BLE001
        print(f"[bug-draft] failed to (re)generate the drafts index: {err}")
