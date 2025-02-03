import React, { useState, useEffect } from "react";
import axios from "axios";
import "./ContentSubscriptions.css";

const ContentSubscriptions = ({ onViewSubscription }) => {
  const [subscriptions, setSubscriptions] = useState([]);
  const [loading, setLoading] = useState(false);

  // Fetch subscriptions from the backend
  useEffect(() => {
    const fetchSubscriptions = async () => {
      setLoading(true);
      try {
        const response = await axios.get("http://localhost:5000/api/subscriptions");
        setSubscriptions(response.data); // Array of subscriptions
      } catch (error) {
        console.error("Error fetching subscriptions:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchSubscriptions();
  }, []);

  // Handle viewing a subscription
  const handleView = async (subscription) => {
    setLoading(true);
    try {
      // Simulate job start (view content in Content Theatre)
      onViewSubscription(subscription); // Pass the subscription to Content Theatre
    } catch (error) {
      console.error("Error viewing subscription:", error);
    } finally {
      setLoading(false);
    }
  };

  // Handle deleting a subscription
  const handleDelete = async (subscriptionId) => {
    try {
      await axios.delete(`http://localhost:5000/api/subscriptions/${subscriptionId}`);
      setSubscriptions(subscriptions.filter((sub) => sub.id !== subscriptionId));
    } catch (error) {
      console.error("Error deleting subscription:", error);
    }
  };

  // Handle disabling a subscription
  const handleDisable = async (subscriptionId) => {
    try {
      await axios.post(`http://localhost:5000/api/subscriptions/${subscriptionId}/disable`);
      setSubscriptions(
        subscriptions.map((sub) =>
          sub.id === subscriptionId ? { ...sub, disabled: true } : sub
        )
      );
    } catch (error) {
      console.error("Error disabling subscription:", error);
    }
  };

  return (
    <div className="content-subscriptions">
      <h2>Content Subscriptions</h2>
      {loading && <div className="loading">Loading...</div>}
      <ul>
        {subscriptions.map((sub) => (
          <li key={sub.id} className={sub.disabled ? "disabled" : ""}>
            <div className="subscription-details">
              <span>{sub.name}</span>
            </div>
            <div className="subscription-actions">
              <button onClick={() => handleView(sub)}>View</button>
              <button onClick={() => handleDisable(sub.id)}>
                {sub.disabled ? "Enable" : "Disable"}
              </button>
              <button onClick={() => handleDelete(sub.id)}>Delete</button>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default ContentSubscriptions;
