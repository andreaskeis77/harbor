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

const TOAST_CONTAINER_ID = "harbor-toasts";
const TOAST_MAX_VISIBLE = 5;
const TOAST_KIND_DURATIONS_MS = {
  info: 2500,
  success: 4000,
  error: 7000,
};

const showToast = (text, options = {}) => {
  const container = byId(TOAST_CONTAINER_ID);
  if (!container) {
    return;
  }
  const kind = options.kind && TOAST_KIND_DURATIONS_MS[options.kind]
    ? options.kind
    : "info";
  const duration = typeof options.duration === "number" && options.duration > 0
    ? options.duration
    : TOAST_KIND_DURATIONS_MS[kind];
  const message = text === null || text === undefined ? "" : String(text);

  while (container.children.length >= TOAST_MAX_VISIBLE) {
    container.removeChild(container.firstElementChild);
  }

  const item = document.createElement("li");
  item.className = `harbor-toast harbor-toast-${kind}`;
  item.setAttribute("role", kind === "error" ? "alert" : "status");
  item.dataset.toastKind = kind;
  item.textContent = message;
  container.appendChild(item);

  window.setTimeout(() => {
    if (item.isConnected) {
      item.classList.add("harbor-toast-dismissing");
      window.setTimeout(() => {
        if (item.isConnected) {
          item.remove();
        }
      }, 300);
    }
  }, duration);
};

const setStatus = (_id, text, kind = "info") => {
  showToast(text, { kind });
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
  setTableBodyMessage("project-sources-table-body", 7, "Loading...");
  setTableBodyMessage("handbook-versions-table-body", 4, "Loading...");
  setTableBodyMessage("lineage-table-body", 6, "Loading...");
  setTableBodyMessage("openai-dry-run-history-body", 6, "Loading...");
  setTableBodyMessage("automation-tasks-table-body", 6, "Loading...");
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
  setTableBodyMessage("project-sources-table-body", 7, "Load failed.");
  setTableBodyMessage("handbook-versions-table-body", 4, "Load failed.");
  setTableBodyMessage("lineage-table-body", 6, "Load failed.");
  setTableBodyMessage("openai-dry-run-history-body", 6, "Load failed.");
  setTableBodyMessage("automation-tasks-table-body", 6, "Load failed.");
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

const renderProjectSourceActions = (item) => {
  const id = encodeURIComponent(item.project_source_id);
  const status = item.review_status;
  const buttons = [];
  if (status !== "accepted") {
    buttons.push(
      `<button type="button" class="source-review-action"` +
        ` data-action="source-review-update"` +
        ` data-project-source-id="${id}" data-target-status="accepted">` +
        `Accept</button>`,
    );
  }
  if (status !== "rejected") {
    buttons.push(
      `<button type="button" class="source-review-action"` +
        ` data-action="source-review-update"` +
        ` data-project-source-id="${id}" data-target-status="rejected">` +
        `Reject</button>`,
    );
  }
  if (status !== "candidate") {
    buttons.push(
      `<button type="button" class="source-review-action"` +
        ` data-action="source-review-update"` +
        ` data-project-source-id="${id}" data-target-status="candidate">` +
        `Reset</button>`,
    );
  }
  return buttons.join(" ");
};

const renderProjectSources = (items) => {
  const body = byId("project-sources-table-body");
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
        <tr data-project-source-id="${encodeURIComponent(item.project_source_id)}">
          <td>${safeText(item.source.title)}</td>
          <td>${badge(item.review_status)}</td>
          <td>${safeText(item.relevance)}</td>
          <td>${safeText(item.source.trust_tier)}</td>
          <td>${inlineCode(item.project_source_id)}</td>
          <td>${safeText(item.source.canonical_url)}</td>
          <td class="source-review-actions">${renderProjectSourceActions(item)}</td>
        </tr>
      `,
    )
    .join("");
};

const renderHandbookVersions = (items) => {
  const body = byId("handbook-versions-table-body");
  if (!body) {
    return;
  }
  if (!items.length) {
    body.innerHTML = emptyRow(4);
    return;
  }
  body.innerHTML = items
    .map(
      (item) => `
        <tr data-handbook-version-id="${encodeURIComponent(item.handbook_version_id)}">
          <td>v${safeText(item.version_number)}</td>
          <td>${formatTimestamp(item.created_at)}</td>
          <td>${item.change_note ? safeText(item.change_note) : textFallback}</td>
          <td>
            <details class="handbook-version-details">
              <summary>View markdown (${safeText(item.handbook_markdown.length)} chars)</summary>
              <pre class="handbook-version-markdown">${safeText(item.handbook_markdown)}</pre>
            </details>
          </td>
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

const renderAutomationTasks = (items) => {
  const body = byId("automation-tasks-table-body");
  if (!body) {
    return;
  }
  if (!items.length) {
    body.innerHTML = emptyRow(6, "No automation tasks yet.");
    return;
  }
  body.innerHTML = items
    .map((item) => {
      const detail = item.error_message || item.result_summary || "";
      return `
        <tr data-automation-task-id="${encodeURIComponent(item.automation_task_id)}">
          <td>${safeText(item.task_kind)}</td>
          <td>${safeText(item.trigger_source)}</td>
          <td>
            <span class="badge automation-task-status-${escapeHtml(item.status)}"
                  data-automation-task-status="${escapeHtml(item.status)}">
              ${safeText(item.status)}
            </span>
          </td>
          <td>${formatDateTime(item.started_at)}</td>
          <td>${formatDateTime(item.completed_at)}</td>
          <td>${detail ? safeText(detail) : textFallback}</td>
        </tr>
      `;
    })
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
    const handbookVersionsPromise = fetchJson(`${projectBase}/handbook/versions`);
    const dryRunLogsPromise = fetchJson(
      `${apiBase}/openai/projects/${encodeURIComponent(projectId)}/dry-run-logs`,
    );
    const automationTasksPromise = fetchJson(`${projectBase}/automation-tasks`);

    const [
      project,
      summary,
      campaignsPayload,
      reviewQueuePayload,
      projectSourcesPayload,
      handbookVersionsPayload,
      dryRunLogsPayload,
      automationTasksPayload,
    ] = await Promise.all([
      projectPromise,
      summaryPromise,
      campaignsPromise,
      reviewQueuePromise,
      projectSourcesPromise,
      handbookVersionsPromise,
      dryRunLogsPromise,
      automationTasksPromise,
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
    renderHandbookVersions(handbookVersionsPayload.items);
    renderLineage(summary.lineage_items);
    renderOpenAIDryRunHistory(dryRunLogsPayload.items);
    renderAutomationTasks(automationTasksPayload.items);

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
    return;
  }

  if (button.dataset.action === "source-review-update") {
    const projectSourceId = button.dataset.projectSourceId;
    const targetStatus = button.dataset.targetStatus;
    if (!projectSourceId || !targetStatus) {
      return;
    }
    const url = `${projectBase}/sources/${projectSourceId}/review-status`;
    const row = button.closest("tr");
    const peers = row
      ? row.querySelectorAll("button[data-action=\\"source-review-update\\"]")
      : [button];
    peers.forEach((b) => {
      b.disabled = true;
    });
    try {
      const response = await fetch(url, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ review_status: targetStatus }),
      });
      if (!response.ok) {
        const err = await response.json().catch(() => ({}));
        throw new Error(err.detail || `HTTP ${response.status}`);
      }
      await loadProjectDetailPage();
    } catch (err) {
      setStatus(
        "detail-status",
        `Review status update failed: ${String(err.message || err)}`,
        "error",
      );
      peers.forEach((b) => {
        b.disabled = false;
      });
    }
  }
});

const SECTION_STORAGE_PREFIX = "harbor.operator.section.";

const initSectionCollapsibles = () => {
  const sections = document.querySelectorAll(
    "section.section-card[data-section-key]",
  );
  sections.forEach((section) => {
    const key = section.getAttribute("data-section-key");
    const storageKey = `${SECTION_STORAGE_PREFIX}${key}`;
    let stored = null;
    try {
      stored = window.localStorage.getItem(storageKey);
    } catch (err) {
      stored = null;
    }
    if (stored === "collapsed") {
      section.classList.add("is-collapsed");
    }
    const heading = section.querySelector(":scope > h2");
    if (!heading) {
      return;
    }
    heading.addEventListener("click", () => {
      const collapsed = section.classList.toggle("is-collapsed");
      try {
        window.localStorage.setItem(
          storageKey,
          collapsed ? "collapsed" : "expanded",
        );
      } catch (err) {
        /* storage unavailable — state is still toggled in-memory */
      }
    });
  });
};

const renderPendingActionsTable = (items) => {
  const body = byId("pending-actions-table-body");
  if (!body) {
    return;
  }
  if (!items.length) {
    body.innerHTML = emptyRow(6, "No open review-queue items across projects.");
    return;
  }
  body.innerHTML = items
    .map((item) => {
      const projectLink = (
        `<a href="/operator/projects/${escapeHtml(item.project_id)}">` +
        `${safeText(item.project_title)}</a>`
      );
      return (
        `<tr data-pending-action-id="${escapeHtml(item.review_queue_item_id)}">` +
        `<td>${projectLink}</td>` +
        `<td>${safeText(item.title)}</td>` +
        `<td>${safeText(item.queue_kind)}</td>` +
        `<td>${safeText(item.priority)}</td>` +
        `<td>${formatDateTime(item.created_at)}</td>` +
        `<td>${formatDateTime(item.updated_at)}</td>` +
        "</tr>"
      );
    })
    .join("");
};

const loadPendingActionsPage = async () => {
  const body = byId("pending-actions-table-body");
  if (body) {
    body.innerHTML = emptyRow(6, "Loading...");
  }
  try {
    const payload = await fetchJson(`${apiBase}/pending-actions`);
    renderPendingActionsTable(payload.items || []);
    showToast(`${(payload.items || []).length} pending action(s) loaded.`, {
      kind: "success",
    });
  } catch (error) {
    if (body) {
      body.innerHTML = emptyRow(6, "Load failed.");
    }
    showToast(error.message, { kind: "error" });
  }
};

const reloadPendingActionsButton = byId("pending-actions-reload-button");
if (reloadPendingActionsButton) {
  reloadPendingActionsButton.addEventListener("click", loadPendingActionsPage);
}

initSectionCollapsibles();

if (bootstrap.page === "projects") {
  loadProjectsPage();
}
if (bootstrap.page === "project-detail") {
  loadProjectDetailPage();
}
if (bootstrap.page === "pending-actions") {
  loadPendingActionsPage();
}
