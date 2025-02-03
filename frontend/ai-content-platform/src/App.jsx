import React, { useState } from "react";
import ChatInterface from "./components/ChatInterface";
import ContentTheatre from "./components/ContentTheatre";
import ContentSubscriptions from "./components/ContentSubscriptions";
import "./App.css";

function App() {
  const [currentTab, setCurrentTab] = useState("chat");
  const [contentForTheatre, setContentForTheatre] = useState(null);

  const handleViewSubscription = (subscription) => {
    setContentForTheatre(subscription); // Pass subscription to Content Theatre
    setCurrentTab("content-theatre");
  };

  return (
    <div className="app-container">
      <nav className="tab-navigation">
        <button
          className={currentTab === "chat" ? "active" : ""}
          onClick={() => setCurrentTab("chat")}
        >
          Chat
        </button>
        <button
          className={currentTab === "content-theatre" ? "active" : ""}
          onClick={() => setCurrentTab("content-theatre")}
        >
          Content Theatre
        </button>
        <button
          className={currentTab === "subscriptions" ? "active" : ""}
          onClick={() => setCurrentTab("subscriptions")}
        >
          Content Subscriptions
        </button>
      </nav>

      <div className="content">
        {currentTab === "chat" && <ChatInterface />}
        {currentTab === "content-theatre" && <ContentTheatre subscription={contentForTheatre} />}
        {currentTab === "subscriptions" && <ContentSubscriptions onViewSubscription={handleViewSubscription} />}
      </div>
    </div>
  );
}

export default App;
