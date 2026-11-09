// ============================================================
// YUVAAI — FRONTEND APPLICATION
// Authentication + Chat + Conversation Management
// ============================================================


// ============================================================
// 1. CONFIGURATION
// ============================================================


const API_BASE_URL = (
    window.YUVAAI_API_BASE_URL || ""
).replace(/\/+$/, "");

const DAILY_MESSAGE_LIMIT = 50;

const MAX_MESSAGE_LENGTH = 4000;


// ============================================================
// 2. APPLICATION STATE
// ============================================================

let csrfToken = null;

let currentUser = null;

let activeConversationId = null;

let isSendingMessage = false;

let usageLimit = DAILY_MESSAGE_LIMIT;

let messagesUsed = 0;

let appInitializationStarted = false;


// ============================================================
// 3. DOM ELEMENTS
// ============================================================

const authScreen = document.getElementById("authScreen");
const appContainer = document.getElementById("appContainer");

const loginForm = document.getElementById("loginForm");
const registerForm = document.getElementById("registerForm");

const authTitle = document.getElementById("authTitle");
const authSubtitle = document.getElementById("authSubtitle");

const authMessage = document.getElementById("authMessage");

const authSwitchText = document.getElementById("authSwitchText");
const authSwitchButton = document.getElementById("authSwitchButton");

const loginEmail = document.getElementById("loginEmail");
const loginPassword = document.getElementById("loginPassword");

const registerName = document.getElementById("registerName");
const registerEmail = document.getElementById("registerEmail");
const registerPassword = document.getElementById("registerPassword");
const confirmPassword = document.getElementById("confirmPassword");

const loginSubmit = document.getElementById("loginSubmit");
const registerSubmit = document.getElementById("registerSubmit");

const currentUserName = document.getElementById("currentUserName");
const currentUserEmail = document.getElementById("currentUserEmail");

const logoutButton = document.getElementById("logoutButton");

const conversationList = document.getElementById("conversationList");

const newChatButton = document.getElementById("newChatButton");

const welcomeScreen = document.getElementById("welcomeScreen");
const messagesContainer = document.getElementById("messagesContainer");

const messageForm = document.getElementById("messageForm");
const messageInput = document.getElementById("messageInput");
const sendButton = document.getElementById("sendButton");

const characterCounter = document.getElementById("characterCounter");

const usageText = document.getElementById("usageText");
const usageProgress = document.getElementById("usageProgress");

const themeButton = document.getElementById("themeButton");

const sidebar = document.getElementById("sidebar");
const sidebarOverlay = document.getElementById("sidebarOverlay");

const menuButton = document.getElementById("menuButton");
const closeSidebar = document.getElementById("closeSidebar");
document.querySelector(".ai-orb-container");
// ============================================================
// 4. API HELPERS
// ============================================================

async function fetchCsrfToken() {

    const response = await fetch(
        `${API_BASE_URL}/api/auth/csrf`,
        {
            method: "GET",
            credentials: "include"
        }
    );

    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
        throw new Error(
            data.detail || "Unable to initialize security token."
        );
    }

    csrfToken = data.csrf_token;

    if (!csrfToken) {
        throw new Error("CSRF token was not returned by the server.");
    }

    return csrfToken;
}


async function apiRequest(endpoint, options = {}) {

    const method = (options.method || "GET").toUpperCase();

    const headers = {
        ...(options.headers || {})
    };

    const isWriteRequest = [
        "POST",
        "PUT",
        "PATCH",
        "DELETE"
    ].includes(method);


    // Attach CSRF token to write requests.

    if (isWriteRequest) {

        if (!csrfToken) {
            await fetchCsrfToken();
        }

        headers["X-CSRF-Token"] = csrfToken;
    }


    // Handle request body.

    let body = options.body;

    if (
        body &&
        typeof body === "object" &&
        !(body instanceof FormData) &&
        !(body instanceof Blob)
    ) {

        headers["Content-Type"] = "application/json";

        body = JSON.stringify(body);
    }


    const response = await fetch(
        `${API_BASE_URL}${endpoint}`,
        {
            ...options,
            method,
            headers,
            body,
            credentials: "include"
        }
    );


    const data = await response.json().catch(() => ({}));


    if (!response.ok) {

        const errorMessage =
            typeof data.detail === "string"
                ? data.detail
                : data.detail?.message ||
                  data.message ||
                  "Something went wrong.";

        const error = new Error(errorMessage);

        error.status = response.status;

        error.data = data;


        // Handle expired authentication.

        if (
            response.status === 401 &&
            endpoint !== "/api/auth/login" &&
            endpoint !== "/api/auth/register" &&
            endpoint !== "/api/auth/me"
        ) {

            showAuthScreen("login");
        }

        throw error;
    }

    return data;
}


// ============================================================
// 5. AUTHENTICATION UI
// ============================================================

function showAuthMessage(message, type = "error") {

    if (!authMessage) return;

    authMessage.textContent = message;

    authMessage.className = `auth-message ${type}`;

    authMessage.hidden = false;
}


function clearAuthMessage() {

    if (!authMessage) return;

    authMessage.textContent = "";

    authMessage.className = "auth-message";

    authMessage.hidden = true;
}


function showAuthMode(mode = "login") {

    const isRegister = mode === "register";

    clearAuthMessage();


    if (loginForm) {

        loginForm.hidden = isRegister;

        loginForm.reset();
    }


    if (registerForm) {

        registerForm.hidden = !isRegister;

        registerForm.reset();
    }


    if (isRegister) {

        if (authTitle) {
            authTitle.textContent = "Create your account";
        }

        if (authSubtitle) {
            authSubtitle.textContent =
                "Start your YuvaAI experience.";
        }

        if (authSwitchText) {
            authSwitchText.textContent =
                "Already have an account?";
        }

        if (authSwitchButton) {
            authSwitchButton.textContent = "Sign in";
        }

    } else {

        if (authTitle) {
            authTitle.textContent = "Welcome back";
        }

        if (authSubtitle) {
            authSubtitle.textContent =
                "Sign in to continue to YuvaAI.";
        }

        if (authSwitchText) {
            authSwitchText.textContent =
                "Don't have an account?";
        }

        if (authSwitchButton) {
            authSwitchButton.textContent = "Create account";
        }
    }
}


function showAuthScreen(mode = "login") {

    currentUser = null;

    activeConversationId = null;

    if (appContainer) {
        appContainer.hidden = true;
    }

    if (authScreen) {
        authScreen.hidden = false;
    }

    closeSidebarPanel();

    showAuthMode(mode);
}


function showApplication() {

    if (authScreen) {
        authScreen.hidden = true;
    }

    if (appContainer) {
        appContainer.hidden = false;
    }
}


function updateUserInterface(user) {

    if (!user) return;

    currentUser = user;

    if (currentUserName) {

        currentUserName.textContent =
            user.name ||
            user.email?.split("@")[0] ||
            "YuvaAI User";
    }

    if (currentUserEmail) {
        currentUserEmail.textContent = user.email || "";
    }
}


// ============================================================
// 6. LOGIN
// ============================================================

if (loginForm) {

    loginForm.addEventListener("submit", async (event) => {

        event.preventDefault();

        clearAuthMessage();

        const email = loginEmail.value.trim().toLowerCase();

        const password = loginPassword.value;


        if (!email || !password) {

            showAuthMessage(
                "Please enter your email and password."
            );

            return;
        }


        loginSubmit.disabled = true;

        loginSubmit.textContent = "Signing in...";


        try {

            const data = await apiRequest(
                "/api/auth/login",
                {
                    method: "POST",
                    body: {
                        email,
                        password
                    }
                }
            );

            await completeAuthentication(data);


        } catch (error) {

            showAuthMessage(error.message);


        } finally {

            loginSubmit.disabled = false;

            loginSubmit.textContent = "Sign In";
        }

    });
}


// ============================================================
// 7. REGISTRATION
// ============================================================

if (registerForm) {

    registerForm.addEventListener("submit", async (event) => {

        event.preventDefault();

        clearAuthMessage();


        const name = registerName.value.trim();

        const email = registerEmail.value.trim().toLowerCase();

        const password = registerPassword.value;

        const confirm = confirmPassword.value;


        if (!name || !email || !password || !confirm) {

            showAuthMessage("Please complete all fields.");

            return;
        }


        if (name.length < 2) {

            showAuthMessage(
                "Your name must contain at least 2 characters."
            );

            return;
        }


        if (password.length < 8 || password.length > 128) {

            showAuthMessage(
                "Password must contain between 8 and 128 characters."
            );

            return;
        }


        if (password !== confirm) {

            showAuthMessage("Passwords do not match.");

            return;
        }


        registerSubmit.disabled = true;

        registerSubmit.textContent = "Creating account...";


        try {

            const data = await apiRequest(
                "/api/auth/register",
                {
                    method: "POST",
                    body: {
                        name,
                        email,
                        password
                    }
                }
            );

            await completeAuthentication(data);


        } catch (error) {

            showAuthMessage(error.message);


        } finally {

            registerSubmit.disabled = false;

            registerSubmit.textContent = "Create Account";
        }

    });
}


// ============================================================
// 8. AUTHENTICATION SWITCH
// ============================================================

if (authSwitchButton) {

    authSwitchButton.addEventListener("click", () => {

        const registrationVisible =
            registerForm && !registerForm.hidden;

        showAuthMode(
            registrationVisible ? "login" : "register"
        );

    });
}


// ============================================================
// 9. COMPLETE LOGIN / REGISTRATION
// ============================================================

async function completeAuthentication(data) {

    const user = data.user || data;

    updateUserInterface(user);

    showApplication();

    clearChatView();

    await loadConversations();

    updateCharacterCounter();

    if (messageInput) {
        messageInput.focus();
    }
}


// ============================================================
// 10. LOGOUT
// ============================================================

if (logoutButton) {

    logoutButton.addEventListener("click", async () => {

        logoutButton.disabled = true;

        try {

            await apiRequest(
                "/api/auth/logout",
                {
                    method: "POST"
                }
            );

        } catch (error) {

            console.error("Logout error:", error);

        } finally {

            csrfToken = null;

            showAuthScreen("login");

            logoutButton.disabled = false;
        }

    });
}


// ============================================================
// 11. SESSION INITIALIZATION
// ============================================================

async function initializeApp() {

    if (appInitializationStarted) return;

    appInitializationStarted = true;

    loadTheme();

    updateCharacterCounter();

    showAuthScreen("login");


    try {

        await fetchCsrfToken();

        const data = await apiRequest("/api/auth/me");

        const user = data.user || data;

        updateUserInterface(user);

        showApplication();

        await loadConversations();


    } catch (error) {

        if (error.status === 401) {

            showAuthScreen("login");

            return;
        }

        console.error("Initialization error:", error);

        showAuthScreen("login");

        showAuthMessage(
            "Unable to connect to YuvaAI. Make sure the backend server is running."
        );
    }

}


// ============================================================
// 12. CONVERSATION MANAGEMENT
// ============================================================

async function loadConversations() {

    if (!conversationList) return;

    try {

        const data = await apiRequest("/api/conversations");

        let conversations;


        if (Array.isArray(data)) {

            conversations = data;

        } else {

            conversations =
                data.conversations ||
                data.items ||
                [];
        }


        renderConversationList(conversations);


    } catch (error) {

        console.error(
            "Conversation loading error:",
            error
        );
    }
}


function renderConversationList(conversations) {

    if (!conversationList) return;

    conversationList.replaceChildren();


    if (!Array.isArray(conversations) || conversations.length === 0) {

        const emptyMessage = document.createElement("div");

        emptyMessage.className = "empty-history";

        emptyMessage.textContent =
            "Your conversations will appear here.";

        conversationList.appendChild(emptyMessage);

        return;
    }


    conversations.forEach((conversation) => {

        const item = document.createElement("div");

        item.className = "conversation-item";

        item.dataset.conversationId = String(conversation.id);


        if (
            Number(conversation.id) ===
            Number(activeConversationId)
        ) {

            item.classList.add("active");
        }


        const title = document.createElement("span");

        title.className = "conversation-title";

        title.textContent =
            conversation.title || "New Chat";


        const deleteButton = document.createElement("button");

        deleteButton.className = "conversation-delete";

        deleteButton.type = "button";

        deleteButton.textContent = "×";

        deleteButton.title = "Delete conversation";

        deleteButton.setAttribute(
            "aria-label",
            "Delete conversation"
        );

        deleteButton.dataset.deleteConversation =
            String(conversation.id);


        item.appendChild(title);

        item.appendChild(deleteButton);

        conversationList.appendChild(item);

    });

}


// ============================================================
// 13. CONVERSATION CLICK HANDLING
// ============================================================

if (conversationList) {

    conversationList.addEventListener("click", async (event) => {

        const deleteButton = event.target.closest(
            "[data-delete-conversation]"
        );


        if (deleteButton) {

            event.stopPropagation();

            const conversationId =
                deleteButton.dataset.deleteConversation;

            await deleteConversation(conversationId);

            return;
        }


        const item = event.target.closest(
            "[data-conversation-id]"
        );


        if (!item) return;

        const conversationId = item.dataset.conversationId;

        await openConversation(conversationId);

    });

}


// ============================================================
// 14. OPEN OLD CONVERSATION
// FIXED: BACKEND RETURNS MESSAGES AT TOP LEVEL.
// ============================================================

async function openConversation(conversationId) {

    if (isSendingMessage) return;

    try {

        const data = await apiRequest(
            `/api/conversations/${encodeURIComponent(conversationId)}`
        );


        // Correctly read the conversation object.

        const conversation = data.conversation || data;


        // Correctly read messages from the top-level response.

        const messages = Array.isArray(data.messages)
            ? data.messages
            : Array.isArray(conversation.messages)
                ? conversation.messages
                : [];


        activeConversationId =
            conversation.id ?? Number(conversationId);


        // Clear the previous chat.

        if (messagesContainer) {

            messagesContainer.replaceChildren();

            messagesContainer.hidden = false;
        }


        // Hide welcome screen.

        if (welcomeScreen) {

            welcomeScreen.hidden = true;

            welcomeScreen.style.removeProperty("display");
        }


        // Render conversation history.

        if (!messages.length) {

            const emptyState = document.createElement("div");

            emptyState.className = "empty-history";

            emptyState.textContent =
                "This conversation has no messages yet.";

            messagesContainer?.appendChild(emptyState);

        } else {

            messages.forEach((message) => {

                if (
                    !message ||
                    !["user", "assistant"].includes(message.role)
                ) {
                    return;
                }

                appendMessage(
                    message.role,
                    message.content ?? ""
                );

            });

        }


        renderActiveConversation();

        scrollToBottom();

        closeSidebarPanel();


    } catch (error) {

        console.error(
            "Conversation opening error:",
            error
        );

        if (error.status !== 401) {

            alert(
                error.message ||
                "Unable to load conversation."
            );
        }

    }

}


// ============================================================
// 15. DELETE CONVERSATION
// ============================================================

// ============================================================
// YUVAAI — CUSTOM DELETE CONFIRMATION MODAL
// ============================================================

function showDeleteConfirmation() {

    return new Promise((resolve) => {

        const overlay = document.createElement("div");

        overlay.className = "delete-modal-overlay";

        overlay.innerHTML = `
            <div
                class="delete-modal"
                role="dialog"
                aria-modal="true"
                aria-labelledby="deleteModalTitle"
                aria-describedby="deleteModalDescription"
            >

                <div class="delete-modal-icon">
                    <span>🗑</span>
                </div>

                <div class="delete-modal-content">

                    <h2 id="deleteModalTitle">
                        Delete this conversation?
                    </h2>

                    <p id="deleteModalDescription">
                        This conversation and its messages
                        will be permanently deleted.
                        This action cannot be undone.
                    </p>

                </div>

                <div class="delete-modal-actions">

                    <button
                        type="button"
                        class="delete-cancel-button"
                        id="cancelDeleteButton"
                    >
                        Keep conversation
                    </button>

                    <button
                        type="button"
                        class="delete-confirm-button"
                        id="confirmDeleteButton"
                    >
                        Delete conversation
                    </button>

                </div>

                <button
                    type="button"
                    class="delete-modal-close"
                    aria-label="Close dialog"
                    id="closeDeleteModal"
                >
                    ×
                </button>

            </div>
        `;

        document.body.appendChild(overlay);

        const cancelButton = overlay.querySelector(
            "#cancelDeleteButton"
        );

        const confirmButton = overlay.querySelector(
            "#confirmDeleteButton"
        );

        const closeButton = overlay.querySelector(
            "#closeDeleteModal"
        );

        let completed = false;

        function closeModal(result) {

            if (completed) return;

            completed = true;

            document.removeEventListener(
                "keydown",
                handleKeyboard
            );

            overlay.classList.remove("active");

            setTimeout(() => {

                overlay.remove();

                resolve(result);

            }, 180);

        }


        function handleKeyboard(event) {

            if (event.key === "Escape") {

                event.preventDefault();

                closeModal(false);
            }

            if (event.key === "Tab") {

                const buttons = [
                    cancelButton,
                    confirmButton,
                    closeButton
                ];

                const first = buttons[0];

                const last = buttons[2];

                if (
                    event.shiftKey &&
                    document.activeElement === first
                ) {

                    event.preventDefault();

                    last.focus();

                } else if (
                    !event.shiftKey &&
                    document.activeElement === last
                ) {

                    event.preventDefault();

                    first.focus();
                }
            }

        }


        cancelButton.addEventListener("click", () => {

            closeModal(false);

        });


        closeButton.addEventListener("click", () => {

            closeModal(false);

        });


        confirmButton.addEventListener("click", () => {

            closeModal(true);

        });


        overlay.addEventListener("click", (event) => {

            if (event.target === overlay) {

                closeModal(false);

            }

        });


        document.addEventListener(
            "keydown",
            handleKeyboard
        );


        // Trigger opening animation.

        requestAnimationFrame(() => {

            overlay.classList.add("active");

            confirmButton.focus();

        });

    });

}


// ============================================================
// DELETE CONVERSATION
// ============================================================

async function deleteConversation(conversationId) {

    // Show custom confirmation dialog.

    const confirmed = await showDeleteConfirmation();

    if (!confirmed) return;


    try {

        await apiRequest(
            `/api/conversations/${encodeURIComponent(conversationId)}`,
            {
                method: "DELETE"
            }
        );


        // Reset current chat if the deleted conversation was open.

        if (
            Number(activeConversationId) ===
            Number(conversationId)
        ) {

            clearChatView();

        }


        // Refresh sidebar.

        await loadConversations();


    } catch (error) {

        console.error(
            "Conversation deletion error:",
            error
        );

        alert(
            error.message ||
            "Unable to delete this conversation."
        );

    }

}
// ============================================================
// 16. ACTIVE CONVERSATION UI
// ============================================================

function renderActiveConversation() {

    if (!conversationList) return;

    const items = conversationList.querySelectorAll(
        "[data-conversation-id]"
    );


    items.forEach((item) => {

        const id = item.dataset.conversationId;

        item.classList.toggle(
            "active",
            Number(id) === Number(activeConversationId)
        );

    });

}


// ============================================================
// 17. NEW CHAT
// ============================================================

function clearChatView() {

    activeConversationId = null;


    if (messagesContainer) {

        messagesContainer.replaceChildren();

        messagesContainer.hidden = true;
    }


    if (welcomeScreen) {

        welcomeScreen.hidden = false;

        welcomeScreen.style.removeProperty("display");
    }


    renderActiveConversation();
}


if (newChatButton) {

    newChatButton.addEventListener("click", () => {

        if (isSendingMessage) return;

        clearChatView();

        if (messageInput) {

            messageInput.value = "";

            updateCharacterCounter();

            messageInput.focus();
        }

        closeSidebarPanel();

        void loadConversations();

    });

}


// ============================================================
// 18. YUVAAI LOGO NAVIGATION
// Clicking the logo starts a new chat.
// ============================================================

document.addEventListener("click", (event) => {

    const brand = event.target.closest(
        "#appContainer .brand"
    );

    if (!brand) return;

    event.preventDefault();

    if (isSendingMessage) return;

    clearChatView();

    if (messageInput) {

        messageInput.value = "";

        updateCharacterCounter();

        messageInput.focus();
    }

    closeSidebarPanel();

    void loadConversations();

});


// ============================================================
// 19. MESSAGE RENDERING
// ============================================================

function appendMessage(role, content) {

    if (!messagesContainer) return;


    if (welcomeScreen) {
        welcomeScreen.hidden = true;
    }

    messagesContainer.hidden = false;


    const isUser = role === "user";


    const messageRow = document.createElement("div");

    messageRow.className =
        `message message-row ${role}-message ${role}`;


    const messageContent = document.createElement("div");

    messageContent.className =
        "message-content message-bubble";


    if (isUser) {

        // Never interpret user content as HTML.

        messageContent.textContent = content || "";

    } else {

        messageContent.innerHTML =
            renderMarkdown(content || "");
    }


    messageRow.appendChild(messageContent);

    messagesContainer.appendChild(messageRow);


    if (!isUser) {

        highlightCodeBlocks(messageContent);
    }


    scrollToBottom();

    return messageRow;

}


// ============================================================
// 20. MARKDOWN RENDERING
// ============================================================

function escapeHTML(text) {

    return String(text)

        .replace(/&/g, "&amp;")

        .replace(/</g, "&lt;")

        .replace(/>/g, "&gt;")

        .replace(/"/g, "&quot;")

        .replace(/'/g, "&#039;");

}


function normalizeMarkdown(content) {

    const source = String(content ?? "");

    const parts = source.split(/(```[\s\S]*?```)/g);

    return parts.map((part, index) => {

        // Preserve fenced code blocks.

        if (index % 2 === 1) return part;

        return part

            .replace(/\\r\\n/g, "\n")

            .replace(/\\n/g, "\n")

            .replace(/\\t/g, "\t");

    }).join("");

}


function renderMarkdown(content) {

    const source = normalizeMarkdown(content);


    // Safe fallback if Markdown libraries are unavailable.

    if (
        typeof window.marked === "undefined" ||
        typeof window.marked.parse !== "function" ||
        typeof window.DOMPurify === "undefined"
    ) {

        return `<p>${escapeHTML(source).replace(/\n/g, "<br>")}</p>`;
    }


    const parsedMarkdown = window.marked.parse(source, {
        gfm: true,
        breaks: true
    });


    return window.DOMPurify.sanitize(parsedMarkdown, {
        USE_PROFILES: {
            html: true
        }
    });

}


// ============================================================
// 21. CODE HIGHLIGHTING + COPY BUTTONS
// ============================================================



function highlightCodeBlocks(container) {

    if (!container) return;


    const codeBlocks = container.querySelectorAll("pre");


    codeBlocks.forEach((pre) => {

        const code = pre.querySelector("code");

        if (!code) return;


        if (
            typeof window.hljs !== "undefined" &&
            !code.classList.contains("hljs")
        ) {

            window.hljs.highlightElement(code);
        }


        // Avoid duplicate copy buttons.

        if (pre.querySelector(".code-copy-button")) {
            return;
        }


        const copyButton = document.createElement("button");

        copyButton.className = "code-copy-button";

        copyButton.type = "button";

        copyButton.textContent = "Copy";


        copyButton.addEventListener("click", async () => {

            try {

                await navigator.clipboard.writeText(
                    code.innerText
                );

                copyButton.textContent = "Copied!";

                setTimeout(() => {

                    copyButton.textContent = "Copy";

                }, 1500);


            } catch (error) {

                console.error("Code copy failed:", error);

                copyButton.textContent = "Failed";

                setTimeout(() => {

                    copyButton.textContent = "Copy";

                }, 1500);

            }

        });


        pre.appendChild(copyButton);

    });


    // Open external links safely.

    const links = container.querySelectorAll("a[href]");

    links.forEach((link) => {

        link.target = "_blank";

        link.rel = "noopener noreferrer";

    });

}


// ============================================================
// 22. TYPING INDICATOR
// ============================================================

function showTypingIndicator() {

    if (!messagesContainer) return null;

    if (welcomeScreen) {
        welcomeScreen.hidden = true;
    }

    messagesContainer.hidden = false;


    const typingRow = document.createElement("div");

    typingRow.className =
        "message message-row assistant-message typing-message";


    const typingContent = document.createElement("div");

    typingContent.className =
        "message-content message-bubble";


    typingContent.innerHTML = `
        <div class="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
        </div>
    `;


    typingRow.appendChild(typingContent);

    messagesContainer.appendChild(typingRow);

    scrollToBottom();

    return typingRow;

}


// ============================================================
// 23. SEND CHAT MESSAGE
// ============================================================

if (messageForm) {

    messageForm.addEventListener("submit", async (event) => {

        event.preventDefault();

        if (isSendingMessage) return;

        const message = messageInput.value.trim();

        if (!message) return;

        await sendMessage(message);

    });

}


async function sendMessage(message) {

    if (isSendingMessage) return;


    const cleanMessage = String(message ?? "").trim();

    if (!cleanMessage) return;


    if (cleanMessage.length > MAX_MESSAGE_LENGTH) {

        alert(
            `Message cannot exceed ${MAX_MESSAGE_LENGTH} characters.`
        );

        return;
    }


    isSendingMessage = true;

    setChatLoading(true);


    appendMessage("user", cleanMessage);


    if (messageInput) {

        messageInput.value = "";

        updateCharacterCounter();
    }


    const typingIndicator = showTypingIndicator();


    try {

        const data = await apiRequest(
            "/api/chat",
            {
                method: "POST",
                body: {
                    message: cleanMessage,
                    conversation_id: activeConversationId
                }
            }
        );


        // Save newly created conversation ID.

        if (data.conversation_id) {

            activeConversationId = data.conversation_id;
        }


        typingIndicator?.remove();


        const assistantResponse =
            data.response ??
            data.answer ??
            data.assistant_message ??
            data.content;


        let responseText = assistantResponse;


        if (
            assistantResponse &&
            typeof assistantResponse === "object"
        ) {

            responseText = assistantResponse.content;
        }


        appendMessage(
            "assistant",
            responseText ||
            "The assistant returned an empty response."
        );


        // Update usage information.

        if (data.usage) {

            updateUsage(data.usage);

        } else if (data.usage_status) {

            updateUsage(data.usage_status);
        }


        await loadConversations();

        renderActiveConversation();


    } catch (error) {

        console.error("Chat error:", error);

        typingIndicator?.remove();


        if (error.status === 429) {

            const detail = error.data?.detail;

            const limitMessage =
                typeof detail === "string"
                    ? detail
                    : detail?.message ||
                      "You have reached your message limit.";

            appendMessage("assistant", limitMessage);

        } else if (error.status !== 401) {

            appendMessage(
                "assistant",
                `**Unable to complete your request.**\n\n${error.message}`
            );
        }


    } finally {

        isSendingMessage = false;

        setChatLoading(false);

        updateCharacterCounter();

        if (messageInput && appContainer && !appContainer.hidden) {

            messageInput.focus();
        }

    }

}


// ============================================================
// 24. CHAT LOADING STATE
// ============================================================

function setChatLoading(loading) {

    if (messageInput) {
        messageInput.disabled = loading;
    }

    if (sendButton) {
        sendButton.disabled = loading;
    }

}


// ============================================================
// 25. CHARACTER COUNTER
// ============================================================

function updateCharacterCounter() {

    if (!messageInput) return;

    const length = messageInput.value.length;


    if (characterCounter) {

        characterCounter.textContent =
            `${length} / ${MAX_MESSAGE_LENGTH}`;

    }


    if (length > MAX_MESSAGE_LENGTH) {

        characterCounter?.classList.add("limit-reached");

    } else {

        characterCounter?.classList.remove("limit-reached");
    }


    if (sendButton) {

        sendButton.disabled =
            length === 0 ||
            length > MAX_MESSAGE_LENGTH ||
            isSendingMessage;
    }


    // Auto resize textarea.

    messageInput.style.height = "auto";

    messageInput.style.height =
        `${Math.min(messageInput.scrollHeight, 150)}px`;

}


if (messageInput) {

    messageInput.addEventListener(
        "input",
        updateCharacterCounter
    );


    messageInput.addEventListener("keydown", (event) => {

        if (
            event.key === "Enter" &&
            !event.shiftKey &&
            !event.isComposing
        ) {

            event.preventDefault();

            messageForm?.requestSubmit();
        }

    });

}


// ============================================================
// 26. SUGGESTION PROMPTS
// ============================================================

document.querySelectorAll("[data-prompt]").forEach((element) => {

    element.addEventListener("click", () => {

        const prompt = element.dataset.prompt;

        if (!prompt || !messageInput) return;


        messageInput.value = prompt;

        updateCharacterCounter();

        messageInput.focus();

    });

});


// ============================================================
// 27. USAGE DISPLAY
// ============================================================

function updateUsage(usage) {

    if (!usage) return;


    if (usage.messages_used !== undefined) {

        messagesUsed = Number(usage.messages_used);
    }


    if (usage.daily_limit !== undefined) {

        usageLimit = Number(usage.daily_limit);
    }


    const remaining =
        usage.messages_remaining !== undefined
            ? Number(usage.messages_remaining)
            : Math.max(0, usageLimit - messagesUsed);


    if (usageText) {

        usageText.textContent =
            `${remaining} messages remaining today`;

        usageText.style.color =
            remaining <= 5 ? "#ff9999" : "";

    }


    if (usageProgress) {

        const percentage =
            usageLimit > 0
                ? (messagesUsed / usageLimit) * 100
                : 0;

        usageProgress.style.width =
            `${Math.min(Math.max(percentage, 0), 100)}%`;

    }

}


// ============================================================
// 28. SIDEBAR MANAGEMENT
// ============================================================

function openSidebarPanel() {

    document.body.classList.add("sidebar-open");

    sidebar?.classList.add("open");

    sidebarOverlay?.classList.add("visible");

}


function closeSidebarPanel() {

    document.body.classList.remove("sidebar-open");

    sidebar?.classList.remove("open");

    sidebarOverlay?.classList.remove("visible");

}


menuButton?.addEventListener(
    "click",
    openSidebarPanel
);


closeSidebar?.addEventListener(
    "click",
    closeSidebarPanel
);


sidebarOverlay?.addEventListener(
    "click",
    closeSidebarPanel
);


// ============================================================
// 29. SCROLLING
// ============================================================

function scrollToBottom() {

    if (!messagesContainer) return;

    requestAnimationFrame(() => {

        messagesContainer.scrollTop =
            messagesContainer.scrollHeight;

    });

}


// ============================================================
// 30. THEME MANAGEMENT
// Uses body.light-theme to match the existing stylesheet.
// ============================================================

function updateThemeButton(button) {

    if (!button) return;

    const isLight =
        document.body.classList.contains("light-theme");


    button.textContent = isLight ? "☾" : "☀";

    button.title = isLight
        ? "Switch to dark theme"
        : "Switch to light theme";

    button.setAttribute(
        "aria-label",
        button.title
    );

}


function applyTheme(theme) {

    const normalizedTheme =
        theme === "light" ? "light" : "dark";


    const isLight = normalizedTheme === "light";


    // This class is used by the existing CSS.

    document.body.classList.toggle(
        "light-theme",
        isLight
    );


    document.documentElement.dataset.theme =
        normalizedTheme;

    document.body.dataset.theme =
        normalizedTheme;


    // Keep a single localStorage key.

    localStorage.setItem(
        "yuvaai_theme",
        normalizedTheme
    );


    updateThemeButton(themeButton);

    updateThemeButton(
        document.getElementById("authThemeButton")
    );

}


function loadTheme() {

    const savedTheme =
        localStorage.getItem("yuvaai_theme") || "dark";

    applyTheme(savedTheme);

}


// ============================================================
// 31. AUTH SCREEN THEME BUTTON
// ============================================================

function createAuthThemeButton() {

    if (!authScreen) return;

    if (document.getElementById("authThemeButton")) return;


    const button = document.createElement("button");

    button.id = "authThemeButton";

    button.className = "auth-theme-toggle";

    button.type = "button";


    button.addEventListener("click", () => {

        const isLight =
            document.body.classList.contains("light-theme");

        applyTheme(isLight ? "dark" : "light");

    });


    authScreen.appendChild(button);

    updateThemeButton(button);

}


// Main app theme button.

if (themeButton) {

    themeButton.addEventListener("click", () => {

        const isLight =
            document.body.classList.contains("light-theme");

        applyTheme(isLight ? "dark" : "light");

    });

}


// Login / registration theme button.

createAuthThemeButton();


// ============================================================
// 32. KEYBOARD SHORTCUTS
// ============================================================

document.addEventListener("keydown", (event) => {

    // Escape closes mobile sidebar.

    if (event.key === "Escape") {

        closeSidebarPanel();
    }


    // Ctrl + Shift + O starts a new chat.

    if (
        event.ctrlKey &&
        event.shiftKey &&
        event.key.toLowerCase() === "o"
    ) {

        event.preventDefault();

        if (
            appContainer &&
            !appContainer.hidden &&
            newChatButton
        ) {

            newChatButton.click();
        }

    }

});


// ============================================================
// 33. APPLICATION INITIALIZATION
// ============================================================

if (document.readyState === "loading") {

    document.addEventListener(
        "DOMContentLoaded",
        initializeApp,
        { once: true }
    );

} else {

    void initializeApp();

}