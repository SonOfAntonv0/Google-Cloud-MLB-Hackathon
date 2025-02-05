import React, { useState, useEffect } from "react";
import axios from "axios";
import { io } from "socket.io-client";

// ✅ Force WebSocket transport to avoid polling issues
const socket = io("http://127.0.0.1:8080", {
  transports: ["websocket", "polling"], // Force WebSocket only
  reconnection: true,
  reconnectionAttempts: 5,
  reconnectionDelay: 3000,
  timeout: 400000
});

socket.on("connect", () => console.log("✅ Connected to WebSocket"));
socket.on("disconnect", () => console.log("🔴 Disconnected from WebSocket"));

const ContentTheatre = () => {
  const [videoUrl, setVideoUrl] = useState("");
  const [insights, setInsights] = useState("");
  const [notification, setNotification] = useState("");

  useEffect(() => {
    console.log("🔄 Connecting to WebSocket...");

    // ✅ Fetch existing content when component mounts
    axios.get(`http://127.0.0.1:8080/api/content-theatre`, { withCredentials: true })
      .then(async (response) => {
        setVideoUrl(response.data.videoUrl);
          console.log(`RESPONSEEEEEE ✅✅✅✅✅✅✅✅ ${JSON.stringify(response)}`)
        if (response.data.insightsUrl) {
          const insightsResponse = await axios.get(response.data.insightsUrl, { withCredentials: false });
          setInsights(insightsResponse.data.response);
        }
      })
      .catch((error) => {
        console.error("❌ Error fetching content:", error);
      });

    // ✅ Listen for new content being ready
    socket.on("content_ready", async (data) => {
      console.log("🎬 New content received:", data);

      setVideoUrl(data.videoUrl);
      try {
        const insightsResponse = await axios.get(data.insightsUrl);
        setInsights(insightsResponse.data.response);
      } catch (err) {
        console.error("❌ Error fetching insights:", err);
      }
    });

    return () => {
      socket.off("content_ready");
    };
  }, []);

  const formatInsights = (text) => {
    // Split text into sections based on "**" markers
    return text.split('**').map((section, index) => {
      // Check if this is a title section (every odd index)
      const isTitle = index % 2 === 1;
      return (
        <span key={index} className={isTitle ? 'insight-title' : 'insight-content'}>
          {section}
        </span>
      );
    });
  };

  return (
    <div className="content-theatre">
      <h2>Content Theatre</h2>

      {notification && <p className="notification">{notification}</p>}

      {videoUrl ? (
        <video controls>
          <source src={videoUrl} type="video/mp4" />
          Your browser does not support the video tag.
        </video>
      ) : (
        <p>Loading video...</p>
      )}

{insights ? (
        <div className="ai-insights">
          <h3 className="insights-title">AI Insights</h3>
          <div className="insights-content">
            {formatInsights(insights)}
          </div>
        </div>
      ) : (
        <p className="loading-spinner">Loading insights...</p>
      )}
    </div>
  );
};

export default ContentTheatre;
