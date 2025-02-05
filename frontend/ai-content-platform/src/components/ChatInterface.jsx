import React, { useState, useEffect } from "react";
import axios from "axios";
import { v4 as uuidv4 } from "uuid"; // 🔥 Import UUID generator
axios.defaults.withCredentials = true;

const ChatInterface = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [convoId, setConvoId] = useState(null); // Store convo_id

  useEffect(() => {
    // Retrieve existing convo_id or generate a new one
    let savedConvoId = localStorage.getItem("convo_id");

    if (!savedConvoId) {
      savedConvoId = uuidv4(); // Generate new convo_id
      localStorage.setItem("convo_id", savedConvoId);
    }
    setConvoId(savedConvoId);
  }, []);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { sender: "user", text: input };
    setMessages([...messages, userMessage]); // Add user message to chat

    try {
      const response = await axios.post("http://127.0.0.1:8080/api/chat", {
        message: input,
        convo_id: convoId, // ✅ Send convo_id with request
      });

      const botMessage = { sender: "bot", text: response.data.message };
      setMessages([...messages, userMessage, botMessage]);
    } catch (error) {
      console.error("Error sending message:", error);
      setMessages([...messages, { sender: "bot", text: "Something went wrong. Try again." }]);
    }

    setInput(""); // Clear input field
  };

  const startNewConversation = () => {
    const newConvoId = uuidv4(); // 🔥 Generate new convo_id
    setConvoId(newConvoId);
    localStorage.setItem("convo_id", newConvoId);
    setMessages([]); // Clear chat history
  };

  return (
    <div className="chat-container">
      <div className="chat-box">
        {messages.map((msg, index) => (
          <div key={index} className={msg.sender === "user" ? "user-msg" : "bot-msg"}>
            {msg.text}
          </div>
        ))}
      </div>

      <div className="input-container">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message..."
        />
        <button onClick={sendMessage}>Send</button>
      </div>

      <button className="new-chat-btn" onClick={startNewConversation}>
        🔄 Start New Chat
      </button>
    </div>
  );
};

export default ChatInterface;
