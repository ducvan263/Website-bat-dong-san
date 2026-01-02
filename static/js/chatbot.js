const chatInput = document.querySelector("#chat-input");
const sendButton = document.querySelector("#send-btn");
const chatContainer = document.querySelector(".chat-container");
const themeButton = document.querySelector("#theme-btn");
const deleteButton = document.querySelector("#delete-btn");

let userText = "";

// =========================
// LOAD LOCAL STORAGE
// =========================
const loadDataFromLocalstorage = () => {
    const themeColor = localStorage.getItem("themeColor");

    document.body.classList.toggle("light-mode", themeColor === "light_mode");
    themeButton.innerText = document.body.classList.contains("light-mode")
        ? "dark_mode"
        : "light_mode";

    const defaultText = `
        <div class="default-text">
            <h1>Chat Bot</h1>
            <p>Nhập câu hỏi để bắt đầu trò chuyện.</p>
        </div>`;

    chatContainer.innerHTML =
        localStorage.getItem("all-chats") || defaultText;

    chatContainer.scrollTo(0, chatContainer.scrollHeight);
};

// =========================
// CREATE CHAT ELEMENT
// =========================
const createChatElement = (content, className) => {
    const chatDiv = document.createElement("div");
    chatDiv.classList.add("chat", className);
    chatDiv.innerHTML = content;
    return chatDiv;
};

// =========================
// CALL BACKEND (FLASK)
// =========================
const getChatResponse = async (incomingChatDiv) => {
    const pElement = document.createElement("p");

    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: userText })
        });

        const data = await response.json();

        // ✅ ĐÚNG FORMAT BACKEND
        pElement.textContent = data.reply;

    } catch (error) {
        console.error(error);
        pElement.classList.add("error");
        pElement.textContent = "Không thể kết nối AI";
    }

    incomingChatDiv.querySelector(".typing-animation")?.remove();
    incomingChatDiv.querySelector(".chat-details").appendChild(pElement);

    localStorage.setItem("all-chats", chatContainer.innerHTML);
    chatContainer.scrollTo(0, chatContainer.scrollHeight);
};

// =========================
// TYPING ANIMATION
// =========================
const showTypingAnimation = () => {
    const html = `
        <div class="chat-content">
            <div class="chat-details">
                <img src="/static/img/chatbot.jpg" alt="bot">
                <div class="typing-animation">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            </div>
        </div>`;

    const incomingChatDiv = createChatElement(html, "incoming");
    chatContainer.appendChild(incomingChatDiv);
    chatContainer.scrollTo(0, chatContainer.scrollHeight);

    getChatResponse(incomingChatDiv);
};

// =========================
// HANDLE USER MESSAGE
// =========================
const handleOutgoingChat = () => {
    userText = chatInput.value.trim();
    if (!userText) return;

    chatInput.value = "";

    const html = `
        <div class="chat-content">
            <div class="chat-details">
                <img src="/static/img/user.jpg" alt="user">
                <p>${userText}</p>
            </div>
        </div>`;

    const outgoingChatDiv = createChatElement(html, "outgoing");
    chatContainer.querySelector(".default-text")?.remove();
    chatContainer.appendChild(outgoingChatDiv);
    chatContainer.scrollTo(0, chatContainer.scrollHeight);

    setTimeout(showTypingAnimation, 300);
};

// =========================
// EVENTS
// =========================
deleteButton.addEventListener("click", async () => {
    if (confirm("Xóa toàn bộ lịch sử chat?")) {
        await fetch("/reset-chat", { method: "POST" });
        localStorage.removeItem("all-chats");
        loadDataFromLocalstorage();
    }
});

themeButton.addEventListener("click", () => {
    document.body.classList.toggle("light-mode");
    localStorage.setItem("themeColor", themeButton.innerText);
    themeButton.innerText = document.body.classList.contains("light-mode")
        ? "dark_mode"
        : "light_mode";
});

chatInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        handleOutgoingChat();
    }
});

sendButton.addEventListener("click", handleOutgoingChat);

loadDataFromLocalstorage();
