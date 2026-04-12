from __future__ import annotations

import json

from fastapi import APIRouter
from fastapi.responses import HTMLResponse, RedirectResponse

from harbor.config import get_settings

router = APIRouter(tags=["operator_web"])


CHAT_INSTRUCTION_PRESETS = [
    {
        "key": "research-plan",
        "label": "Research plan",
        "value": (
            "Draft a compact next-step research plan with explicit unknowns and "
            "decision-relevant follow-ups."
        ),
    },
    {
        "key": "evidence-summary",
        "label": "Evidence summary",
        "value": (
            "Summarize only the grounded facts in the supplied Harbor context and "
            "state missing evidence briefly."
        ),
    },
    {
        "key": "decision-brief",
        "label": "Decision brief",
        "value": (
            "Return a concise operator decision brief with recommendation, "
            "rationale, and open questions."
        ),
    },
]


BASE_CSS = """
:root {
  color-scheme: light dark;
  font-family: Arial, Helvetica, sans-serif;
}
body {
  margin: 0;
  background: #0f172a;
  color: #e5e7eb;
}
a {
  color: #93c5fd;
}
code.inline,
code.page-code {
  font-family: Consolas, Monaco, monospace;
  font-size: 0.9rem;
}
.page {
  max-width: 1320px;
  margin: 0 auto;
  padding: 24px;
}
.page-header {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
  margin-bottom: 24px;
}
.page-header h1,
.section-card h2 {
  margin: 0 0 8px;
}
.page-subtitle {
  margin: 0;
  color: #cbd5e1;
}
.status {
  margin: 12px 0 0;
}
.status.info {
  color: #bfdbfe;
}
.status.success {
  color: #86efac;
}
.status.error {
  color: #fca5a5;
}
.grid {
  display: grid;
  gap: 16px;
}
.summary-grid {
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
}
.summary-card,
.section-card {
  background: #111827;
  border: 1px solid #334155;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 6px 18px rgba(15, 23, 42, 0.18);
}
.summary-label {
  color: #94a3b8;
  font-size: 0.9rem;
}
.summary-value {
  margin-top: 8px;
  font-size: 1.6rem;
  font-weight: 700;
}
.table-wrap {
  overflow-x: auto;
}
table {
  width: 100%;
  border-collapse: collapse;
}
th,
td {
  padding: 10px 12px;
  border-bottom: 1px solid #334155;
  text-align: left;
  vertical-align: top;
}
th {
  color: #cbd5e1;
  font-size: 0.9rem;
}
td {
  color: #e5e7eb;
}
.empty {
  color: #94a3b8;
}
.badge {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 999px;
  background: #1e293b;
  border: 1px solid #475569;
  font-size: 0.85rem;
}
.meta-list {
  display: grid;
  gap: 6px;
  margin: 0;
}
.meta-row {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
.meta-key {
  color: #94a3b8;
  min-width: 120px;
}
.actions {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}
.action-list {
  margin: 0;
  padding-left: 20px;
  color: #cbd5e1;
}
.action-button {
  border: 1px solid #3b82f6;
  border-radius: 8px;
  background: #1d4ed8;
  color: #eff6ff;
  padding: 6px 10px;
  font-size: 0.9rem;
  cursor: pointer;
}
.action-button:hover {
  background: #2563eb;
}
.action-button.secondary {
  background: #1e293b;
  border-color: #475569;
  color: #e5e7eb;
}
.action-button.secondary:hover {
  background: #334155;
}
.action-button[disabled] {
  opacity: 0.65;
  cursor: progress;
}
.action-note {
  margin: 0;
  color: #cbd5e1;
}
.form-grid {
  display: grid;
  gap: 16px;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
}
.form-panel {
  display: grid;
  gap: 12px;
}
.form-panel h3 {
  margin: 0;
}
.form-field {
  display: grid;
  gap: 6px;
}
.form-label {
  color: #cbd5e1;
  font-size: 0.9rem;
}
.form-field input,
.form-field select,
.form-field textarea {
  width: 100%;
  box-sizing: border-box;
  padding: 10px 12px;
  border-radius: 8px;
  border: 1px solid #475569;
  background: #0f172a;
  color: #e5e7eb;
}
.form-field textarea {
  min-height: 88px;
  resize: vertical;
}
.form-field input:disabled,
.form-field select:disabled,
.form-field textarea:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}
.form-actions {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}
.form-hint {
  color: #94a3b8;
  font-size: 0.85rem;
}
.response-grid {
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  margin-top: 16px;
}
.response-card {
  background: #0f172a;
  border: 1px solid #334155;
  border-radius: 12px;
  padding: 14px;
}
.response-label {
  color: #94a3b8;
  font-size: 0.85rem;
}
.response-value {
  margin-top: 8px;
  font-size: 1rem;
  font-weight: 600;
  word-break: break-word;
}
.response-pre {
  margin: 0;
  padding: 12px;
  border-radius: 8px;
  border: 1px solid #334155;
  background: #0f172a;
  color: #e5e7eb;
  white-space: pre-wrap;
  word-break: break-word;
}
.chat-history {
  display: grid;
  gap: 12px;
}
.chat-history-note {
  margin: 0 0 12px;
  color: #94a3b8;
}
.chat-turn-block {
  display: grid;
  gap: 12px;
  border: 1px solid #334155;
  border-radius: 12px;
  padding: 12px;
  background: #0b1220;
}
.chat-turn-block-header {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}
.chat-turn-block-title {
  font-weight: 700;
  color: #e5e7eb;
}
.chat-turn-block-meta {
  color: #94a3b8;
  font-size: 0.85rem;
}
.chat-turn-block-body {
  display: grid;
  gap: 10px;
}
.chat-message {
  border: 1px solid #334155;
  border-radius: 12px;
  padding: 12px;
  background: #0f172a;
}
.chat-message.user {
  border-color: #2563eb;
}
.chat-message.assistant {
  border-color: #10b981;
}
.chat-message.error {
  border-color: #ef4444;
}
.chat-message-header {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
  margin-bottom: 10px;
}
.chat-role {
  font-weight: 700;
}
.chat-meta {
  color: #94a3b8;
  font-size: 0.85rem;
}
.chat-message-text {
  margin: 0;
}
.chat-message-body {
  display: grid;
  gap: 8px;
}
.chat-message-preview {
  margin: 0;
  color: #94a3b8;
  font-size: 0.85rem;
}
.chat-collapsible {
  border: 1px solid #334155;
  border-radius: 10px;
  background: #111827;
}
.chat-collapsible > summary {
  cursor: pointer;
  list-style: none;
  padding: 10px 12px;
  color: #cbd5e1;
}
.chat-collapsible > summary::-webkit-details-marker {
  display: none;
}
.chat-collapsible-summary {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}
.chat-collapsible-label {
  color: #e5e7eb;
  font-weight: 600;
}
.chat-collapsible-preview {
  color: #94a3b8;
  font-size: 0.85rem;
}
.chat-collapsible-body {
  padding: 0 12px 12px;
}
.chat-turn-selector {
  max-width: 360px;
}
.chat-turn-summary {
  margin-top: 0;
}
.chat-turn-compare-grid {
  margin-top: 0;
}
.chat-turn-compare-note {
  margin: 0;
  color: #94a3b8;
  font-size: 0.9rem;
}
.chat-turn-compare-row {
  display: grid;
  gap: 8px;
}
.chat-inspector {
  display: grid;
  gap: 12px;
}
.chat-turn-detail {
  display: grid;
  gap: 8px;
}
.chat-source-attribution-badge {
  margin-top: 6px;
  padding: 4px 8px;
  font-size: 0.8rem;
  color: #94a3b8;
  border-left: 2px solid #334155;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.citation-ref {
  display: inline;
  padding: 1px 4px;
  font-size: 0.8em;
  font-weight: 600;
  color: #60a5fa;
  background: #1e293b;
  border-radius: 3px;
  cursor: default;
}
.citation-ref:hover {
  background: #334155;
  color: #93c5fd;
}
.chat-source-attribution-list {
  display: grid;
  gap: 10px;
}
.chat-source-attribution-item {
  padding: 8px 10px;
  border: 1px solid #1e293b;
  border-radius: 6px;
  background: #0f172a;
}
.chat-source-attribution-title {
  font-weight: 600;
  color: #e5e7eb;
}
.chat-source-attribution-url {
  font-size: 0.85rem;
  color: #60a5fa;
  word-break: break-all;
}
.chat-source-attribution-note {
  margin-top: 4px;
  font-size: 0.85rem;
  color: #94a3b8;
}
.propose-source-form {
  display: grid;
  gap: 8px;
}
.propose-source-form input {
  width: 100%;
  box-sizing: border-box;
}
.propose-source-result {
  margin-top: 8px;
  padding: 6px 10px;
  font-size: 0.85rem;
  border-radius: 4px;
}
.propose-source-result.success {
  background: #064e3b;
  color: #6ee7b7;
}
.propose-source-result.error {
  background: #7f1d1d;
  color: #fca5a5;
}
.draft-handbook-result {
  margin-top: 8px;
  padding: 6px 10px;
  font-size: 0.85rem;
  border-radius: 4px;
}
.draft-handbook-result.success {
  background: #064e3b;
  color: #6ee7b7;
}
.draft-handbook-result.error {
  background: #7f1d1d;
  color: #fca5a5;
}
.chat-session-summary {
  margin-top: 0;
}
.chat-session-meta {
  display: grid;
  gap: 8px;
}
.chat-session-meta-row {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
"""





def _bootstrap_payload(page: str, project_id: str | None = None) -> str:
    settings = get_settings()
    payload: dict[str, str] = {
        "page": page,
        "apiBase": settings.api_v1_prefix,
    }
    if project_id is not None:
        payload["projectId"] = project_id
    return json.dumps(payload).replace("</", "<\\/")


def _render_document(*, title: str, body: str, bootstrap_json: str) -> HTMLResponse:
    html = f"""
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{title}</title>
    <style>{BASE_CSS}</style>
  </head>
  <body>
    {body}
    <script id="harbor-operator-bootstrap" type="application/json">
      {bootstrap_json}
    </script>
    <script src="/static/operator.js" defer></script>
  </body>
</html>
"""
    return HTMLResponse(content=html)


def _render_chat_document(*, title: str, body: str, bootstrap_json: str) -> HTMLResponse:
    html = f"""
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{title}</title>
    <style>{BASE_CSS}</style>
  </head>
  <body>
    {body}
    <script id="harbor-chat-bootstrap" type="application/json">
      {bootstrap_json}
    </script>
    <script src="/static/chat.js" defer></script>
  </body>
</html>
"""
    return HTMLResponse(content=html)


def _projects_page() -> HTMLResponse:
    body = """
<div class="page" id="operator-shell" data-operator-shell="projects">
  <header class="page-header">
    <div>
      <h1>Harbor Operator Web Shell</h1>
      <p class="page-subtitle">
        Project list for the manual operator workflow baseline.
      </p>
      <p class="status info" id="projects-status">Waiting to load projects.</p>
    </div>
    <div class="actions">
      <button
        type="button"
        class="action-button secondary"
        id="projects-reload-button"
        data-action="reload-projects"
      >
        Reload projects
      </button>
      <a href="/chat">Chat</a>
      <a href="/healthz">Health</a>
      <a href="/runtime">Runtime</a>
    </div>
  </header>

  <section class="section-card">
    <h2>Create Project</h2>
    <p class="action-note">
      Create a new Harbor project and continue directly in the operator shell.
    </p>
    <form id="create-project-form" data-create-form="create-project">
      <div class="form-grid">
        <div class="form-panel">
          <div class="form-field">
            <label class="form-label" for="create-project-title">Title</label>
            <input id="create-project-title" name="title" type="text" required />
          </div>
          <div class="form-field">
            <label class="form-label" for="create-project-short-description">
              Short description
            </label>
            <textarea
              id="create-project-short-description"
              name="short_description"
            ></textarea>
          </div>
          <div class="form-actions">
            <button type="submit" class="action-button">Create project</button>
            <span class="form-hint">Defaults: status draft, type standard.</span>
          </div>
        </div>
      </div>
      <p
        class="status info"
        id="projects-create-status"
        data-create-status="projects-create"
      >
        No create action executed yet.
      </p>
    </form>
  </section>

  <section class="section-card">
    <h2>Projects</h2>
    <p>
      Open a project to inspect workflow summary, runs, candidates,
      review queue, and project sources.
    </p>
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Title</th>
            <th>Status</th>
            <th>Type</th>
            <th>Blueprint</th>
            <th>Updated</th>
            <th>Description</th>
          </tr>
        </thead>
        <tbody id="projects-table-body">
          <tr>
            <td colspan="6" class="empty">Loading...</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</div>
"""
    return _render_document(
        title="Harbor Operator Web Shell",
        body=body,
        bootstrap_json=_bootstrap_payload("projects"),
    )


def _project_detail_page(project_id: str) -> HTMLResponse:
    body = f"""
<div class="page" id="operator-shell" data-operator-shell="project-detail">
  <header class="page-header">
    <div>
      <h1 id="project-title">Project Detail</h1>
      <p class="page-subtitle">
        Read-heavy operator surface with targeted workflow actions.
      </p>
      <p class="status info" id="detail-status">Waiting to load project detail.</p>
    </div>
    <div class="actions">
      <button
        type="button"
        class="action-button secondary"
        id="project-detail-reload-button"
        data-action="reload-project-detail"
      >
        Reload detail
      </button>
      <a href="/operator/projects">Back to projects</a>
      <span>
        Requested project:
        <code class="page-code" id="project-id-value">{project_id}</code>
      </span>
    </div>
  </header>

  <section class="section-card">
    <h2>Project</h2>
    <div id="project-meta" class="meta-list">
      <div class="empty">Loading project metadata...</div>
    </div>
  </section>

  <section class="section-card">
    <h2>Workflow Summary</h2>
    <div
      class="grid summary-grid"
      id="workflow-summary-grid"
      data-summary-mount="workflow-summary"
    >
      <div class="empty">Loading workflow summary...</div>
    </div>
  </section>

  <section class="section-card">
    <h2>Operator Actions</h2>
    <p class="action-note">
      Actions stay thin and call the existing Harbor APIs only.
    </p>
    <ul class="action-list">
      <li data-operator-action="promote-to-review">
        Candidate -&gt; Review Queue
      </li>
      <li data-operator-action="promote-to-source">
        Review Queue -&gt; Source / ProjectSource
      </li>
    </ul>
    <p class="status info" id="action-status" data-action-status="operator-actions">
      No action executed yet.
    </p>
  </section>

  <section class="section-card">
    <h2>OpenAI Dry Run</h2>
    <p class="action-note">
      Send an explicit operator request through the Harbor OpenAI adapter and
      optionally persist the result in Harbor history.
    </p>
    <form
      class="form-panel"
      id="openai-project-dry-run-form"
      data-openai-form="project-dry-run"
    >
      <div class="form-field">
        <label class="form-label" for="openai-dry-run-input-text">
          Operator request
        </label>
        <textarea
          id="openai-dry-run-input-text"
          name="input_text"
          required
        ></textarea>
      </div>
      <div class="form-field">
        <label class="form-label" for="openai-dry-run-instructions">
          Instructions (optional)
        </label>
        <textarea
          id="openai-dry-run-instructions"
          name="instructions"
        ></textarea>
      </div>
      <div class="form-field">
        <label class="form-label" for="openai-dry-run-persist">
          <input
            id="openai-dry-run-persist"
            name="persist"
            type="checkbox"
            checked
          />
          Persist this dry run in Harbor history
        </label>
      </div>
      <div class="form-actions">
        <button
          type="submit"
          class="action-button"
          id="openai-dry-run-submit"
        >
          Run dry-run
        </button>
        <span class="form-hint">
          Uses current project context plus your explicit request.
        </span>
      </div>
    </form>
    <p
      class="status info"
      id="openai-dry-run-status"
      data-openai-status="project-dry-run"
    >
      No dry run executed yet.
    </p>
    <div
      class="grid response-grid"
      data-openai-response="project-dry-run"
    >
      <div class="response-card">
        <div class="response-label">Provider</div>
        <div class="response-value" id="openai-dry-run-provider">&mdash;</div>
      </div>
      <div class="response-card">
        <div class="response-label">Model</div>
        <div class="response-value" id="openai-dry-run-model">&mdash;</div>
      </div>
      <div class="response-card">
        <div class="response-label">Status</div>
        <div class="response-value" id="openai-dry-run-response-status">
          &mdash;
        </div>
      </div>
      <div class="response-card">
        <div class="response-label">Response ID</div>
        <div class="response-value" id="openai-dry-run-response-id">
          &mdash;
        </div>
      </div>
    </div>
    <div class="form-panel">
      <h3>Response Text</h3>
      <pre
        class="response-pre"
        id="openai-dry-run-output-text"
      >&mdash;</pre>
    </div>
    <div class="table-wrap" data-openai-history="project-dry-run">
      <table>
        <thead>
          <tr>
            <th>Created</th>
            <th>Status</th>
            <th>Model</th>
            <th>Response ID</th>
            <th>Request</th>
            <th>Response</th>
          </tr>
        </thead>
        <tbody id="openai-dry-run-history-body">
          <tr>
            <td colspan="6" class="empty">Loading...</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>

  <section class="section-card">
    <h2>Manual Create Actions</h2>
    <p class="action-note">
      Create the next workflow objects directly from the operator shell.
    </p>
    <div class="form-grid">
      <form
        class="form-panel"
        id="create-search-campaign-form"
        data-create-form="create-search-campaign"
      >
        <h3>Create Search Campaign</h3>
        <div class="form-field">
          <label class="form-label" for="create-search-campaign-title">
            Title
          </label>
          <input
            id="create-search-campaign-title"
            name="title"
            type="text"
            required
          />
        </div>
        <div class="form-field">
          <label class="form-label" for="create-search-campaign-query-text">
            Query text
          </label>
          <textarea
            id="create-search-campaign-query-text"
            name="query_text"
          ></textarea>
        </div>
        <div class="form-field">
          <label class="form-label" for="create-search-campaign-note">Note</label>
          <input id="create-search-campaign-note" name="note" type="text" />
        </div>
        <div class="form-actions">
          <button type="submit" class="action-button">Create campaign</button>
          <span class="form-hint">Defaults: manual, planned.</span>
        </div>
      </form>

      <form
        class="form-panel"
        id="create-search-run-form"
        data-create-form="create-search-run"
      >
        <h3>Create Search Run</h3>
        <div class="form-field">
          <label class="form-label" for="create-run-campaign-id">Campaign</label>
          <select
            id="create-run-campaign-id"
            name="search_campaign_id"
            data-create-target="campaign-select"
            required
            disabled
          >
            <option value="">Loading campaigns...</option>
          </select>
        </div>
        <div class="form-field">
          <label class="form-label" for="create-search-run-title">Title</label>
          <input id="create-search-run-title" name="title" type="text" required />
        </div>
        <div class="form-field">
          <label class="form-label" for="create-search-run-query-snapshot">
            Query snapshot
          </label>
          <textarea
            id="create-search-run-query-snapshot"
            name="query_text_snapshot"
          ></textarea>
        </div>
        <div class="form-field">
          <label class="form-label" for="create-search-run-note">Note</label>
          <input id="create-search-run-note" name="note" type="text" />
        </div>
        <div class="form-actions">
          <button
            type="submit"
            class="action-button"
            id="create-run-submit"
            disabled
          >
            Create run
          </button>
          <span class="form-hint" id="create-run-hint">Loading campaigns...</span>
        </div>
      </form>

      <form
        class="form-panel"
        id="create-result-candidate-form"
        data-create-form="create-result-candidate"
      >
        <h3>Create Result Candidate</h3>
        <div class="form-field">
          <label class="form-label" for="create-candidate-run-id">Run</label>
          <select
            id="create-candidate-run-id"
            name="search_run_id"
            data-create-target="run-select"
            required
            disabled
          >
            <option value="">Loading runs...</option>
          </select>
        </div>
        <div class="form-field">
          <label class="form-label" for="create-candidate-title">Title</label>
          <input id="create-candidate-title" name="title" type="text" required />
        </div>
        <div class="form-field">
          <label class="form-label" for="create-candidate-url">URL</label>
          <input id="create-candidate-url" name="url" type="url" required />
        </div>
        <div class="form-field">
          <label class="form-label" for="create-candidate-domain">Domain</label>
          <input id="create-candidate-domain" name="domain" type="text" />
        </div>
        <div class="form-field">
          <label class="form-label" for="create-candidate-rank">Rank</label>
          <input id="create-candidate-rank" name="rank" type="number" min="1" />
        </div>
        <div class="form-field">
          <label class="form-label" for="create-candidate-snippet">Snippet</label>
          <textarea id="create-candidate-snippet" name="snippet"></textarea>
        </div>
        <div class="form-field">
          <label class="form-label" for="create-candidate-note">Note</label>
          <input id="create-candidate-note" name="note" type="text" />
        </div>
        <div class="form-actions">
          <button
            type="submit"
            class="action-button"
            id="create-candidate-submit"
            disabled
          >
            Create candidate
          </button>
          <span class="form-hint" id="create-candidate-hint">Loading runs...</span>
        </div>
      </form>
    </div>
    <p class="status info" id="create-status" data-create-status="project-create-actions">
      No create action executed yet.
    </p>
  </section>

  <section class="section-card">
    <h2>Search Campaigns</h2>
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Title</th>
            <th>Status</th>
            <th>Kind</th>
            <th>Query</th>
            <th>Updated</th>
            <th>Note</th>
          </tr>
        </thead>
        <tbody id="campaigns-table-body">
          <tr>
            <td colspan="6" class="empty">Loading...</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>

  <section class="section-card">
    <h2>Runs</h2>
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Title</th>
            <th>Status</th>
            <th>Kind</th>
            <th>Query snapshot</th>
            <th>Updated</th>
            <th>Note</th>
          </tr>
        </thead>
        <tbody id="runs-table-body">
          <tr>
            <td colspan="6" class="empty">Loading...</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>

  <section class="section-card">
    <h2>Result Candidates</h2>
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Title</th>
            <th>Disposition</th>
            <th>Domain</th>
            <th>Rank</th>
            <th>Updated</th>
            <th>Snippet</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody id="candidates-table-body">
          <tr>
            <td colspan="7" class="empty">Loading...</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>

  <section class="section-card">
    <h2>Review Queue</h2>
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Title</th>
            <th>Status</th>
            <th>Priority</th>
            <th>Kind</th>
            <th>Candidate ID</th>
            <th>Updated</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody id="review-queue-table-body">
          <tr>
            <td colspan="7" class="empty">Loading...</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>

  <section class="section-card">
    <h2>Project Sources</h2>
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Title</th>
            <th>Review</th>
            <th>Relevance</th>
            <th>Trust tier</th>
            <th>Project source ID</th>
            <th>Canonical URL</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody id="project-sources-table-body" data-source-review-actions="true">
          <tr>
            <td colspan="7" class="empty">Loading...</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>

  <section class="section-card" data-handbook-versions="project-detail">
    <h2>Handbook Versions</h2>
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Version</th>
            <th>Created</th>
            <th>Change note</th>
            <th>Handbook markdown</th>
          </tr>
        </thead>
        <tbody id="handbook-versions-table-body">
          <tr>
            <td colspan="4" class="empty">Loading...</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>

  <section class="section-card">
    <h2>Candidate Lineage</h2>
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Candidate</th>
            <th>Disposition</th>
            <th>Review status</th>
            <th>Project source review</th>
            <th>Review item ID</th>
            <th>Project source ID</th>
          </tr>
        </thead>
        <tbody id="lineage-table-body">
          <tr>
            <td colspan="6" class="empty">Loading...</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</div>
"""
    return _render_document(
        title=f"Harbor Operator Project {project_id}",
        body=body,
        bootstrap_json=_bootstrap_payload("project-detail", project_id=project_id),
    )


def _chat_page() -> HTMLResponse:
    body = """
<div class="page" id="chat-shell" data-chat-shell="chat">
  <header class="page-header">
    <div>
      <h1>Harbor Chat Surface</h1>
      <p class="page-subtitle">
        Thin chat-style surface over the Harbor OpenAI adapter with persisted
        session history.
      </p>
      <p class="status info" id="chat-status">Loading Harbor projects.</p>
    </div>
    <div class="actions">
      <button
        type="button"
        class="action-button secondary"
        id="chat-reload-projects-button"
        data-chat-action="reload-projects"
      >
        Reload projects
      </button>
      <a href="/operator/projects">Operator</a>
      <a href="/healthz">Health</a>
      <a href="/runtime">Runtime</a>
    </div>
  </header>

  <section class="section-card">
    <h2>Composer</h2>
    <p class="action-note">
      Select a Harbor project, continue a persisted chat session or start a new
      one, then send a message through the Harbor OpenAI adapter.
    </p>
    <form
      class="form-panel"
      id="chat-message-form"
      data-chat-form="persisted-chat"
    >
      <div class="form-field">
        <label class="form-label" for="chat-project-id">Project</label>
        <select id="chat-project-id" name="project_id" required disabled>
          <option value="">Loading projects...</option>
        </select>
      </div>
      <div class="form-field">
        <label class="form-label" for="chat-session-id">Session</label>
        <select
          id="chat-session-id"
          name="chat_session_id"
          data-chat-session-select="persisted"
          disabled
        >
          <option value="">Start new session</option>
        </select>
      </div>
      <div class="form-actions">
        <button
          type="button"
          class="action-button secondary"
          id="chat-new-session-button"
          data-chat-action="new-session"
          disabled
        >
          New session
        </button>
        <span class="form-hint">
          Sessions and turns are persisted in Harbor.
        </span>
      </div>
      <div class="form-grid">
        <div class="form-panel" data-chat-composer-panel="message">
          <h3>Message</h3>
          <div class="form-field">
            <label class="form-label" for="chat-input-text">Operator message</label>
            <textarea
              id="chat-input-text"
              name="input_text"
              required
              disabled
              placeholder="Ask Harbor for a compact project-specific response."
            ></textarea>
          </div>
          <div class="form-hint">
            The message is persisted as the operator input for the new chat turn.
          </div>
        </div>
        <div class="form-panel" data-chat-composer-panel="instructions">
          <h3>Instructions</h3>
          <div class="form-field">
            <label class="form-label" for="chat-instructions-preset">
              Preset
            </label>
            <select
              id="chat-instructions-preset"
              name="instructions_preset"
              data-chat-instructions-preset="persisted-chat"
              disabled
            >
              <option value="__default__">Harbor default instructions</option>
            </select>
          </div>
          <div class="form-actions">
            <button
              type="button"
              class="action-button secondary"
              id="chat-apply-instructions-preset-button"
              data-chat-action="apply-instructions-preset"
              disabled
            >
              Apply preset
            </button>
            <span class="form-hint" id="chat-instructions-preset-state">
              Preset: Harbor default instructions.
            </span>
          </div>
          <div
            class="chat-turn-detail"
            data-chat-default-instructions="persisted-chat"
          >
            <div class="response-label">Harbor default instructions</div>
            <pre class="response-pre" id="chat-default-instructions-text"></pre>
          </div>
          <div class="form-field">
            <label class="form-label" for="chat-instructions-text">
              Optional instructions override
            </label>
            <textarea
              id="chat-instructions-text"
              name="instructions"
              data-chat-instructions-field="persisted-chat"
              disabled
              placeholder="Optional. Leave blank to use Harbor's default chat instructions."
            ></textarea>
          </div>
          <div class="form-actions">
            <button
              type="button"
              class="action-button secondary"
              id="chat-clear-instructions-button"
              data-chat-action="clear-instructions"
              disabled
            >
              Use default instructions
            </button>
            <span class="form-hint" id="chat-instructions-state">
              Using Harbor default instructions.
            </span>
          </div>
          <div class="form-hint">
            Presets and custom instructions are transient and apply to the
            next sent or retried turn.
          </div>
        </div>
      </div>
      <div class="form-actions">
        <button
          type="submit"
          class="action-button"
          id="chat-send-button"
          disabled
        >
          Send message
        </button>
        <button
          type="button"
          class="action-button secondary"
          id="chat-retry-last-failed-button"
          data-chat-action="retry-last-failed"
          disabled
        >
          Retry last failed message
        </button>
        <span class="form-hint" id="chat-retry-hint">
          No failed message awaiting retry.
        </span>
      </div>
    </form>
    <div
      id="chat-retry-panel"
      class="chat-inspector"
      data-chat-retry-panel="persisted-chat"
    >
      <div class="empty">No failed message awaiting retry.</div>
    </div>
  </section>

  <section class="section-card">
    <h2>Selected Session</h2>
    <p class="action-note">
      Inspect the current persisted session state or the new-session state before
      sending the next message.
    </p>
    <div
      class="response-grid chat-session-summary"
      id="chat-session-summary"
      data-chat-session-summary="persisted-chat"
    >
      <div class="response-card">
        <div class="response-label">Session</div>
        <div class="response-value">New session</div>
      </div>
    </div>
    <div
      id="chat-session-meta"
      class="chat-session-meta"
      data-chat-session-meta="persisted-chat"
    >
      <div class="empty">New session not yet persisted.</div>
    </div>
  </section>

  <section class="section-card">
    <details class="chat-collapsible">
      <summary>
        <span class="chat-collapsible-summary">
          <span class="chat-collapsible-label">Propose Source</span>
          <span class="chat-collapsible-preview">Submit a URL to propose as project source</span>
        </span>
      </summary>
      <div class="chat-collapsible-body">
        <form id="propose-source-form" class="propose-source-form">
          <div class="form-field">
            <label class="form-label" for="propose-source-url">URL (required)</label>
            <input type="url" id="propose-source-url" class="form-input"
              placeholder="https://example.com/article" required maxlength="1000" />
          </div>
          <div class="form-field">
            <label class="form-label" for="propose-source-title">Title (optional)</label>
            <input type="text" id="propose-source-title" class="form-input"
              placeholder="Source title" maxlength="300" />
          </div>
          <div class="form-field">
            <label class="form-label" for="propose-source-note">Note (optional)</label>
            <input type="text" id="propose-source-note" class="form-input"
              placeholder="Why this source is relevant" maxlength="1000" />
          </div>
          <button type="submit" class="button button-sm">Propose source</button>
        </form>
        <div id="propose-source-result"></div>
      </div>
    </details>
  </section>

  <section class="section-card">
    <h2>Persisted Session History</h2>
    <p class="chat-history-note" data-chat-history-density="compact">
      Long operator and assistant turns render in compact cards and collapse
      automatically when they become dense.
    </p>
    <div id="chat-history" class="chat-history" data-chat-history="persisted-chat">
      <div class="empty">No persisted turns yet.</div>
    </div>
  </section>

  <section class="section-card" data-chat-turn-density="compact">
    <h2>Selected Turn Context</h2>
    <p class="action-note" data-chat-collapsible-support="chat-content">
      Inspect the exact Harbor-rendered input and persisted output for a selected
      turn. Longer fields collapse automatically for readability.
    </p>
    <div class="form-field chat-turn-selector">
      <label class="form-label" for="chat-turn-id">Persisted turn</label>
      <select
        id="chat-turn-id"
        name="chat_turn_id"
        data-chat-turn-select="persisted"
        disabled
      >
        <option value="">No persisted turns</option>
      </select>
    </div>
    <div
      class="response-grid chat-turn-summary"
      id="chat-turn-summary"
      data-chat-turn-summary="persisted-chat"
    >
      <div class="response-card">
        <div class="response-label">Selected turn</div>
        <div class="response-value">&mdash;</div>
      </div>
    </div>
    <p class="chat-turn-compare-note" data-chat-turn-compare-note="selected-turn">
      Compare the persisted operator input, the Harbor-rendered input, and the
      persisted assistant output with compact metrics before opening dense text
      blocks.
    </p>
    <div
      class="response-grid chat-turn-compare-grid"
      id="chat-turn-compare-grid"
      data-chat-turn-compare="persisted-chat"
    >
      <div class="response-card">
        <div class="response-label">Comparison</div>
        <div class="response-value">&mdash;</div>
      </div>
    </div>
    <div
      id="chat-turn-inspector"
      class="chat-inspector"
      data-chat-turn-inspector="persisted-chat"
    >
      <div class="empty">No persisted turn selected.</div>
    </div>
  </section>
</div>
"""
    return _render_chat_document(
        title="Harbor Chat Surface",
        body=body,
        bootstrap_json=_bootstrap_payload("chat"),
    )


@router.get("/chat", include_in_schema=False)
def chat_page() -> HTMLResponse:
    return _chat_page()


@router.get("/operator", include_in_schema=False)
def operator_root() -> RedirectResponse:
    return RedirectResponse(url="/operator/projects", status_code=307)


@router.get("/operator/projects", include_in_schema=False)
def operator_projects_page() -> HTMLResponse:
    return _projects_page()


@router.get("/operator/projects/{project_id}", include_in_schema=False)
def operator_project_detail_page(project_id: str) -> HTMLResponse:
    return _project_detail_page(project_id)
