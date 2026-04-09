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
"""


BASE_SCRIPT = """
const textFallback = "&mdash;";
const bootstrap = JSON.parse(
  document.getElementById("harbor-operator-bootstrap").textContent,
);
const apiBase = bootstrap.apiBase;
let currentProject = null;
let currentCampaigns = [];
let currentRuns = [];

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

const parseErrorDetail = async (response) => {
  let detail = response.statusText || "Request failed.";
  try {
    const payload = await response.json();
    detail = payload.detail || JSON.stringify(payload);
  } catch (error) {
    detail = response.statusText || "Request failed.";
  }
  return `${response.status} ${detail}`;
};

const fetchJson = async (url) => {
  const response = await fetch(url, {
    headers: { Accept: "application/json" },
  });
  if (!response.ok) {
    throw new Error(await parseErrorDetail(response));
  }
  return response.json();
};

const postJson = async (url, payload) => {
  const response = await fetch(url, {
    method: "POST",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw new Error(await parseErrorDetail(response));
  }
  return response.json();
};

const safeTrim = (value) => String(value ?? "").trim();

const optionalText = (value) => {
  const trimmed = safeTrim(value);
  return trimmed || null;
};

const optionalInt = (value) => {
  const trimmed = safeTrim(value);
  if (!trimmed) {
    return null;
  }
  const parsed = Number.parseInt(trimmed, 10);
  if (Number.isNaN(parsed)) {
    throw new Error("Rank must be a whole number.");
  }
  return parsed;
};

const setSelectOptions = (element, options, emptyLabel) => {
  if (!element) {
    return;
  }
  element.innerHTML = "";
  if (!options.length) {
    const emptyOption = document.createElement("option");
    emptyOption.value = "";
    emptyOption.textContent = emptyLabel;
    element.appendChild(emptyOption);
    element.value = "";
    return;
  }

  const placeholder = document.createElement("option");
  placeholder.value = "";
  placeholder.textContent = "Select...";
  element.appendChild(placeholder);

  for (const optionData of options) {
    const option = document.createElement("option");
    option.value = optionData.value;
    option.textContent = optionData.label;
    element.appendChild(option);
  }
  element.value = "";
};

const refreshCreateFormState = () => {
  const campaignSelect = byId("create-run-campaign-id");
  const runSubmit = byId("create-run-submit");
  const runHint = byId("create-run-hint");

  const campaignOptions = currentCampaigns.map((item) => ({
    value: item.search_campaign_id,
    label: item.title,
  }));
  setSelectOptions(campaignSelect, campaignOptions, "No campaigns available.");

  const hasCampaigns = currentCampaigns.length > 0;
  if (campaignSelect) {
    campaignSelect.disabled = !hasCampaigns;
  }
  if (runSubmit) {
    runSubmit.disabled = !hasCampaigns;
  }
  if (runHint) {
    runHint.textContent = hasCampaigns
      ? "Create a manual run in an existing campaign."
      : "Create a search campaign first.";
  }

  const campaignTitleById = new Map(
    currentCampaigns.map((item) => [item.search_campaign_id, item.title]),
  );
  const runOptions = currentRuns.map((item) => ({
    value: item.search_run_id,
    label: `${item.title} — ${campaignTitleById.get(item.search_campaign_id) || "Run"}`,
  }));

  const runSelect = byId("create-candidate-run-id");
  const candidateSubmit = byId("create-candidate-submit");
  const candidateHint = byId("create-candidate-hint");
  setSelectOptions(runSelect, runOptions, "No runs available.");

  const hasRuns = currentRuns.length > 0;
  if (runSelect) {
    runSelect.disabled = !hasRuns;
  }
  if (candidateSubmit) {
    candidateSubmit.disabled = !hasRuns;
  }
  if (candidateHint) {
    candidateHint.textContent = hasRuns
      ? "Add a manual search candidate to an existing run."
      : "Create a search run first.";
  }
};

const runFormAction = async (form, statusId, callback, successMessage, afterSuccess) => {
  const submitButton = form.querySelector('button[type="submit"]');
  const originalLabel = submitButton ? submitButton.textContent : "";

  if (submitButton) {
    submitButton.disabled = true;
    submitButton.textContent = "Working...";
  }
  setStatus(statusId, "Executing create action...");

  try {
    const result = await callback();
    if (afterSuccess) {
      await afterSuccess(result);
    }
    setStatus(statusId, successMessage);
  } catch (error) {
    setStatus(statusId, error.message, true);
  } finally {
    if (submitButton && submitButton.isConnected) {
      submitButton.disabled = false;
      submitButton.textContent = originalLabel;
    }
  }
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


const buildProjectPayload = (form) => {
  const payload = {
    title: safeTrim(form.elements.namedItem("title").value),
    short_description: optionalText(
      form.elements.namedItem("short_description").value,
    ),
    project_type: "standard",
  };
  if (!payload.title) {
    throw new Error("Project title is required.");
  }
  return payload;
};

const buildCampaignPayload = (form) => {
  const payload = {
    title: safeTrim(form.elements.namedItem("title").value),
    query_text: optionalText(form.elements.namedItem("query_text").value),
    campaign_kind: "manual",
    status: "planned",
    note: optionalText(form.elements.namedItem("note").value),
  };
  if (!payload.title) {
    throw new Error("Campaign title is required.");
  }
  return payload;
};

const buildRunPayload = (form) => {
  const searchCampaignId = safeTrim(
    form.elements.namedItem("search_campaign_id").value,
  );
  if (!searchCampaignId) {
    throw new Error("Select a search campaign first.");
  }
  const payload = {
    searchCampaignId,
    body: {
      title: safeTrim(form.elements.namedItem("title").value),
      run_kind: "manual",
      status: "planned",
      query_text_snapshot: optionalText(
        form.elements.namedItem("query_text_snapshot").value,
      ),
      note: optionalText(form.elements.namedItem("note").value),
    },
  };
  if (!payload.body.title) {
    throw new Error("Run title is required.");
  }
  return payload;
};

const buildCandidatePayload = (form) => {
  const searchRunId = safeTrim(form.elements.namedItem("search_run_id").value);
  if (!searchRunId) {
    throw new Error("Select a search run first.");
  }
  const selectedRun = currentRuns.find((item) => item.search_run_id === searchRunId);
  if (!selectedRun) {
    throw new Error("Selected search run was not found.");
  }

  const payload = {
    searchCampaignId: selectedRun.search_campaign_id,
    searchRunId,
    body: {
      title: safeTrim(form.elements.namedItem("title").value),
      url: safeTrim(form.elements.namedItem("url").value),
      domain: optionalText(form.elements.namedItem("domain").value),
      snippet: optionalText(form.elements.namedItem("snippet").value),
      rank: optionalInt(form.elements.namedItem("rank").value),
      disposition: "pending",
      note: optionalText(form.elements.namedItem("note").value),
    },
  };
  if (!payload.body.title) {
    throw new Error("Candidate title is required.");
  }
  if (!payload.body.url) {
    throw new Error("Candidate URL is required.");
  }
  return payload;
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

const renderCandidateAction = (item) => {
  if (item.disposition !== "pending") {
    return `<span class="empty">Not available</span>`;
  }
  return `
    <button
      type="button"
      class="action-button"
      data-action="promote-candidate"
      data-search-campaign-id="${escapeHtml(item.search_campaign_id)}"
      data-search-run-id="${escapeHtml(item.search_run_id)}"
      data-search-result-candidate-id="${
        escapeHtml(item.search_result_candidate_id)
      }"
    >
      Promote to review
    </button>
  `;
};

const renderCandidates = (items) => {
  const body = byId("candidates-table-body");
  if (!body) {
    return;
  }
  if (!items.length) {
    body.innerHTML = emptyRow(7);
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
          <td>${renderCandidateAction(item)}</td>
        </tr>
      `,
    )
    .join("");
};

const renderReviewQueueAction = (item) => {
  const isPromotable =
    item.queue_kind === "candidate_review" &&
    item.status !== "completed" &&
    !item.source_id &&
    !item.project_source_id;

  if (!isPromotable) {
    return `<span class="empty">Not available</span>`;
  }

  return `
    <button
      type="button"
      class="action-button"
      data-action="promote-review-item"
      data-review-queue-item-id="${escapeHtml(item.review_queue_item_id)}"
    >
      Promote to source
    </button>
  `;
};

const renderReviewQueue = (items) => {
  const body = byId("review-queue-table-body");
  if (!body) {
    return;
  }
  if (!items.length) {
    body.innerHTML = emptyRow(7);
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
          <td>${renderReviewQueueAction(item)}</td>
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
          <td>
            ${item.review_queue_status ? badge(item.review_queue_status) : textFallback}
          </td>
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

const handleProjectsCreateSubmit = async (form) => {
  await runFormAction(
    form,
    "projects-create-status",
    () => postJson(`${apiBase}/projects`, buildProjectPayload(form)),
    "Project created.",
    async (project) => {
      window.location.assign(
        `/operator/projects/${encodeURIComponent(project.project_id)}`,
      );
    },
  );
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

    currentProject = project;
    currentCampaigns = campaignsPayload.items;

    renderProjectHeader(project);
    renderSummary(summary);
    renderCampaigns(campaignsPayload.items);
    renderReviewQueue(reviewQueuePayload.items);
    renderProjectSources(projectSourcesPayload.items);
    renderLineage(summary.lineage_items);

    const runs = [];
    const candidates = [];

    for (const campaign of campaignsPayload.items) {
      const campaignBase = `${projectBase}/search-campaigns/${
        encodeURIComponent(campaign.search_campaign_id)
      }`;
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

    currentRuns = runs;
    refreshCreateFormState();

    renderRuns(runs);
    renderCandidates(candidates);
    setStatus("detail-status", `Loaded project ${project.title}.`);
  } catch (error) {
    setStatus("detail-status", error.message, true);
  }
};

const handleProjectDetailCreateSubmit = async (form) => {
  const projectId = encodeURIComponent(bootstrap.projectId);
  const projectBase = `${apiBase}/projects/${projectId}`;

  if (form.dataset.createForm === "create-search-campaign") {
    await runFormAction(
      form,
      "create-status",
      () => postJson(`${projectBase}/search-campaigns`, buildCampaignPayload(form)),
      "Search campaign created.",
      async () => {
        form.reset();
        await loadProjectDetailPage();
      },
    );
    return;
  }

  if (form.dataset.createForm === "create-search-run") {
    const payload = buildRunPayload(form);
    const campaignId = encodeURIComponent(payload.searchCampaignId);
    const url = `${projectBase}/search-campaigns/${campaignId}/runs`;
    await runFormAction(
      form,
      "create-status",
      () => postJson(url, payload.body),
      "Search run created.",
      async () => {
        form.reset();
        await loadProjectDetailPage();
      },
    );
    return;
  }

  if (form.dataset.createForm === "create-result-candidate") {
    const payload = buildCandidatePayload(form);
    const campaignId = encodeURIComponent(payload.searchCampaignId);
    const runId = encodeURIComponent(payload.searchRunId);
    const url = `${projectBase}/search-campaigns/${campaignId}/runs/${runId}` +
      "/result-candidates";
    await runFormAction(
      form,
      "create-status",
      () => postJson(url, payload.body),
      "Result candidate created.",
      async () => {
        form.reset();
        await loadProjectDetailPage();
      },
    );
  }
};

const runOperatorAction = async (button, callback, successMessage) => {
  const originalLabel = button.textContent;
  button.disabled = true;
  button.textContent = "Working...";
  setStatus("action-status", "Executing operator action...");
  try {
    await callback();
    await loadProjectDetailPage();
    setStatus("action-status", successMessage);
  } catch (error) {
    setStatus("action-status", error.message, true);
  } finally {
    if (button.isConnected) {
      button.disabled = false;
      button.textContent = originalLabel;
    }
  }
};

document.addEventListener("submit", async (event) => {
  const form = event.target.closest("form[data-create-form]");
  if (!form) {
    return;
  }

  event.preventDefault();

  if (bootstrap.page === "projects") {
    await handleProjectsCreateSubmit(form);
    return;
  }
  if (bootstrap.page === "project-detail") {
    await handleProjectDetailCreateSubmit(form);
  }
});

document.addEventListener("click", async (event) => {
  const button = event.target.closest("button[data-action]");
  if (!button || !bootstrap.projectId) {
    return;
  }

  const projectBase = `${apiBase}/projects/${encodeURIComponent(bootstrap.projectId)}`;

  if (button.dataset.action === "promote-candidate") {
    const campaignId = encodeURIComponent(button.dataset.searchCampaignId);
    const runId = encodeURIComponent(button.dataset.searchRunId);
    const candidateId = encodeURIComponent(button.dataset.searchResultCandidateId);
    const url = `${projectBase}/search-campaigns/${campaignId}/runs/${runId}` +
      `/result-candidates/${candidateId}/promote-to-review`;
    await runOperatorAction(
      button,
      () => postJson(url, { note: "Promoted from operator web shell." }),
      "Candidate promoted to review queue.",
    );
    return;
  }

  if (button.dataset.action === "promote-review-item") {
    const reviewQueueItemId = encodeURIComponent(button.dataset.reviewQueueItemId);
    const url = `${projectBase}/review-queue-items/${reviewQueueItemId}` +
      "/promote-to-source";
    await runOperatorAction(
      button,
      () => postJson(url, { note: "Accepted from operator web shell." }),
      "Review queue item promoted to source.",
    );
  }
});

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
            <span class="form-hint">
              Defaults: status draft, type standard.
            </span>
          </div>
        </div>
      </div>
      <p
        class="status"
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
    <h2>Operator Actions</h2>
    <p class="action-note">
      Actions stay thin and call the existing Harbor APIs only.
    </p>
    <ul class="action-list">
      <li data-operator-action="promote-to-review">
        Candidate -> Review Queue
      </li>
      <li data-operator-action="promote-to-source">
        Review Queue -> Source / ProjectSource
      </li>
    </ul>
    <p class="status" id="action-status" data-action-status="operator-actions">
      No action executed yet.
    </p>
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
          <span class="form-hint" id="create-run-hint">
            Loading campaigns...
          </span>
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
          <span class="form-hint" id="create-candidate-hint">
            Loading runs...
          </span>
        </div>
      </form>
    </div>
    <p
      class="status"
      id="create-status"
      data-create-status="project-create-actions"
    >
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
