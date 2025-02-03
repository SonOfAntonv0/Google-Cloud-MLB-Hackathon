import React, { useState, useEffect } from "react";
import { io } from "socket.io-client";

// ✅ Force WebSocket transport to avoid polling issues
const socket = io("https://cloud-hackathon-venky.ue.r.appspot.com", {
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

    // ✅ Fetch existing content when component mounts using fetch
    fetch(`/api/content-theatre`)
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
      })
      .then(async (data) => {
        setVideoUrl(data.videoUrl);

        if (data.insightsUrl) {
          try {
            const insightsResponse = await fetch(data.insightsUrl);
            if (!insightsResponse.ok) {
              throw new Error(`HTTP error! Status: ${insightsResponse.status}`);
            }
            const insightsData = await insightsResponse.json();
            setInsights(insightsData.response);
          } catch (err) {
            console.error("❌ Error fetching insights:", err);
          }
        }
      })
      .catch(error => console.error("❌ Error fetching content:", error));

    // ✅ Listen for new content being ready
    socket.on("content_ready", async (data) => {
      console.log("🎬 New content received:", data);

      setVideoUrl(data.videoUrl);
      try {
        const insightsResponse = await fetch(data.insightsUrl);
        if (!insightsResponse.ok) {
          throw new Error(`HTTP error! Status: ${insightsResponse.status}`);
        }
        const insightsData = await insightsResponse.json();
        setInsights(insightsData.response);
      } catch (err) {
        console.error("❌ Error fetching insights:", err);
      }
    });

    return () => {
      socket.off("content_ready");
    };
  }, []);

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
          <h3>AI Insights</h3>
          <p>{insights}</p>
        </div>
      ) : (
        <p>Loading insights...</p>
      )}
    </div>
  );
};

export default ContentTheatre;
