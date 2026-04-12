from __future__ import annotations

import json

from fastapi import APIRouter
from fastapi.responses import HTMLResponse, RedirectResponse

from harbor.config import get_settings
from harbor.scheduler import all_known_task_kinds

SCHEDULER_DEFAULT_INTERVAL_SECONDS = 3600

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
    <link rel="stylesheet" href="/static/operator.css" />
  </head>
  <body>
    {body}
    <ol id="harbor-toasts" class="harbor-toasts" aria-live="polite" aria-atomic="false"></ol>
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
    <link rel="stylesheet" href="/static/operator.css" />
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
      <a href="/operator/pending-actions">Pending actions</a>
      <a href="/operator/scheduler">Scheduler</a>
      <a href="/chat">Chat</a>
      <a href="/healthz">Health</a>
      <a href="/runtime">Runtime</a>
    </div>
  </header>

  <section class="section-card" data-section-key="create-project">
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
    </form>
  </section>

  <section class="section-card" data-section-key="projects-list">
    <h2>Projects</h2>
    <p>
      Open a project to inspect workflow summary, runs, candidates,
      review queue, and project sources.
    </p>
    <div class="table-wrap">
      <table class="sortable" id="projects-table">
        <thead>
          <tr>
            <th data-sort-type="text">Title</th>
            <th data-sort-type="text">Status</th>
            <th data-sort-type="text">Type</th>
            <th data-sort-type="text">Blueprint</th>
            <th data-sort-type="date">Updated</th>
            <th data-sort-type="text">Description</th>
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

  <section class="section-card" data-section-key="project-meta">
    <h2>Project</h2>
    <div id="project-meta" class="meta-list">
      <div class="empty">Loading project metadata...</div>
    </div>
  </section>

  <section class="section-card" data-section-key="workflow-summary">
    <h2>Workflow Summary</h2>
    <div
      class="grid summary-grid"
      id="workflow-summary-grid"
      data-summary-mount="workflow-summary"
    >
      <div class="empty">Loading workflow summary...</div>
    </div>
  </section>

  <section class="section-card" data-section-key="operator-actions">
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
  </section>

  <section
    class="section-card"
    data-section-key="automation-tasks"
    data-automation-tasks="project-detail"
  >
    <h2>Automation Tasks</h2>
    <p class="action-note">
      Recent automation-triggered work for this project. Rows reflect the
      state machine: pending &rarr; running &rarr; succeeded / failed.
    </p>
    <div class="filter-bar" data-automation-tasks-filters>
      <label class="filter-label" for="automation-tasks-filter-kind">
        Kind
        <select
          id="automation-tasks-filter-kind"
          data-automation-tasks-filter="kind"
        >
          <option value="">All kinds</option>
        </select>
      </label>
      <label class="filter-label" for="automation-tasks-filter-status">
        Status
        <select
          id="automation-tasks-filter-status"
          data-automation-tasks-filter="status"
        >
          <option value="">All statuses</option>
          <option value="pending">pending</option>
          <option value="running">running</option>
          <option value="succeeded">succeeded</option>
          <option value="failed">failed</option>
        </select>
      </label>
      <span class="filter-summary" id="automation-tasks-filter-summary"
            data-automation-tasks-filter-summary>
        &mdash;
      </span>
    </div>
    <div class="table-wrap">
      <table class="sortable" id="automation-tasks-table">
        <thead>
          <tr>
            <th data-sort-type="text">Kind</th>
            <th data-sort-type="text">Trigger</th>
            <th data-sort-type="text">Status</th>
            <th data-sort-type="date">Started</th>
            <th data-sort-type="date">Completed</th>
            <th data-sort-disable="1">Result / Error</th>
          </tr>
        </thead>
        <tbody id="automation-tasks-table-body">
          <tr>
            <td colspan="6" class="empty">Loading...</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>

  <section class="section-card" data-section-key="openai-dry-run">
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

  <section class="section-card" data-section-key="manual-create">
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
  </section>

  <section class="section-card" data-section-key="campaigns">
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

  <section class="section-card" data-section-key="runs">
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

  <section class="section-card" data-section-key="candidates">
    <h2>Result Candidates</h2>
    <div class="table-wrap">
      <table class="sortable" id="candidates-table">
        <thead>
          <tr>
            <th data-sort-type="text">Title</th>
            <th data-sort-type="text">Disposition</th>
            <th data-sort-type="text">Domain</th>
            <th data-sort-type="number">Rank</th>
            <th data-sort-type="date">Updated</th>
            <th data-sort-disable="1">Snippet</th>
            <th data-sort-disable="1">Action</th>
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

  <section class="section-card" data-section-key="review-queue">
    <h2>Review Queue</h2>
    <div class="table-wrap">
      <table class="sortable" id="review-queue-table">
        <thead>
          <tr>
            <th data-sort-type="text">Title</th>
            <th data-sort-type="text">Status</th>
            <th data-sort-type="text">Priority</th>
            <th data-sort-type="text">Kind</th>
            <th data-sort-type="text">Candidate ID</th>
            <th data-sort-type="date">Updated</th>
            <th data-sort-disable="1">Action</th>
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

  <section class="section-card" data-section-key="project-sources">
    <h2>Project Sources</h2>
    <div class="table-wrap">
      <table class="sortable" id="project-sources-table">
        <thead>
          <tr>
            <th data-sort-type="text">Title</th>
            <th data-sort-type="text">Review</th>
            <th data-sort-type="text">Relevance</th>
            <th data-sort-type="text">Trust tier</th>
            <th data-sort-type="text">Project source ID</th>
            <th data-sort-type="text">Canonical URL</th>
            <th data-sort-disable="1">Latest snapshot</th>
            <th data-sort-disable="1">Actions</th>
          </tr>
        </thead>
        <tbody id="project-sources-table-body" data-source-review-actions="true">
          <tr>
            <td colspan="8" class="empty">Loading...</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>

  <section
    class="section-card"
    data-handbook-versions="project-detail"
    data-section-key="handbook-versions"
  >
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

  <section class="section-card" data-section-key="candidate-lineage">
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


def _overview_page() -> HTMLResponse:
    body = """
<div class="page" id="operator-shell" data-operator-shell="overview">
  <header class="page-header">
    <div>
      <h1>Operator Overview</h1>
      <p class="page-subtitle">
        Cross-project health snapshot: totals, recent automation tasks,
        and a per-project drill-down.
      </p>
    </div>
    <div class="actions">
      <a href="/operator/projects">Projects</a>
      <a href="/operator/pending-actions">Pending actions</a>
      <a href="/operator/scheduler">Scheduler</a>
      <button
        type="button"
        class="action-button secondary"
        id="overview-reload-button"
        data-action="reload-overview"
      >
        Reload
      </button>
    </div>
  </header>

  <section class="section-card" data-section-key="overview-totals">
    <h2>Totals</h2>
    <div id="overview-totals-grid" class="overview-totals-grid">
      <span class="empty">Loading...</span>
    </div>
  </section>

  <section class="section-card" data-section-key="overview-projects">
    <h2>Projects (latest 20 by update time)</h2>
    <div class="table-wrap">
      <table class="sortable" id="overview-projects-table">
        <thead>
          <tr>
            <th data-sort-type="text">Title</th>
            <th data-sort-type="date">Updated</th>
            <th data-sort-type="number">Sources</th>
            <th data-sort-type="number">Open review</th>
            <th data-sort-type="number">Latest handbook</th>
            <th data-sort-type="number">Stale snapshots</th>
            <th data-sort-type="number">Fetch errors</th>
          </tr>
        </thead>
        <tbody id="overview-projects-table-body">
          <tr>
            <td colspan="7" class="empty">Loading...</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>

  <section class="section-card" data-section-key="overview-tasks">
    <h2>Recent automation tasks</h2>
    <div class="table-wrap">
      <table class="sortable" id="overview-tasks-table">
        <thead>
          <tr>
            <th data-sort-type="text">Kind</th>
            <th data-sort-type="text">Project</th>
            <th data-sort-type="text">Status</th>
            <th data-sort-type="text">Trigger</th>
            <th data-sort-type="date">Created</th>
            <th data-sort-type="date">Completed</th>
          </tr>
        </thead>
        <tbody id="overview-tasks-table-body">
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
        title="Harbor Operator - Overview",
        body=body,
        bootstrap_json=_bootstrap_payload("overview"),
    )


def _pending_actions_page() -> HTMLResponse:
    body = """
<div class="page" id="operator-shell" data-operator-shell="pending-actions">
  <header class="page-header">
    <div>
      <h1>Pending Actions</h1>
      <p class="page-subtitle">
        Cross-project view of open review-queue items. Click a row to jump
        into the owning project.
      </p>
    </div>
    <div class="actions">
      <a href="/operator/projects">Projects</a>
      <button
        type="button"
        class="action-button secondary"
        id="pending-actions-reload-button"
        data-action="reload-pending-actions"
      >
        Reload
      </button>
    </div>
  </header>

  <section class="section-card" data-section-key="pending-actions-list">
    <h2>Open review-queue items</h2>
    <p class="action-note" data-pending-actions-note>
      Items with status <code class="inline">open</code>, most recent first.
    </p>
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Project</th>
            <th>Title</th>
            <th>Kind</th>
            <th>Priority</th>
            <th>Created</th>
            <th>Updated</th>
          </tr>
        </thead>
        <tbody id="pending-actions-table-body" data-pending-actions="open-items">
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
        title="Harbor Operator - Pending Actions",
        body=body,
        bootstrap_json=_bootstrap_payload("pending-actions"),
    )


def _scheduler_page() -> HTMLResponse:
    handler_keys = all_known_task_kinds()
    handler_rows = "\n".join(
        f"""
          <tr data-scheduler-row="{key}">
            <td><code class="inline">{key}</code></td>
            <td>
              <label class="scheduler-toggle">
                <input
                  type="checkbox"
                  data-scheduler-enabled-toggle="{key}"
                  data-scheduler-task-kind="{key}"
                />
                <span data-scheduler-enabled-label="{key}">disabled</span>
              </label>
            </td>
            <td>
              <input
                type="number"
                min="1"
                step="1"
                value="{SCHEDULER_DEFAULT_INTERVAL_SECONDS}"
                data-scheduler-interval-input="{key}"
                data-scheduler-task-kind="{key}"
              />
            </td>
            <td data-scheduler-last-run-at="{key}">&mdash;</td>
            <td data-scheduler-next-run-at="{key}">&mdash;</td>
            <td>
              <button
                type="button"
                class="action-button secondary"
                data-scheduler-save-button="{key}"
                data-scheduler-task-kind="{key}"
              >Save</button>
            </td>
          </tr>"""
        for key in handler_keys
    )
    registered_json = json.dumps(handler_keys).replace("</", "<\\/")
    default_interval = SCHEDULER_DEFAULT_INTERVAL_SECONDS
    body = f"""
<div class="page" id="operator-shell" data-operator-shell="scheduler">
  <header class="page-header">
    <div>
      <h1>Scheduler</h1>
      <p class="page-subtitle">
        Registered automation handlers. Enable a handler, set an interval,
        and trigger a tick on demand. Schedules fan out across all projects.
      </p>
    </div>
    <div class="actions">
      <a href="/operator/projects">Projects</a>
      <button
        type="button"
        class="action-button secondary"
        id="scheduler-reload-button"
        data-action="reload-scheduler"
      >Reload</button>
      <button
        type="button"
        class="action-button"
        id="scheduler-tick-button"
        data-scheduler-tick-button
      >Run tick now</button>
    </div>
  </header>

  <section class="section-card" data-section-key="scheduler-recent-runs">
    <h2>Recent scheduled runs</h2>
    <p class="action-note">
      Last scheduled automation tasks, newest first. Shows up to 50 entries.
      Global handler runs render with project <code class="inline">(global)</code>.
    </p>
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Started</th>
            <th>Handler</th>
            <th>Project</th>
            <th>Status</th>
            <th>Duration</th>
            <th>Note</th>
          </tr>
        </thead>
        <tbody id="scheduler-recent-tasks-body" data-scheduler-recent-tasks>
          <tr>
            <td colspan="6" class="empty">Loading...</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>

  <section class="section-card" data-section-key="scheduler-handlers">
    <h2>Handlers</h2>
    <p class="action-note">
      Handlers listed below are registered in <code class="inline">SCHEDULE_HANDLERS</code>.
      Saving creates or updates the schedule row; unsaved handlers are not ticked.
      Default interval is {default_interval} seconds.
    </p>
    <div
      class="table-wrap"
      data-scheduler-registered-handlers='{registered_json}'
      data-scheduler-default-interval="{default_interval}"
    >
      <table>
        <thead>
          <tr>
            <th>Handler</th>
            <th>Enabled</th>
            <th>Interval (seconds)</th>
            <th>Last run</th>
            <th>Next run</th>
            <th></th>
          </tr>
        </thead>
        <tbody id="scheduler-table-body" data-scheduler-table>
{handler_rows}
        </tbody>
      </table>
    </div>
  </section>
</div>
"""
    return _render_document(
        title="Harbor Operator - Scheduler",
        body=body,
        bootstrap_json=_bootstrap_payload("scheduler"),
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


@router.get("/operator/overview", include_in_schema=False)
def operator_overview_page() -> HTMLResponse:
    return _overview_page()


@router.get("/operator/pending-actions", include_in_schema=False)
def operator_pending_actions_page() -> HTMLResponse:
    return _pending_actions_page()


@router.get("/operator/scheduler", include_in_schema=False)
def operator_scheduler_page() -> HTMLResponse:
    return _scheduler_page()


@router.get("/operator/projects/{project_id}", include_in_schema=False)
def operator_project_detail_page(project_id: str) -> HTMLResponse:
    return _project_detail_page(project_id)
