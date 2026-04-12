const bootstrap = JSON.parse(
  document.getElementById("harbor-chat-bootstrap").textContent,
);
const apiBase = bootstrap.apiBase;
const preferredProjectId = new URLSearchParams(window.location.search).get(
  "project_id",
);
const chatDefaultInstructions = String(
  bootstrap.chatDefaultInstructions || "",
).trim();
const CHAT_DEFAULT_PRESET_KEY = "__default__";
const CHAT_CUSTOM_PRESET_KEY = "__custom__";
const chatInstructionPresets = Array.isArray(bootstrap.chatInstructionPresets)
  ? bootstrap.chatInstructionPresets
  : [];
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

const compactWhitespace = (value) => {
  return String(value ?? "")
    .replace(/\\s+/g, " ")
    .trim();
};

const previewText = (value, maxLength = 220) => {
  const normalized = compactWhitespace(value);
  if (!normalized) {
    return "No content.";
  }
  if (normalized.length <= maxLength) {
    return normalized;
  }
  return `${normalized.slice(0, maxLength - 15)} …[truncated]`;
};

const textLength = (value) => {
  return String(value ?? "").trim().length;
};

const lineCount = (value) => {
  const text = String(value ?? "").trim();
  if (!text) {
    return 0;
  }
  return text.split("\n").length;
};

const formatDelta = (current, baseline) => {
  const delta = current - baseline;
  if (delta === 0) {
    return "0";
  }
  return `${delta > 0 ? "+" : ""}${String(delta)}`;
};

const shouldCollapseText = (value, collapseLimit = 280) => {
  const text = String(value ?? "");
  const normalized = compactWhitespace(text);
  return (
    normalized.length > collapseLimit ||
    text.split("\n").length > 6 ||
    text.includes("\n\n")
  );
};

const renderCollapsibleTextBlock = (
  label,
  value,
  { collapseLimit = 280, openByDefault = false, sourceAttribution = null } = {},
) => {
  const text = String(value ?? "").trim();
  if (!text) {
    return `
      <div class="chat-message-body">
        <p class="chat-message-preview">No content.</p>
      </div>
    `;
  }

  const rendered = sourceAttribution
    ? renderCitedText(text, sourceAttribution)
    : safeText(text);

  if (!shouldCollapseText(text, collapseLimit)) {
    return `
      <div class="chat-message-body">
        <p class="chat-message-preview">${safeText(label)}</p>
        <pre class="response-pre chat-message-text">${rendered}</pre>
      </div>
    `;
  }

  return `
    <details class="chat-collapsible" data-chat-collapsible="chat-content"${
      openByDefault ? " open" : ""
    }>
      <summary>
        <span class="chat-collapsible-summary">
          <span class="chat-collapsible-label">${safeText(label)}</span>
          <span class="chat-collapsible-preview">${safeText(
            previewText(text, 220),
          )}</span>
        </span>
      </summary>
      <div class="chat-collapsible-body">
        <pre class="response-pre chat-message-text">${rendered}</pre>
      </div>
    </details>
  `;
};

const renderCitedText = (text, sourceAttribution) => {
  const safe = safeText(text);
  if (!Array.isArray(sourceAttribution) || !sourceAttribution.length) {
    return safe;
  }
  return safe.replace(/\\[(\\d+)]/g, (match, num) => {
    const index = parseInt(num, 10);
    if (index >= 1 && index <= sourceAttribution.length) {
      const source = sourceAttribution[index - 1];
      const title = safeText(source.title || `Source ${index}`);
      return `<span class="citation-ref" title="${title}">[${index}]</span>`;
    }
    return match;
  });
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
  const instructions = byId("chat-instructions-text");
  const sendButton = byId("chat-send-button");
  const newSessionButton = byId("chat-new-session-button");
  const reloadButton = byId("chat-reload-projects-button");
  const retryButton = byId("chat-retry-last-failed-button");
  const clearInstructionsButton = byId("chat-clear-instructions-button");
  const presetSelect = byId("chat-instructions-preset");
  const applyPresetButton = byId("chat-apply-instructions-preset-button");

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
  if (instructions) {
    instructions.disabled = !hasProjects || chatBusy;
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
  if (clearInstructionsButton) {
    clearInstructionsButton.disabled = !hasProjects || chatBusy;
  }
  if (presetSelect) {
    presetSelect.disabled = !hasProjects || chatBusy;
  }
  if (applyPresetButton) {
    const presetKey = String(presetSelect?.value || CHAT_DEFAULT_PRESET_KEY);
    applyPresetButton.disabled = !hasProjects || chatBusy || presetKey === CHAT_CUSTOM_PRESET_KEY;
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

const matchedInstructionPreset = (instructions) => {
  if (!instructions) {
    return null;
  }
  return chatInstructionPresets.find((preset) => preset.value === instructions) || null;
};

const renderDefaultInstructionsPreview = () => {
  const target = byId("chat-default-instructions-text");
  if (!target) {
    return;
  }
  target.textContent = chatDefaultInstructions || "Harbor default instructions unavailable.";
};

const renderInstructionPresetOptions = () => {
  const select = byId("chat-instructions-preset");
  if (!select) {
    return;
  }

  select.innerHTML = "";

  const defaultOption = document.createElement("option");
  defaultOption.value = CHAT_DEFAULT_PRESET_KEY;
  defaultOption.textContent = "Harbor default instructions";
  select.appendChild(defaultOption);

  for (const preset of chatInstructionPresets) {
    const option = document.createElement("option");
    option.value = preset.key;
    option.textContent = preset.label;
    select.appendChild(option);
  }

  const customOption = document.createElement("option");
  customOption.value = CHAT_CUSTOM_PRESET_KEY;
  customOption.textContent = "Custom current text";
  select.appendChild(customOption);
};

const applyInstructionPreset = (presetKey) => {
  const instructions = byId("chat-instructions-text");
  const presetSelect = byId("chat-instructions-preset");
  if (!instructions || !presetSelect) {
    return;
  }

  if (presetKey === CHAT_DEFAULT_PRESET_KEY) {
    instructions.value = "";
    presetSelect.value = CHAT_DEFAULT_PRESET_KEY;
    renderInstructionsState();
    return;
  }

  const preset = chatInstructionPresets.find((item) => item.key === presetKey);
  if (!preset) {
    return;
  }

  instructions.value = preset.value;
  presetSelect.value = preset.key;
  renderInstructionsState();
};

const clearFailedChatRequest = () => {
  lastFailedChatRequest = null;
  renderChatRetryPanel();
};

const rememberFailedChatRequest = ({
  projectId,
  chatSessionId,
  inputText,
  instructions,
  errorMessage,
}) => {
  lastFailedChatRequest = {
    projectId,
    chatSessionId: chatSessionId || null,
    inputText,
    instructions: instructions || null,
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
    <div class="chat-turn-detail">
      <div class="response-label">Retry instructions</div>
      <pre class="response-pre">${safeText(
        lastFailedChatRequest.instructions || "Harbor default instructions"
      )}</pre>
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
  const compare = byId("chat-turn-compare-grid");
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
  if (compare) {
    compare.innerHTML = `
      <div class="response-card">
        <div class="response-label">Comparison</div>
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
  const compare = byId("chat-turn-compare-grid");
  const detail = byId("chat-turn-inspector");
  if (!summary || !compare || !detail) {
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

  const operatorText = String(turn.request_input_text || "").trim();
  const renderedText = String(turn.rendered_input_text || "").trim();
  const assistantText = String(
    turn.output_text || turn.error_message || "No output.",
  ).trim();
  const operatorChars = textLength(operatorText);
  const renderedChars = textLength(renderedText);
  const assistantChars = textLength(assistantText);
  const operatorLines = lineCount(operatorText);
  const renderedLines = lineCount(renderedText);
  const assistantLines = lineCount(assistantText);

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
  compare.innerHTML = `
    <div class="response-card">
      <div class="response-label">Operator chars</div>
      <div class="response-value">${safeText(operatorChars)}</div>
    </div>
    <div class="response-card">
      <div class="response-label">Rendered input chars</div>
      <div class="response-value">${safeText(renderedChars)}</div>
    </div>
    <div class="response-card">
      <div class="response-label">Assistant output chars</div>
      <div class="response-value">${safeText(assistantChars)}</div>
    </div>
    <div class="response-card">
      <div class="response-label">Input → rendered delta</div>
      <div class="response-value">${safeText(formatDelta(renderedChars, operatorChars))}</div>
    </div>
    <div class="response-card">
      <div class="response-label">Rendered → output delta</div>
      <div class="response-value">${safeText(formatDelta(assistantChars, renderedChars))}</div>
    </div>
    <div class="response-card">
      <div class="response-label">Line counts</div>
      <div class="response-value">${safeText(
        `${operatorLines} / ${renderedLines} / ${assistantLines}`,
      )}</div>
    </div>
  `;
  const inspectorSources = Array.isArray(turn.source_attribution) ? turn.source_attribution : [];
  const sourceDetailHtml = inspectorSources.length
    ? inspectorSources.map((s, i) => `
        <div class="chat-source-attribution-item">
          <div class="chat-source-attribution-title">${safeText(`${i + 1}. ${s.title}`)}</div>
          <div class="chat-source-attribution-url">${safeText(s.canonical_url)}</div>
          ${s.note ? `<div class="chat-source-attribution-note">${safeText(s.note)}</div>` : ""}
        </div>
      `).join("")
    : '<div class="empty">No source attribution for this turn.</div>';

  detail.innerHTML = `
    <div class="chat-turn-detail">
      <div class="response-label">Created</div>
      <div class="response-value">${safeText(formatDateTime(turn.created_at))}</div>
    </div>
    <div class="chat-turn-compare-row">
      <details class="chat-collapsible" data-chat-collapsible="chat-content"${
        inspectorSources.length ? " open" : ""
      }>
        <summary>
          <span class="chat-collapsible-summary">
            <span class="chat-collapsible-label">Source attribution (${
              inspectorSources.length
            })</span>
          </span>
        </summary>
        <div class="chat-collapsible-body chat-source-attribution-list">
          ${sourceDetailHtml}
        </div>
      </details>
    </div>
    <div class="chat-turn-compare-row">
      ${renderCollapsibleTextBlock(
        "Persisted operator message",
        operatorText,
        { collapseLimit: 220 },
      )}
    </div>
    <div class="chat-turn-compare-row">
      ${renderCollapsibleTextBlock(
        "Rendered Harbor input",
        renderedText,
        { collapseLimit: 420 },
      )}
    </div>
    <div class="chat-turn-compare-row">
      ${renderCollapsibleTextBlock(
        "Persisted assistant output",
        assistantText,
        { collapseLimit: 320 },
      )}
    </div>
    ${turn.status === "completed" && turn.output_text ? `
    <div class="chat-turn-compare-row">
      <details class="chat-collapsible" data-chat-collapsible="chat-content">
        <summary>
          <span class="chat-collapsible-summary">
            <span class="chat-collapsible-label">Draft as handbook</span>
            <span class="chat-collapsible-preview">
              Save assistant output as a new handbook version
            </span>
          </span>
        </summary>
        <div class="chat-collapsible-body">
          <div class="form-field">
            <label class="form-label"
              for="draft-handbook-note">Change note (optional)</label>
            <input type="text" id="draft-handbook-note"
              class="form-input"
              placeholder="Drafted from chat turn ${turn.turn_index}"
              maxlength="500" />
          </div>
          <button type="button" id="draft-handbook-btn"
            class="button button-sm">
            Save as handbook draft
          </button>
          <div id="draft-handbook-result"></div>
        </div>
      </details>
    </div>
    ` : ""}
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
    const turnMeta = [
      formatDateTime(turn.created_at),
      turn.status ? `Status: ${turn.status}` : "",
      turn.model ? `Model: ${turn.model}` : "",
    ].filter(Boolean);
    const assistantText = turn.output_text || turn.error_message || "No output.";
    const assistantRole = turn.status === "completed" ? "Assistant" : "Error";
    const assistantClass = turn.status === "completed" ? "assistant" : "error";
    const operatorMeta = [
      `Project: ${chatProjectLabel(turn.project_id)}`,
      turn.request_input_text ? `Chars: ${String(turn.request_input_text).length}` : "",
    ].filter(Boolean);
    const assistantMeta = [
      turn.provider ? `Provider: ${turn.provider}` : "",
      turn.response_id ? `Response: ${turn.response_id}` : "",
      assistantText ? `Chars: ${String(assistantText).length}` : "",
    ].filter(Boolean);

    const sourceAttr = Array.isArray(turn.source_attribution) ? turn.source_attribution : [];
    const sourcesBadge = sourceAttr.length
      ? `<div class="chat-source-attribution-badge">${safeText(
          sourceAttr.length === 1
            ? "1 source"
            : `${sourceAttr.length} sources`,
        )}: ${safeText(sourceAttr.map((s) => s.title).join(", "))}</div>`
      : "";

    fragments.push(`
      <article class="chat-turn-block" data-chat-turn-block="persisted-chat">
        <div class="chat-turn-block-header">
          <div class="chat-turn-block-title">${safeText(turnLabel)}</div>
          <div class="chat-turn-block-meta">${safeText(turnMeta.join(" · "))}</div>
        </div>
        <div class="chat-turn-block-body">
          <section class="chat-message user">
            <div class="chat-message-header">
              <div class="chat-role">Operator</div>
              <div class="chat-meta">${safeText(operatorMeta.join(" · "))}</div>
            </div>
            ${renderCollapsibleTextBlock(
              "Operator message",
              turn.request_input_text,
              { collapseLimit: 220 },
            )}
            ${sourcesBadge}
          </section>
          <section class="chat-message ${assistantClass}">
            <div class="chat-message-header">
              <div class="chat-role">${safeText(assistantRole)}</div>
              <div class="chat-meta">${safeText(assistantMeta.join(" · "))}</div>
            </div>
            ${renderCollapsibleTextBlock(
              assistantRole === "Assistant" ? "Assistant output" : "Error output",
              assistantText,
              { collapseLimit: 320, sourceAttribution: sourceAttr.length ? sourceAttr : null },
            )}
          </section>
        </div>
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

const currentInstructionsText = () => {
  return String(byId("chat-instructions-text")?.value || "").trim();
};

const renderInstructionsState = () => {
  const target = byId("chat-instructions-state");
  const presetState = byId("chat-instructions-preset-state");
  const presetSelect = byId("chat-instructions-preset");
  if (!target || !presetState || !presetSelect) {
    return;
  }

  const instructions = currentInstructionsText();
  if (!instructions) {
    target.textContent = "Using Harbor default instructions.";
    presetState.textContent = "Preset: Harbor default instructions.";
    presetSelect.value = CHAT_DEFAULT_PRESET_KEY;
    syncChatControls();
    return;
  }

  const matchedPreset = matchedInstructionPreset(instructions);
  if (matchedPreset) {
    target.textContent = `Using preset instructions: ${matchedPreset.label}.`;
    presetState.textContent = `Preset: ${matchedPreset.label}.`;
    presetSelect.value = matchedPreset.key;
    syncChatControls();
    return;
  }

  target.textContent = `Using custom instructions (${instructions.length} chars).`;
  presetState.textContent = "Preset: custom current text.";
  presetSelect.value = CHAT_CUSTOM_PRESET_KEY;
  syncChatControls();
};

const persistChatTurn = async ({
  projectId,
  inputText,
  chatSessionId,
  instructions,
}) => {
  return postJson(
    `${apiBase}/openai/projects/${encodeURIComponent(projectId)}/chat-turns`,
    {
      input_text: inputText,
      chat_session_id: chatSessionId,
      instructions: instructions || null,
    },
  );
};

const retryFailedChatMessage = async () => {
  if (chatBusy || !lastFailedChatRequest) {
    return;
  }

  const failedRequest = { ...lastFailedChatRequest };
  const input = byId("chat-input-text");
  const instructions = byId("chat-instructions-text");
  if (input) {
    input.value = failedRequest.inputText;
  }
  if (instructions) {
    instructions.value = failedRequest.instructions || "";
  }
  renderInstructionsState();

  chatBusy = true;
  syncChatControls();
  setChatStatus("Retrying failed Harbor chat turn...", "info");

  try {
    const payload = await persistChatTurn({
      projectId: failedRequest.projectId,
      inputText: failedRequest.inputText,
      chatSessionId: failedRequest.chatSessionId,
      instructions: failedRequest.instructions,
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
      instructions: failedRequest.instructions,
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
  const instructions = currentInstructionsText();

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
      instructions,
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
      instructions,
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
  if (button.dataset.chatAction === "clear-instructions") {
    applyInstructionPreset(CHAT_DEFAULT_PRESET_KEY);
  }
  if (button.dataset.chatAction === "apply-instructions-preset") {
    const presetSelect = byId("chat-instructions-preset");
    applyInstructionPreset(String(presetSelect?.value || CHAT_DEFAULT_PRESET_KEY));
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
    renderInstructionsState();
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
    return;
  }

  const presetSelect = event.target.closest("#chat-instructions-preset");
  if (presetSelect) {
    syncChatControls();
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

const proposeSourceForm = byId("propose-source-form");
if (proposeSourceForm) {
  proposeSourceForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const projectId = byId("chat-project-id")?.value;
    if (!projectId) {
      return;
    }
    const url = byId("propose-source-url")?.value?.trim();
    if (!url) {
      return;
    }
    const title = byId("propose-source-title")?.value?.trim() || null;
    const note = byId("propose-source-note")?.value?.trim() || null;
    const resultDiv = byId("propose-source-result");
    const body = { canonical_url: url };
    if (title) body.title = title;
    if (note) body.note = note;
    try {
      const ep = `${apiBase}/openai/projects/` +
        `${encodeURIComponent(projectId)}/propose-source`;
      const opts = {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      };
      const response = await fetch(ep, opts);
      if (!response.ok) {
        const err = await response.json().catch(() => ({}));
        throw new Error(err.detail || `HTTP ${response.status}`);
      }
      const data = await response.json();
      if (resultDiv) {
        const t = safeText(data.source?.title || url);
        resultDiv.innerHTML =
          `<div class="propose-source-result success">` +
          `Source proposed: ${t} (candidate)</div>`;
      }
      proposeSourceForm.reset();
    } catch (err) {
      if (resultDiv) {
        const m = safeText(String(err.message || err));
        resultDiv.innerHTML =
          `<div class="propose-source-result error">` +
          `${m}</div>`;
      }
    }
  });
}

document.addEventListener("click", async (event) => {
  const btn = event.target.closest("#draft-handbook-btn");
  if (!btn) return;
  const turn = chatHistory.find(
    (t) => t.openai_project_chat_turn_id === currentTurnId,
  );
  if (!turn || !turn.output_text) return;
  const projectId = turn.project_id;
  const noteInput = byId("draft-handbook-note");
  const changeNote = noteInput?.value?.trim() || null;
  const resultDiv = byId("draft-handbook-result");
  const body = { handbook_markdown: turn.output_text };
  if (changeNote) body.change_note = changeNote;
  btn.disabled = true;
  try {
    const ep = `${apiBase}/openai/projects/` +
      `${encodeURIComponent(projectId)}/draft-handbook`;
    const opts = {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    };
    const response = await fetch(ep, opts);
    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      throw new Error(err.detail || `HTTP ${response.status}`);
    }
    const data = await response.json();
    if (resultDiv) {
      const v = safeText(`v${data.version_number}`);
      resultDiv.innerHTML =
        `<div class="draft-handbook-result success">` +
        `Handbook ${v} created.</div>`;
    }
  } catch (err) {
    btn.disabled = false;
    if (resultDiv) {
      const m = safeText(String(err.message || err));
      resultDiv.innerHTML =
        `<div class="draft-handbook-result error">` +
        `${m}</div>`;
    }
  }
});

clearChatHistory("Loading Harbor projects...");
renderDefaultInstructionsPreview();
renderInstructionPresetOptions();
renderInstructionsState();
renderChatRetryPanel();
loadChatProjects();
byId("chat-instructions-text")?.addEventListener("input", renderInstructionsState);
