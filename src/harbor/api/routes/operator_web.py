from __future__ import annotations

import json

from fastapi import APIRouter
from fastapi.responses import HTMLResponse, RedirectResponse

from harbor.config import get_settings

router = APIRouter(tags=["operator_web"])


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
  color: #bfdbfe;
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
"""


BASE_SCRIPT = """
const textFallback = "&mdash;";
const bootstrap = JSON.parse(
  document.getElementById("harbor-operator-bootstrap").textContent,
);
const apiBase = bootstrap.apiBase;

const byId = (id) => document.getElementById(id);

const escapeHtml = (value) =>
  String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");

const safeText = (value) => {
  if (value === null || value === undefined || value === "") {
    return textFallback;
  }
  return escapeHtml(value);
};

const formatDateTime = (value) => {
  if (!value) {
    return textFallback;
  }
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return escapeHtml(value);
  }
  return escapeHtml(parsed.toLocaleString());
};

const badge = (value) => `<span class="badge">${safeText(value)}</span>`;
const inlineCode = (value) => `<code class="inline">${safeText(value)}</code>`;

const emptyRow = (colspan, text = "No items.") => (
  `<tr><td colspan="${colspan}" class="empty">${safeText(text)}</td></tr>`
);

const setStatus = (id, text, isError = false) => {
  const target = byId(id);
  if (!target) {
    return;
  }
  target.textContent = text;
  target.classList.toggle("error", isError);
};

const fetchJson = async (url) => {
  const response = await fetch(url, {
    headers: { Accept: "application/json" },
  });
  if (!response.ok) {
    let detail = response.statusText;
    try {
      const payload = await response.json();
      detail = payload.detail || JSON.stringify(payload);
    } catch (error) {
      detail = response.statusText || "Request failed.";
    }
    throw new Error(`${response.status} ${detail}`);
  }
  return response.json();
};

const renderProjectsTable = (projects) => {
  const body = byId("projects-table-body");
  if (!body) {
    return;
  }
  if (!projects.length) {
    body.innerHTML = emptyRow(6);
    return;
  }
  body.innerHTML = projects
    .map(
      (project) => `
        <tr>
          <td>
            <a href="/operator/projects/${encodeURIComponent(project.project_id)}">
              ${safeText(project.title)}
            </a>
          </td>
          <td>${badge(project.status)}</td>
          <td>${safeText(project.project_type)}</td>
          <td>${safeText(project.blueprint_status)}</td>
          <td>${formatDateTime(project.updated_at)}</td>
          <td>${safeText(project.short_description)}</td>
        </tr>
      `,
    )
    .join("");
};

const renderProjectHeader = (project) => {
  const title = byId("project-title");
  const meta = byId("project-meta");
  if (title) {
    title.textContent = project.title;
  }
  if (!meta) {
    return;
  }
  meta.innerHTML = `
    <div class="meta-row">
      <span class="meta-key">Project ID</span>
      <code class="page-code">${safeText(project.project_id)}</code>
    </div>
    <div class="meta-row">
      <span class="meta-key">Status</span>
      ${badge(project.status)}
    </div>
    <div class="meta-row">
      <span class="meta-key">Type</span>
      <span>${safeText(project.project_type)}</span>
    </div>
    <div class="meta-row">
      <span class="meta-key">Blueprint</span>
      <span>${safeText(project.blueprint_status)}</span>
    </div>
    <div class="meta-row">
      <span class="meta-key">Description</span>
      <span>${safeText(project.short_description)}</span>
    </div>
  `;
};

const renderSummary = (summary) => {
  const target = byId("workflow-summary-grid");
  if (!target) {
    return;
  }
  const cards = [
    ["Campaigns", summary.counts.search_campaign_count],
    ["Runs", summary.counts.search_run_count],
    ["Candidates", summary.counts.search_result_candidate_count],
    ["Pending", summary.counts.candidate_pending_count],
    ["Promoted", summary.counts.candidate_promoted_count],
    ["Accepted", summary.counts.candidate_accepted_count],
    ["Review queue", summary.counts.review_queue_item_count],
    ["Review open", summary.counts.review_queue_open_count],
    ["Review done", summary.counts.review_queue_completed_count],
    ["Project sources", summary.counts.project_source_count],
  ];
  target.innerHTML = cards
    .map(
      ([label, value]) => `
        <div class="summary-card">
          <div class="summary-label">${safeText(label)}</div>
          <div class="summary-value">${safeText(value)}</div>
        </div>
      `,
    )
    .join("");
};

const renderCampaigns = (items) => {
  const body = byId("campaigns-table-body");
  if (!body) {
    return;
  }
  if (!items.length) {
    body.innerHTML = emptyRow(6);
    return;
  }
  body.innerHTML = items
    .map(
      (item) => `
        <tr>
          <td>${safeText(item.title)}</td>
          <td>${badge(item.status)}</td>
          <td>${safeText(item.campaign_kind)}</td>
          <td>${safeText(item.query_text)}</td>
          <td>${formatDateTime(item.updated_at)}</td>
          <td>${safeText(item.note)}</td>
        </tr>
      `,
    )
    .join("");
};

const renderRuns = (items) => {
  const body = byId("runs-table-body");
  if (!body) {
    return;
  }
  if (!items.length) {
    body.innerHTML = emptyRow(6);
    return;
  }
  body.innerHTML = items
    .map(
      (item) => `
        <tr>
          <td>${safeText(item.title)}</td>
          <td>${badge(item.status)}</td>
          <td>${safeText(item.run_kind)}</td>
          <td>${safeText(item.query_text_snapshot)}</td>
          <td>${formatDateTime(item.updated_at)}</td>
          <td>${safeText(item.note)}</td>
        </tr>
      `,
    )
    .join("");
};

const renderCandidates = (items) => {
  const body = byId("candidates-table-body");
  if (!body) {
    return;
  }
  if (!items.length) {
    body.innerHTML = emptyRow(6);
    return;
  }
  body.innerHTML = items
    .map(
      (item) => `
        <tr>
          <td>
            <a href="${escapeHtml(item.url)}" target="_blank" rel="noreferrer">
              ${safeText(item.title)}
            </a>
          </td>
          <td>${badge(item.disposition)}</td>
          <td>${safeText(item.domain)}</td>
          <td>${safeText(item.rank)}</td>
          <td>${formatDateTime(item.updated_at)}</td>
          <td>${safeText(item.snippet)}</td>
        </tr>
      `,
    )
    .join("");
};

const renderReviewQueue = (items) => {
  const body = byId("review-queue-table-body");
  if (!body) {
    return;
  }
  if (!items.length) {
    body.innerHTML = emptyRow(6);
    return;
  }
  body.innerHTML = items
    .map(
      (item) => `
        <tr>
          <td>${safeText(item.title)}</td>
          <td>${badge(item.status)}</td>
          <td>${safeText(item.priority)}</td>
          <td>${safeText(item.queue_kind)}</td>
          <td>${inlineCode(item.search_result_candidate_id)}</td>
          <td>${formatDateTime(item.updated_at)}</td>
        </tr>
      `,
    )
    .join("");
};

const renderProjectSources = (items) => {
  const body = byId("project-sources-table-body");
  if (!body) {
    return;
  }
  if (!items.length) {
    body.innerHTML = emptyRow(6);
    return;
  }
  body.innerHTML = items
    .map(
      (item) => `
        <tr>
          <td>${safeText(item.source.title)}</td>
          <td>${badge(item.review_status)}</td>
          <td>${safeText(item.relevance)}</td>
          <td>${safeText(item.source.trust_tier)}</td>
          <td>${inlineCode(item.project_source_id)}</td>
          <td>${safeText(item.source.canonical_url)}</td>
        </tr>
      `,
    )
    .join("");
};

const renderLineage = (items) => {
  const body = byId("lineage-table-body");
  if (!body) {
    return;
  }
  if (!items.length) {
    body.innerHTML = emptyRow(6);
    return;
  }
  body.innerHTML = items
    .map(
      (item) => `
        <tr>
          <td>${safeText(item.candidate_title)}</td>
          <td>${badge(item.candidate_disposition)}</td>
          <td>${item.review_queue_status ? badge(item.review_queue_status) : textFallback}</td>
          <td>
            ${
              item.project_source_review_status
                ? badge(item.project_source_review_status)
                : textFallback
            }
          </td>
          <td>
            ${
              item.review_queue_item_id
                ? inlineCode(item.review_queue_item_id)
                : textFallback
            }
          </td>
          <td>
            ${item.project_source_id ? inlineCode(item.project_source_id) : textFallback}
          </td>
        </tr>
      `,
    )
    .join("");
};

const loadProjectsPage = async () => {
  setStatus("projects-status", "Loading projects...");
  try {
    const payload = await fetchJson(`${apiBase}/projects`);
    renderProjectsTable(payload.items);
    setStatus("projects-status", `${payload.items.length} project(s) loaded.`);
  } catch (error) {
    setStatus("projects-status", error.message, true);
  }
};

const loadProjectDetailPage = async () => {
  const projectId = bootstrap.projectId;
  const projectBase = `${apiBase}/projects/${encodeURIComponent(projectId)}`;

  setStatus("detail-status", "Loading project detail...");
  try {
    const projectPromise = fetchJson(projectBase);
    const summaryPromise = fetchJson(`${projectBase}/workflow-summary`);
    const campaignsPromise = fetchJson(`${projectBase}/search-campaigns`);
    const reviewQueuePromise = fetchJson(`${projectBase}/review-queue-items`);
    const projectSourcesPromise = fetchJson(`${projectBase}/sources`);

    const [project, summary, campaignsPayload, reviewQueuePayload, projectSourcesPayload] =
      await Promise.all([
        projectPromise,
        summaryPromise,
        campaignsPromise,
        reviewQueuePromise,
        projectSourcesPromise,
      ]);

    renderProjectHeader(project);
    renderSummary(summary);
    renderCampaigns(campaignsPayload.items);
    renderReviewQueue(reviewQueuePayload.items);
    renderProjectSources(projectSourcesPayload.items);
    renderLineage(summary.lineage_items);

    const runs = [];
    const candidates = [];

    for (const campaign of campaignsPayload.items) {
      const campaignBase =
        `${projectBase}/search-campaigns/${encodeURIComponent(campaign.search_campaign_id)}`;
      const runsPayload = await fetchJson(`${campaignBase}/runs`);
      for (const run of runsPayload.items) {
        runs.push(run);
        const runBase = `${campaignBase}/runs/${encodeURIComponent(run.search_run_id)}`;
        const candidatesPayload = await fetchJson(`${runBase}/result-candidates`);
        for (const candidate of candidatesPayload.items) {
          candidates.push(candidate);
        }
      }
    }

    renderRuns(runs);
    renderCandidates(candidates);
    setStatus("detail-status", `Loaded project ${project.title}.`);
  } catch (error) {
    setStatus("detail-status", error.message, true);
  }
};

if (bootstrap.page === "projects") {
  loadProjectsPage();
}
if (bootstrap.page === "project-detail") {
  loadProjectDetailPage();
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
    <script>{BASE_SCRIPT}</script>
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
      <p class="status" id="projects-status">Waiting to load projects.</p>
    </div>
    <div class="actions">
      <a href="/healthz">Health</a>
      <a href="/runtime">Runtime</a>
    </div>
  </header>

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
        Read-only operator surface for workflow summary and lineage.
      </p>
      <p class="status" id="detail-status">Waiting to load project detail.</p>
    </div>
    <div class="actions">
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
          </tr>
        </thead>
        <tbody id="candidates-table-body">
          <tr>
            <td colspan="6" class="empty">Loading...</td>
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
          </tr>
        </thead>
        <tbody id="review-queue-table-body">
          <tr>
            <td colspan="6" class="empty">Loading...</td>
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
          </tr>
        </thead>
        <tbody id="project-sources-table-body">
          <tr>
            <td colspan="6" class="empty">Loading...</td>
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


@router.get("/operator", include_in_schema=False)
def operator_root() -> RedirectResponse:
    return RedirectResponse(url="/operator/projects", status_code=307)


@router.get("/operator/projects", include_in_schema=False)
def operator_projects_page() -> HTMLResponse:
    return _projects_page()


@router.get("/operator/projects/{project_id}", include_in_schema=False)
def operator_project_detail_page(project_id: str) -> HTMLResponse:
    return _project_detail_page(project_id)
