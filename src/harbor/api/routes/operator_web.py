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
.chat-message {
  border: 1px solid #334155;
  border-radius: 12px;
  padding: 14px;
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
.chat-turn-selector {
  max-width: 360px;
}
.chat-turn-summary {
  margin-top: 0;
}
.chat-inspector {
  display: grid;
  gap: 12px;
}
.chat-turn-detail {
  display: grid;
  gap: 8px;
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


BASE_SCRIPT = """
const textFallback = "&mdash;";
const bootstrap = JSON.parse(
  document.getElementById("harbor-operator-bootstrap").textContent,
);
const apiBase = bootstrap.apiBase;
let currentProject = null;
let currentCampaigns = [];
let currentRuns = [];
let currentDryRunLogs = [];
let projectsLoadToken = 0;
let detailLoadToken = 0;

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

const setStatus = (id, text, kind = "info") => {
  const target = byId(id);
  if (!target) {
    return;
  }
  target.textContent = text;
  target.classList.remove("info", "success", "error");
  target.classList.add(kind);
  target.dataset.statusKind = kind;
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

const displayText = (value) => {
  if (value === null || value === undefined || value === "") {
    return "—";
  }
  return String(value);
};

const setTextContent = (id, value) => {
  const target = byId(id);
  if (!target) {
    return;
  }
  target.textContent = displayText(value);
};

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

const setControlsDisabled = (root, disabled) => {
  if (!root) {
    return;
  }
  for (const element of root.querySelectorAll("button, input, select, textarea")) {
    element.disabled = disabled;
  }
};

const setButtonsDisabled = (selector, disabled) => {
  for (const element of document.querySelectorAll(selector)) {
    element.disabled = disabled;
  }
};

const setTableBodyMessage = (id, colspan, text) => {
  const body = byId(id);
  if (!body) {
    return;
  }
  body.innerHTML = emptyRow(colspan, text);
};

const renderSummaryMessage = (text) => {
  const target = byId("workflow-summary-grid");
  if (!target) {
    return;
  }
  target.innerHTML = `<div class="empty">${safeText(text)}</div>`;
};

const setProjectsPageDisabled = (disabled) => {
  setControlsDisabled(byId("create-project-form"), disabled);
  const reloadButton = byId("projects-reload-button");
  if (reloadButton) {
    reloadButton.disabled = disabled;
  }
};

const setProjectInteractionDisabled = (disabled) => {
  const forms = document.querySelectorAll(
    'form[data-create-form], form[data-openai-form]',
  );
  for (const form of forms) {
    setControlsDisabled(form, disabled);
  }
  setButtonsDisabled('button[data-action]', disabled);
  const reloadButton = byId("project-detail-reload-button");
  if (reloadButton) {
    reloadButton.disabled = disabled;
  }
};

const resetOpenAIDryRunPanel = (statusText = "No dry run executed yet.", kind = "info") => {
  setTextContent("openai-dry-run-provider", null);
  setTextContent("openai-dry-run-model", null);
  setTextContent("openai-dry-run-response-status", null);
  setTextContent("openai-dry-run-response-id", null);
  setTextContent("openai-dry-run-output-text", null);
  setStatus("openai-dry-run-status", statusText, kind);
};

const renderOpenAIDryRunResult = (payload) => {
  setTextContent("openai-dry-run-provider", payload.provider);
  setTextContent("openai-dry-run-model", payload.model);
  setTextContent(
    "openai-dry-run-response-status",
    payload.response_status || payload.status,
  );
  setTextContent("openai-dry-run-response-id", payload.response_id);
  setTextContent(
    "openai-dry-run-output-text",
    payload.output_text || payload.error_message,
  );

  let statusText = `Dry run status: ${displayText(payload.status)}.`;
  let statusKind = "info";

  if (payload.status === "completed") {
    statusText = payload.persisted
      ? "Dry run completed and persisted to Harbor history."
      : "Dry run completed.";
    statusKind = "success";
  } else if (payload.status === "not_configured") {
    statusText = "OpenAI is not configured.";
    statusKind = "error";
  } else if (payload.status === "sdk_unavailable") {
    statusText = "OpenAI SDK is unavailable.";
    statusKind = "error";
  } else if (payload.status === "error") {
    statusText = payload.error_message || "Dry run failed.";
    statusKind = "error";
  }

  setStatus("openai-dry-run-status", statusText, statusKind);
};

const renderOpenAIDryRunHistory = (items) => {
  const body = byId("openai-dry-run-history-body");
  if (!body) {
    return;
  }
  if (!items.length) {
    body.innerHTML = emptyRow(6, "No persisted dry runs yet.");
    return;
  }
  body.innerHTML = items
    .map(
      (item) => `
        <tr>
          <td>${formatDateTime(item.created_at)}</td>
          <td>${badge(item.status)}</td>
          <td>${safeText(item.model)}</td>
          <td>${item.response_id ? inlineCode(item.response_id) : textFallback}</td>
          <td>${safeText(item.request_input_text)}</td>
          <td>${safeText(item.output_text || item.error_message)}</td>
        </tr>
      `,
    )
    .join("");
};

const loadProjectDryRunHistory = async (projectId) => {
  const encodedProjectId = encodeURIComponent(projectId);
  const payload = await fetchJson(
    `${apiBase}/openai/projects/${encodedProjectId}/dry-run-logs`,
  );
  currentDryRunLogs = payload.items;
  renderOpenAIDryRunHistory(payload.items);
  return payload.items;
};

const buildOpenAIDryRunPayload = (form) => {
  const payload = {
    input_text: safeTrim(form.elements.namedItem("input_text").value),
    instructions: optionalText(form.elements.namedItem("instructions").value),
    persist: Boolean(form.elements.namedItem("persist").checked),
  };
  if (!payload.input_text) {
    throw new Error("Operator request is required.");
  }
  return payload;
};

const handleProjectDetailOpenAISubmit = async (form) => {
  if (form.dataset.busy === "true") {
    return;
  }
  form.dataset.busy = "true";

  const submitButton = form.querySelector('button[type="submit"]');
  const originalLabel = submitButton ? submitButton.textContent : "";

  if (submitButton) {
    submitButton.textContent = "Working...";
  }

  setProjectInteractionDisabled(true);
  setStatus("openai-dry-run-status", "Executing OpenAI dry run...", "info");
  setTextContent("openai-dry-run-response-status", "pending");
  setTextContent("openai-dry-run-response-id", null);
  setTextContent("openai-dry-run-output-text", "Waiting for response...");

  try {
    const projectId = encodeURIComponent(bootstrap.projectId);
    const payload = buildOpenAIDryRunPayload(form);
    const result = await postJson(`${apiBase}/openai/projects/${projectId}/dry-run`, payload);
    renderOpenAIDryRunResult(result);
    if (result.persisted) {
      await loadProjectDryRunHistory(bootstrap.projectId);
    }
  } catch (error) {
    setTextContent("openai-dry-run-response-status", "error");
    setTextContent("openai-dry-run-response-id", null);
    setTextContent("openai-dry-run-output-text", error.message);
    setStatus("openai-dry-run-status", error.message, "error");
  } finally {
    form.dataset.busy = "false";
    if (submitButton && submitButton.isConnected) {
      submitButton.textContent = originalLabel;
    }
    setProjectInteractionDisabled(false);
    refreshCreateFormState(currentProject ? "ready" : "error");
  }
};

const setProjectDetailLoadingState = () => {
  renderSummaryMessage("Loading workflow summary...");
  setTableBodyMessage("campaigns-table-body", 6, "Loading...");
  setTableBodyMessage("runs-table-body", 6, "Loading...");
  setTableBodyMessage("candidates-table-body", 7, "Loading...");
  setTableBodyMessage("review-queue-table-body", 7, "Loading...");
  setTableBodyMessage("project-sources-table-body", 6, "Loading...");
  setTableBodyMessage("lineage-table-body", 6, "Loading...");
  setTableBodyMessage("openai-dry-run-history-body", 6, "Loading...");
  currentCampaigns = [];
  currentRuns = [];
  currentDryRunLogs = [];
  refreshCreateFormState("loading");
  resetOpenAIDryRunPanel("Waiting for project detail to load.", "info");
};

const setProjectDetailErrorState = () => {
  renderSummaryMessage("Workflow summary unavailable.");
  setTableBodyMessage("campaigns-table-body", 6, "Load failed.");
  setTableBodyMessage("runs-table-body", 6, "Load failed.");
  setTableBodyMessage("candidates-table-body", 7, "Load failed.");
  setTableBodyMessage("review-queue-table-body", 7, "Load failed.");
  setTableBodyMessage("project-sources-table-body", 6, "Load failed.");
  setTableBodyMessage("lineage-table-body", 6, "Load failed.");
  setTableBodyMessage("openai-dry-run-history-body", 6, "Load failed.");
  currentCampaigns = [];
  currentRuns = [];
  currentDryRunLogs = [];
  refreshCreateFormState("error");
  resetOpenAIDryRunPanel("Project detail load failed.", "error");
};

const refreshCreateFormState = (mode = "ready") => {
  const campaignSelect = byId("create-run-campaign-id");
  const runSubmit = byId("create-run-submit");
  const runHint = byId("create-run-hint");
  const runSelect = byId("create-candidate-run-id");
  const candidateSubmit = byId("create-candidate-submit");
  const candidateHint = byId("create-candidate-hint");

  if (mode === "loading") {
    setSelectOptions(campaignSelect, [], "Loading campaigns...");
    setSelectOptions(runSelect, [], "Loading runs...");
    if (runSubmit) {
      runSubmit.disabled = true;
    }
    if (candidateSubmit) {
      candidateSubmit.disabled = true;
    }
    if (runHint) {
      runHint.textContent = "Loading campaigns...";
    }
    if (candidateHint) {
      candidateHint.textContent = "Loading runs...";
    }
    return;
  }

  if (mode === "error") {
    setSelectOptions(campaignSelect, [], "Load failed.");
    setSelectOptions(runSelect, [], "Load failed.");
    if (runSubmit) {
      runSubmit.disabled = true;
    }
    if (candidateSubmit) {
      candidateSubmit.disabled = true;
    }
    if (runHint) {
      runHint.textContent = "Project detail load failed.";
    }
    if (candidateHint) {
      candidateHint.textContent = "Project detail load failed.";
    }
    return;
  }

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
  if (form.dataset.busy === "true") {
    return;
  }
  form.dataset.busy = "true";

  const submitButton = form.querySelector('button[type="submit"]');
  const originalLabel = submitButton ? submitButton.textContent : "";

  if (submitButton) {
    submitButton.textContent = "Working...";
  }

  if (bootstrap.page === "projects") {
    setProjectsPageDisabled(true);
  }
  if (bootstrap.page === "project-detail") {
    setProjectInteractionDisabled(true);
  }

  setStatus(statusId, "Executing create action...", "info");

  try {
    const result = await callback();
    let statusText = successMessage;
    let statusKind = "success";

    if (afterSuccess) {
      const afterSuccessResult = await afterSuccess(result);
      if (afterSuccessResult === false) {
        statusText = `${successMessage} Reload failed; see detail status.`;
        statusKind = "error";
      }
    }

    setStatus(statusId, statusText, statusKind);
  } catch (error) {
    setStatus(statusId, error.message, "error");
  } finally {
    form.dataset.busy = "false";
    if (submitButton && submitButton.isConnected) {
      submitButton.textContent = originalLabel;
    }
    if (bootstrap.page === "projects") {
      setProjectsPageDisabled(false);
    }
    if (bootstrap.page === "project-detail") {
      setProjectInteractionDisabled(false);
      refreshCreateFormState(currentProject ? "ready" : "error");
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
      data-search-result-candidate-id="${escapeHtml(item.search_result_candidate_id)}"
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
  const loadToken = ++projectsLoadToken;
  setProjectsPageDisabled(true);
  setTableBodyMessage("projects-table-body", 6, "Loading...");
  setStatus("projects-status", "Loading projects...", "info");

  try {
    const payload = await fetchJson(`${apiBase}/projects`);
    if (loadToken !== projectsLoadToken) {
      return false;
    }
    renderProjectsTable(payload.items);
    setStatus("projects-status", `${payload.items.length} project(s) loaded.`, "success");
    return true;
  } catch (error) {
    if (loadToken !== projectsLoadToken) {
      return false;
    }
    setTableBodyMessage("projects-table-body", 6, "Load failed.");
    setStatus("projects-status", error.message, "error");
    return false;
  } finally {
    if (loadToken === projectsLoadToken) {
      setProjectsPageDisabled(false);
    }
  }
};

const handleProjectsCreateSubmit = async (form) => {
  await runFormAction(
    form,
    "projects-create-status",
    () => postJson(`${apiBase}/projects`, buildProjectPayload(form)),
    "Project created.",
    async (project) => {
      window.location.assign(`/operator/projects/${encodeURIComponent(project.project_id)}`);
      return true;
    },
  );
};

const loadProjectDetailPage = async () => {
  const projectId = bootstrap.projectId;
  const projectBase = `${apiBase}/projects/${encodeURIComponent(projectId)}`;
  const loadToken = ++detailLoadToken;

  setProjectInteractionDisabled(true);
  setProjectDetailLoadingState();
  setStatus("detail-status", "Loading project detail...", "info");

  try {
    const projectPromise = fetchJson(projectBase);
    const summaryPromise = fetchJson(`${projectBase}/workflow-summary`);
    const campaignsPromise = fetchJson(`${projectBase}/search-campaigns`);
    const reviewQueuePromise = fetchJson(`${projectBase}/review-queue-items`);
    const projectSourcesPromise = fetchJson(`${projectBase}/sources`);
    const dryRunLogsPromise = fetchJson(
      `${apiBase}/openai/projects/${encodeURIComponent(projectId)}/dry-run-logs`,
    );

    const [
      project,
      summary,
      campaignsPayload,
      reviewQueuePayload,
      projectSourcesPayload,
      dryRunLogsPayload,
    ] = await Promise.all([
      projectPromise,
      summaryPromise,
      campaignsPromise,
      reviewQueuePromise,
      projectSourcesPromise,
      dryRunLogsPromise,
    ]);

    if (loadToken !== detailLoadToken) {
      return false;
    }

    currentProject = project;
    currentCampaigns = campaignsPayload.items;
    currentDryRunLogs = dryRunLogsPayload.items;

    renderProjectHeader(project);
    renderSummary(summary);
    renderCampaigns(campaignsPayload.items);
    renderReviewQueue(reviewQueuePayload.items);
    renderProjectSources(projectSourcesPayload.items);
    renderLineage(summary.lineage_items);
    renderOpenAIDryRunHistory(dryRunLogsPayload.items);

    const runs = [];
    const candidates = [];

    for (const campaign of campaignsPayload.items) {
      const campaignBase = `${projectBase}/search-campaigns/${
        encodeURIComponent(campaign.search_campaign_id)
      }`;
      const runsPayload = await fetchJson(`${campaignBase}/runs`);
      if (loadToken !== detailLoadToken) {
        return false;
      }
      for (const run of runsPayload.items) {
        runs.push(run);
        const runBase = `${campaignBase}/runs/${encodeURIComponent(run.search_run_id)}`;
        const candidatesPayload = await fetchJson(`${runBase}/result-candidates`);
        if (loadToken !== detailLoadToken) {
          return false;
        }
        for (const candidate of candidatesPayload.items) {
          candidates.push(candidate);
        }
      }
    }

    currentRuns = runs;
    refreshCreateFormState();
    resetOpenAIDryRunPanel();
    renderRuns(runs);
    renderCandidates(candidates);
    setStatus("detail-status", `Loaded project ${project.title}.`, "success");
    return true;
  } catch (error) {
    if (loadToken !== detailLoadToken) {
      return false;
    }
    currentProject = null;
    setProjectDetailErrorState();
    setStatus("detail-status", error.message, "error");
    return false;
  } finally {
    if (loadToken === detailLoadToken) {
      setProjectInteractionDisabled(false);
      refreshCreateFormState(currentProject ? "ready" : "error");
    }
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
        return loadProjectDetailPage();
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
        return loadProjectDetailPage();
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
        return loadProjectDetailPage();
      },
    );
  }
};

const runOperatorAction = async (button, callback, successMessage) => {
  if (button.dataset.busy === "true") {
    return;
  }
  button.dataset.busy = "true";
  const originalLabel = button.textContent;
  button.textContent = "Working...";
  setProjectInteractionDisabled(true);
  setStatus("action-status", "Executing operator action...", "info");

  try {
    await callback();
    const reloaded = await loadProjectDetailPage();
    if (reloaded) {
      setStatus("action-status", successMessage, "success");
    } else {
      setStatus(
        "action-status",
        `${successMessage} Reload failed; see detail status.`,
        "error",
      );
    }
  } catch (error) {
    setStatus("action-status", error.message, "error");
  } finally {
    button.dataset.busy = "false";
    if (button.isConnected) {
      button.textContent = originalLabel;
    }
    setProjectInteractionDisabled(false);
    refreshCreateFormState(currentProject ? "ready" : "error");
  }
};

document.addEventListener("submit", async (event) => {
  const createForm = event.target.closest("form[data-create-form]");
  const openaiForm = event.target.closest("form[data-openai-form]");
  if (!createForm && !openaiForm) {
    return;
  }

  event.preventDefault();

  if (bootstrap.page === "project-detail" && openaiForm) {
    await handleProjectDetailOpenAISubmit(openaiForm);
    return;
  }

  if (bootstrap.page === "projects" && createForm) {
    await handleProjectsCreateSubmit(createForm);
    return;
  }
  if (bootstrap.page === "project-detail" && createForm) {
    await handleProjectDetailCreateSubmit(createForm);
  }
});

document.addEventListener("click", async (event) => {
  const button = event.target.closest("button[data-action]");
  if (!button) {
    return;
  }

  if (button.dataset.action === "reload-projects") {
    await loadProjectsPage();
    return;
  }

  if (button.dataset.action === "reload-project-detail") {
    await loadProjectDetailPage();
    return;
  }

  if (!bootstrap.projectId) {
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

CHAT_SCRIPT = """
const bootstrap = JSON.parse(
  document.getElementById("harbor-chat-bootstrap").textContent,
);
const apiBase = bootstrap.apiBase;
const preferredProjectId = new URLSearchParams(window.location.search).get(
  "project_id",
);
let chatProjects = [];
let chatSessions = [];
let chatHistory = [];
let chatBusy = false;
let currentSessionId = null;
let currentTurnId = null;
let lastFailedChatRequest = null;

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
    return "&mdash;";
  }
  return escapeHtml(value);
};

const setChatStatus = (text, kind = "info") => {
  const target = byId("chat-status");
  if (!target) {
    return;
  }
  target.textContent = text;
  target.classList.remove("info", "success", "error");
  target.classList.add(kind);
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

const chatProjectLabel = (projectId) => {
  const project = chatProjects.find((item) => item.project_id === projectId);
  if (!project) {
    return projectId || "Unknown project";
  }
  return project.title;
};

const formatDateTime = (value) => {
  if (!value) {
    return "";
  }
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return String(value);
  }
  return parsed.toLocaleString();
};

const setChatControlsDisabled = (disabled) => {
  const form = byId("chat-message-form");
  if (form) {
    for (const element of form.querySelectorAll("button, input, select, textarea")) {
      element.disabled = disabled;
    }
  }
  for (const element of document.querySelectorAll("button[data-chat-action]")) {
    element.disabled = disabled;
  }
};

const syncChatControls = () => {
  const hasProjects = chatProjects.length > 0;
  const hasHistory = chatHistory.length > 0;
  const projectSelect = byId("chat-project-id");
  const sessionSelect = byId("chat-session-id");
  const turnSelect = byId("chat-turn-id");
  const input = byId("chat-input-text");
  const sendButton = byId("chat-send-button");
  const newSessionButton = byId("chat-new-session-button");
  const reloadButton = byId("chat-reload-projects-button");
  const retryButton = byId("chat-retry-last-failed-button");

  if (projectSelect) {
    projectSelect.disabled = !hasProjects || chatBusy;
  }
  if (sessionSelect) {
    sessionSelect.disabled = !hasProjects || chatBusy;
  }
  if (turnSelect) {
    turnSelect.disabled = !hasHistory || chatBusy;
  }
  if (input) {
    input.disabled = !hasProjects || chatBusy;
  }
  if (sendButton) {
    sendButton.disabled = !hasProjects || chatBusy;
  }
  if (newSessionButton) {
    newSessionButton.disabled = !hasProjects || chatBusy;
  }
  if (reloadButton) {
    reloadButton.disabled = chatBusy;
  }
  if (retryButton) {
    retryButton.disabled = !lastFailedChatRequest || chatBusy;
  }
};

const renderProjectOptions = () => {
  const select = byId("chat-project-id");
  if (!select) {
    return;
  }
  select.innerHTML = "";

  if (!chatProjects.length) {
    const option = document.createElement("option");
    option.value = "";
    option.textContent = "No projects available";
    select.appendChild(option);
    select.value = "";
    return;
  }

  for (const project of chatProjects) {
    const option = document.createElement("option");
    option.value = project.project_id;
    option.textContent = `${project.title} (${project.project_id})`;
    select.appendChild(option);
  }

  const preferred = chatProjects.find(
    (project) => project.project_id === preferredProjectId,
  );
  if (preferred) {
    select.value = preferred.project_id;
    return;
  }
  select.value = chatProjects[0].project_id;
};

const sessionTitle = (session) => {
  const title = String(session?.title || "").trim();
  return title || "Untitled session";
};

const sessionStatus = (session) => {
  const status = String(session?.last_status || "").trim();
  return status || "pending";
};

const clearFailedChatRequest = () => {
  lastFailedChatRequest = null;
  renderChatRetryPanel();
};

const rememberFailedChatRequest = ({
  projectId,
  chatSessionId,
  inputText,
  errorMessage,
}) => {
  lastFailedChatRequest = {
    projectId,
    chatSessionId: chatSessionId || null,
    inputText,
    errorMessage,
    failedAt: new Date().toISOString(),
  };
  renderChatRetryPanel();
};

const renderChatRetryPanel = () => {
  const panel = byId("chat-retry-panel");
  const hint = byId("chat-retry-hint");
  const retryButton = byId("chat-retry-last-failed-button");
  if (!panel || !hint || !retryButton) {
    return;
  }

  if (!lastFailedChatRequest) {
    hint.textContent = "No failed message awaiting retry.";
    retryButton.disabled = true;
    panel.innerHTML = '<div class="empty">No failed message awaiting retry.</div>';
    return;
  }

  const failedAt = formatDateTime(lastFailedChatRequest.failedAt) || "—";
  const failedProjectLabel = chatProjectLabel(lastFailedChatRequest.projectId);
  const sessionLabel = lastFailedChatRequest.chatSessionId
    ? (chatSessions.find(
        (session) =>
          session.openai_project_chat_session_id === lastFailedChatRequest.chatSessionId,
      )
      ? sessionTitle(
          chatSessions.find(
            (session) =>
              session.openai_project_chat_session_id ===
              lastFailedChatRequest.chatSessionId,
          ),
        )
      : lastFailedChatRequest.chatSessionId)
    : "New session";

  hint.textContent = (
    "Last failed message is preserved in the composer. " +
    "Retry or edit and send manually."
  );
  retryButton.disabled = chatBusy;
  panel.innerHTML = `
    <div class="response-grid">
      <div class="response-card">
        <div class="response-label">Project</div>
        <div class="response-value">${safeText(failedProjectLabel)}</div>
      </div>
      <div class="response-card">
        <div class="response-label">Session</div>
        <div class="response-value">${safeText(sessionLabel)}</div>
      </div>
      <div class="response-card">
        <div class="response-label">Failed at</div>
        <div class="response-value">${safeText(failedAt)}</div>
      </div>
    </div>
    <div class="chat-turn-detail">
      <div class="response-label">Failure detail</div>
      <pre class="response-pre">${safeText(lastFailedChatRequest.errorMessage)}</pre>
    </div>
    <div class="chat-turn-detail">
      <div class="response-label">Retry message</div>
      <pre class="response-pre">${safeText(lastFailedChatRequest.inputText)}</pre>
    </div>
  `;
};

const renderSessionSummary = () => {
  const summary = byId("chat-session-summary");
  const detail = byId("chat-session-meta");
  if (!summary || !detail) {
    return;
  }

  if (!currentSessionId) {
    summary.innerHTML = `
      <div class="response-card">
        <div class="response-label">Session</div>
        <div class="response-value">New session</div>
      </div>
      <div class="response-card">
        <div class="response-label">Status</div>
        <div class="response-value">Not persisted</div>
      </div>
      <div class="response-card">
        <div class="response-label">Turns</div>
        <div class="response-value">0</div>
      </div>
      <div class="response-card">
        <div class="response-label">Updated</div>
        <div class="response-value">&mdash;</div>
      </div>
    `;
    detail.innerHTML = [
      '<div class="empty">',
      'New session not yet persisted. Send a message to create it.',
      '</div>',
    ].join("");
    return;
  }

  const session = chatSessions.find(
    (item) => item.openai_project_chat_session_id === currentSessionId,
  );
  if (!session) {
    summary.innerHTML = `
      <div class="response-card">
        <div class="response-label">Session</div>
        <div class="response-value">Unavailable</div>
      </div>
    `;
    detail.innerHTML = '<div class="empty">Persisted session could not be resolved.</div>';
    return;
  }

  const updatedAt = formatDateTime(session.updated_at) || "—";
  const createdAt = formatDateTime(session.created_at) || "—";
  const title = sessionTitle(session);
  const status = sessionStatus(session);
  const turnCount = session.turn_count ?? 0;
  const lastModel = session.last_model || "—";
  const lastInput = session.last_input_text || "—";

  summary.innerHTML = `
    <div class="response-card">
      <div class="response-label">Session</div>
      <div class="response-value">${safeText(title)}</div>
    </div>
    <div class="response-card">
      <div class="response-label">Status</div>
      <div class="response-value">${safeText(status)}</div>
    </div>
    <div class="response-card">
      <div class="response-label">Turns</div>
      <div class="response-value">${safeText(turnCount)}</div>
    </div>
    <div class="response-card">
      <div class="response-label">Updated</div>
      <div class="response-value">${safeText(updatedAt)}</div>
    </div>
  `;
  detail.innerHTML = `
    <div class="chat-session-meta-row">
      <span class="response-label">Created</span>
      <span class="response-value">${safeText(createdAt)}</span>
    </div>
    <div class="chat-session-meta-row">
      <span class="response-label">Last model</span>
      <span class="response-value">${safeText(lastModel)}</span>
    </div>
    <div class="chat-session-meta-row">
      <span class="response-label">Last operator message</span>
      <span class="response-value">${safeText(lastInput)}</span>
    </div>
  `;
};

const renderTurnInspectorOptions = (preferredTurnId = null) => {
  const select = byId("chat-turn-id");
  if (!select) {
    return;
  }
  select.innerHTML = "";

  if (!chatHistory.length) {
    const option = document.createElement("option");
    option.value = "";
    option.textContent = "No persisted turns";
    select.appendChild(option);
    select.value = "";
    currentTurnId = null;
    return;
  }

  for (const turn of chatHistory) {
    const option = document.createElement("option");
    option.value = turn.openai_project_chat_turn_id;
    option.textContent = `Turn ${turn.turn_index} · ${formatDateTime(turn.created_at)}`;
    select.appendChild(option);
  }

  const preferred = chatHistory.find(
    (turn) => turn.openai_project_chat_turn_id === preferredTurnId,
  );
  const selectedTurn = preferred || chatHistory[chatHistory.length - 1];
  select.value = selectedTurn.openai_project_chat_turn_id;
  currentTurnId = selectedTurn.openai_project_chat_turn_id;
};

const clearChatTurnInspector = (text) => {
  const summary = byId("chat-turn-summary");
  const detail = byId("chat-turn-inspector");
  renderTurnInspectorOptions();
  if (summary) {
    summary.innerHTML = `
      <div class="response-card">
        <div class="response-label">Selected turn</div>
        <div class="response-value">&mdash;</div>
      </div>
    `;
  }
  if (detail) {
    detail.innerHTML = `<div class="empty">${safeText(text)}</div>`;
  }
};

const renderChatTurnInspector = () => {
  const summary = byId("chat-turn-summary");
  const detail = byId("chat-turn-inspector");
  if (!summary || !detail) {
    return;
  }

  const turn = chatHistory.find(
    (item) => item.openai_project_chat_turn_id === currentTurnId,
  );
  if (!turn) {
    clearChatTurnInspector("No persisted turn selected.");
    renderSessionSummary();
    return;
  }

  const assistantText = turn.output_text || turn.error_message || "No output.";
  summary.innerHTML = `
    <div class="response-card">
      <div class="response-label">Selected turn</div>
      <div class="response-value">${safeText(turn.turn_index)}</div>
    </div>
    <div class="response-card">
      <div class="response-label">Status</div>
      <div class="response-value">${safeText(turn.status)}</div>
    </div>
    <div class="response-card">
      <div class="response-label">Model</div>
      <div class="response-value">${safeText(turn.model)}</div>
    </div>
    <div class="response-card">
      <div class="response-label">Response ID</div>
      <div class="response-value">${safeText(turn.response_id)}</div>
    </div>
  `;
  detail.innerHTML = `
    <div class="chat-turn-detail">
      <div class="response-label">Created</div>
      <div class="response-value">${safeText(formatDateTime(turn.created_at))}</div>
    </div>
    <div class="chat-turn-detail">
      <div class="response-label">Rendered Harbor input</div>
      <pre class="response-pre">${safeText(turn.rendered_input_text)}</pre>
    </div>
    <div class="chat-turn-detail">
      <div class="response-label">Persisted operator message</div>
      <pre class="response-pre">${safeText(turn.request_input_text)}</pre>
    </div>
    <div class="chat-turn-detail">
      <div class="response-label">Persisted assistant output</div>
      <pre class="response-pre">${safeText(assistantText)}</pre>
    </div>
  `;
};

const renderSessionOptions = (preferredSessionId = null) => {
  const select = byId("chat-session-id");
  if (!select) {
    return;
  }
  select.innerHTML = "";

  const newOption = document.createElement("option");
  newOption.value = "";
  newOption.textContent = "Start new session";
  select.appendChild(newOption);

  for (const session of chatSessions) {
    const option = document.createElement("option");
    option.value = session.openai_project_chat_session_id;
    option.textContent = [
      sessionTitle(session),
      `${session.turn_count} turn(s)`,
      sessionStatus(session),
    ].join(" · ");
    select.appendChild(option);
  }

  const preferred = chatSessions.find(
    (session) => session.openai_project_chat_session_id === preferredSessionId,
  );
  if (preferred) {
    select.value = preferred.openai_project_chat_session_id;
    currentSessionId = preferred.openai_project_chat_session_id;
    renderSessionSummary();
    return;
  }
  select.value = "";
  currentSessionId = null;
  renderSessionSummary();
};

const renderChatHistory = () => {
  const target = byId("chat-history");
  if (!target) {
    return;
  }
  if (!chatHistory.length) {
    target.innerHTML = '<div class="empty">No persisted turns yet.</div>';
    clearChatTurnInspector("No persisted turn selected.");
    return;
  }

  const fragments = [];
  for (const turn of chatHistory) {
    const turnLabel = `Turn ${turn.turn_index}`;
    const userMeta = [
      `Project: ${chatProjectLabel(turn.project_id)}`,
      turnLabel,
      formatDateTime(turn.created_at),
    ].filter(Boolean);
    fragments.push(`
      <article class="chat-message user">
        <div class="chat-message-header">
          <div class="chat-role">Operator</div>
          <div class="chat-meta">${safeText(userMeta.join(" · "))}</div>
        </div>
        <pre class="response-pre chat-message-text">${safeText(turn.request_input_text)}</pre>
      </article>
    `);

    const assistantText = turn.output_text || turn.error_message || "No output.";
    const assistantRole = turn.status === "completed" ? "Assistant" : "Error";
    const assistantClass = turn.status === "completed" ? "assistant" : "error";
    const assistantMeta = [
      turnLabel,
      turn.provider ? `Provider: ${turn.provider}` : "",
      turn.model ? `Model: ${turn.model}` : "",
      turn.status ? `Status: ${turn.status}` : "",
      turn.response_id ? `Response: ${turn.response_id}` : "",
    ].filter(Boolean);
    fragments.push(`
      <article class="chat-message ${assistantClass}">
        <div class="chat-message-header">
          <div class="chat-role">${safeText(assistantRole)}</div>
          <div class="chat-meta">${safeText(assistantMeta.join(" · "))}</div>
        </div>
        <pre class="response-pre chat-message-text">${safeText(assistantText)}</pre>
      </article>
    `);
  }

  target.innerHTML = fragments.join("");
};

const clearChatHistory = (text) => {
  chatHistory = [];
  currentTurnId = null;
  const target = byId("chat-history");
  if (!target) {
    return;
  }
  target.innerHTML = `<div class="empty">${safeText(text)}</div>`;
  clearChatTurnInspector("No persisted turn selected.");
  renderSessionSummary();
};

const selectedProjectId = () => String(byId("chat-project-id")?.value || "").trim();

const persistChatTurn = async ({ projectId, inputText, chatSessionId }) => {
  return postJson(
    `${apiBase}/openai/projects/${encodeURIComponent(projectId)}/chat-turns`,
    {
      input_text: inputText,
      chat_session_id: chatSessionId,
    },
  );
};

const retryFailedChatMessage = async () => {
  if (chatBusy || !lastFailedChatRequest) {
    return;
  }

  const failedRequest = { ...lastFailedChatRequest };
  const input = byId("chat-input-text");
  if (input) {
    input.value = failedRequest.inputText;
  }

  chatBusy = true;
  syncChatControls();
  setChatStatus("Retrying failed Harbor chat turn...", "info");

  try {
    const payload = await persistChatTurn({
      projectId: failedRequest.projectId,
      inputText: failedRequest.inputText,
      chatSessionId: failedRequest.chatSessionId,
    });

    currentSessionId = payload.session.openai_project_chat_session_id;
    await loadChatSessions(failedRequest.projectId, currentSessionId);
    if (input) {
      input.value = "";
    }
    clearFailedChatRequest();
    setChatStatus("Failed chat turn retried successfully.", "success");
  } catch (error) {
    rememberFailedChatRequest({
      projectId: failedRequest.projectId,
      chatSessionId: failedRequest.chatSessionId,
      inputText: failedRequest.inputText,
      errorMessage: error.message,
    });
    setChatStatus(`Retry failed: ${error.message}`, "error");
  } finally {
    chatBusy = false;
    syncChatControls();
  }
};

const loadChatTurns = async (projectId, chatSessionId) => {
  if (!chatSessionId) {
    clearChatHistory("No persisted turns yet. Start a new session.");
    return;
  }

  const payload = await fetchJson(
    `${apiBase}/openai/projects/${encodeURIComponent(projectId)}` +
      `/chat-sessions/${encodeURIComponent(chatSessionId)}/turns`,
  );
  chatHistory = Array.isArray(payload.items) ? payload.items : [];
  renderTurnInspectorOptions(currentTurnId);
  renderChatHistory();
  renderChatTurnInspector();
};

const loadChatSessions = async (projectId, preferredSessionId = null) => {
  chatSessions = [];
  currentTurnId = null;
  renderSessionOptions();
  clearChatHistory("Loading session history...");
  setChatStatus("Loading persisted chat sessions...", "info");

  const payload = await fetchJson(
    `${apiBase}/openai/projects/${encodeURIComponent(projectId)}/chat-sessions`,
  );
  chatSessions = Array.isArray(payload.items) ? payload.items : [];
  renderSessionOptions(preferredSessionId);

  if (currentSessionId) {
    await loadChatTurns(projectId, currentSessionId);
    setChatStatus("Loaded persisted chat session history.", "success");
    return;
  }

  clearChatHistory("No persisted turns yet. Start a new session.");
  renderSessionSummary();
  setChatStatus(
    "Ready. Start a new chat session or continue a persisted one.",
    "success",
  );
};

const loadChatProjects = async () => {
  setChatControlsDisabled(true);
  setChatStatus("Loading Harbor projects...", "info");
  try {
    const payload = await fetchJson(`${apiBase}/projects`);
    chatProjects = Array.isArray(payload.items) ? payload.items : [];
    renderProjectOptions();

    if (!chatProjects.length) {
      chatSessions = [];
      clearFailedChatRequest();
      renderSessionOptions();
      clearChatHistory("No projects available.");
      setChatStatus(
        "No Harbor projects available. Create one first in the operator shell.",
        "error",
      );
      return;
    }

    await loadChatSessions(selectedProjectId(), currentSessionId);
    if (lastFailedChatRequest && selectedProjectId() !== lastFailedChatRequest.projectId) {
      clearFailedChatRequest();
    } else {
      renderChatRetryPanel();
    }
    renderSessionSummary();
  } catch (error) {
    clearFailedChatRequest();
    setChatStatus(error.message, "error");
    clearChatHistory("Load failed.");
  } finally {
    setChatControlsDisabled(false);
    syncChatControls();
  }
};

const startNewChatSession = () => {
  currentSessionId = null;
  currentTurnId = null;
  clearFailedChatRequest();
  renderSessionOptions();
  clearChatHistory("New session not yet persisted. Send a message to start it.");
  renderSessionSummary();
  setChatStatus("New chat session armed.", "info");
  syncChatControls();
};

const submitChatMessage = async (event) => {
  event.preventDefault();
  if (chatBusy) {
    return;
  }

  const projectId = selectedProjectId();
  const inputText = String(byId("chat-input-text")?.value || "").trim();

  if (!projectId) {
    setChatStatus("Select a project first.", "error");
    return;
  }
  if (!inputText) {
    setChatStatus("Enter a message first.", "error");
    return;
  }

  chatBusy = true;
  syncChatControls();
  setChatStatus("Persisting chat turn through Harbor...", "info");

  try {
    const payload = await persistChatTurn({
      projectId,
      inputText,
      chatSessionId: currentSessionId,
    });

    currentSessionId = payload.session.openai_project_chat_session_id;
    await loadChatSessions(projectId, currentSessionId);
    byId("chat-input-text").value = "";
    clearFailedChatRequest();
    setChatStatus("Chat turn persisted to Harbor session history.", "success");
  } catch (error) {
    rememberFailedChatRequest({
      projectId,
      chatSessionId: currentSessionId,
      inputText,
      errorMessage: error.message,
    });
    setChatStatus(
      `Chat turn failed: ${error.message}. Message preserved for retry.`,
      "error",
    );
  } finally {
    chatBusy = false;
    syncChatControls();
  }
};

document.addEventListener("click", async (event) => {
  const button = event.target.closest("button[data-chat-action]");
  if (!button) {
    return;
  }
  if (button.dataset.chatAction === "reload-projects") {
    await loadChatProjects();
  }
  if (button.dataset.chatAction === "new-session") {
    startNewChatSession();
  }
  if (button.dataset.chatAction === "retry-last-failed") {
    await retryFailedChatMessage();
  }
});

document.addEventListener("change", async (event) => {
  const projectSelect = event.target.closest("#chat-project-id");
  if (projectSelect) {
    currentSessionId = null;
    clearFailedChatRequest();
    await loadChatSessions(selectedProjectId());
    return;
  }

  const sessionSelect = event.target.closest("#chat-session-id");
  if (sessionSelect) {
    currentSessionId = String(sessionSelect.value || "").trim() || null;
    currentTurnId = null;
    clearFailedChatRequest();
    if (currentSessionId) {
      await loadChatTurns(selectedProjectId(), currentSessionId);
      renderSessionSummary();
      setChatStatus("Loaded persisted chat session history.", "success");
      return;
    }
    clearChatHistory("New session not yet persisted. Send a message to start it.");
    renderSessionSummary();
    setChatStatus("New chat session armed.", "info");
    return;
  }

  const turnSelect = event.target.closest("#chat-turn-id");
  if (turnSelect) {
    currentTurnId = String(turnSelect.value || "").trim() || null;
    renderChatTurnInspector();
  }
});

document.addEventListener("submit", async (event) => {
  const form = event.target.closest("form[data-chat-form]");
  if (!form) {
    return;
  }
  if (form.dataset.chatForm === "persisted-chat") {
    await submitChatMessage(event);
  }
});

clearChatHistory("Loading Harbor projects...");
renderChatRetryPanel();
loadChatProjects();
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
    <script>{CHAT_SCRIPT}</script>
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
    <h2>Message</h2>
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
      <div class="form-field">
        <label class="form-label" for="chat-input-text">Message</label>
        <textarea
          id="chat-input-text"
          name="input_text"
          required
          disabled
          placeholder="Ask Harbor for a compact project-specific response."
        ></textarea>
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
    <h2>Persisted Session History</h2>
    <div id="chat-history" class="chat-history" data-chat-history="persisted-chat">
      <div class="empty">No persisted turns yet.</div>
    </div>
  </section>

  <section class="section-card">
    <h2>Selected Turn Context</h2>
    <p class="action-note">
      Inspect the exact Harbor-rendered input and persisted output for a selected
      turn.
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
