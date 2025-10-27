const chatToggle = document.getElementById("chat-toggle");
const chatPopup = document.getElementById("chat-popup");
const closeChat = document.getElementById("close-chat");
const input = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");
const chatBox = document.getElementById("chat-box");

let sessionId = null;

// Toggle chat popup visibility
chatToggle.addEventListener("click", () => {
  chatPopup.style.display = "flex";
  chatToggle.style.display = "none";
});

closeChat.addEventListener("click", () => {
  chatPopup.style.display = "none";
  chatToggle.style.display = "block";
});

// Add messages to the chat box
function addMessage(text, className) {
  const msg = document.createElement("div");
  msg.className = className;
  msg.innerHTML = text;
  chatBox.appendChild(msg);
  chatBox.scrollTop = chatBox.scrollHeight;
  return msg;
}

// Send message to backend
async function sendMessage() {
  const message = input.value.trim();
  if (!message) return;

  addMessage(message, "user-msg");
  input.value = "";

  const typingDiv = addMessage("Typing...", "bot-msg typing");

  try {
    const response = await fetch("http://127.0.0.1:8000/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, session_id: sessionId }),
    });

    const data = await response.json();
    sessionId = data.session_id;

    typingDiv.remove();
    addMessage(data.response, "bot-msg");
  } catch (error) {
    typingDiv.remove();
    addMessage("Oops! Something went wrong. Please try again.", "bot-msg");
    console.error("[Frontend Error]", error);
  }
}

// Event listeners
sendBtn.addEventListener("click", sendMessage);
input.addEventListener("keypress", (e) => {
  if (e.key === "Enter") sendMessage();
});
