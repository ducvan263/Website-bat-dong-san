const chatInput = document.querySelector("#chat-input");
const sendButton = document.querySelector("#send-btn");
const chatContainer = document.querySelector(".chat-container");
const themeButton = document.querySelector("#theme-btn");
const deleteButton = document.querySelector("#delete-btn");

let userText = "";

// =========================
// THEME
// =========================
const loadTheme = () => {
    const themeColor = localStorage.getItem("themeColor");
    document.body.classList.toggle("light-mode", themeColor === "light_mode");
    themeButton.innerText = document.body.classList.contains("light-mode")
        ? "dark_mode"
        : "light_mode";
};
loadTheme();
const avatarUser = document.body.dataset.avatar;
console.log(avatarUser)
// =========================
// CREATE CHAT ELEMENT (GIỮ AVATAR)
// =========================
const createChatElement = (message, className) => {
    const div = document.createElement("div");
    div.className = `chat ${className}`;
    div.innerHTML = `
        <div class="chat-content">
            <div class="chat-details">
                <img src="${className === 'outgoing' ? avatarUser : '/static/img/chatbot.jpg'}">
                <p>${message}</p>
            </div>
        </div>
    `;
    return div;
};

// =========================
// CALL BACKEND
// =========================
const getChatResponse = async (incomingChatDiv) => {
    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: userText })
        });

        const data = await response.json();

        incomingChatDiv.querySelector(".typing-animation")?.remove();
        incomingChatDiv.querySelector("p").textContent = data.reply;

    } catch (err) {
        incomingChatDiv.querySelector("p").textContent = "Không thể kết nối AI";
    }

    chatContainer.scrollTop = chatContainer.scrollHeight;
};

// =========================
// TYPING ANIMATION (GIỮ AVATAR)
// =========================
const showTypingAnimation = () => {
    const div = document.createElement("div");
    div.className = "chat incoming";
    div.innerHTML = `
        <div class="chat-content">
            <div class="chat-details">
                <img src="/static/img/chatbot.jpg">
                <div class="typing-animation">
                    <span></span><span></span><span></span>
                </div>
                <p></p>
            </div>
        </div>
    `;
    chatContainer.appendChild(div);
    chatContainer.scrollTop = chatContainer.scrollHeight;

    getChatResponse(div);
};

// =========================
// SEND USER MESSAGE
// =========================
const handleOutgoingChat = () => {
    userText = chatInput.value.trim();
    if (!userText) return;

    chatInput.value = "";

    chatContainer.querySelector(".default-text")?.remove();

    const outgoing = createChatElement(userText, "outgoing");
    chatContainer.appendChild(outgoing);
    chatContainer.scrollTop = chatContainer.scrollHeight;

    setTimeout(showTypingAnimation, 300);
};

// =========================
// EVENTS
// =========================
sendButton.addEventListener("click", handleOutgoingChat);

chatInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        handleOutgoingChat();
    }
});

themeButton.addEventListener("click", () => {
    document.body.classList.toggle("light-mode");
    localStorage.setItem(
        "themeColor",
        document.body.classList.contains("light-mode")
            ? "light_mode"
            : "dark_mode"
    );
});

deleteButton.addEventListener("click", async () => {
    if (!confirm("Xóa cuộc trò chuyện hiện tại?")) return;

    await fetch("/reset-chat", { method: "POST" });
    chatContainer.innerHTML = `
        <div class="default-text">
            <h1>AI Chatbot</h1>
            <p>Tôi có thể giúp gì cho bạn hôm nay?</p>
        </div>
    `;
});
