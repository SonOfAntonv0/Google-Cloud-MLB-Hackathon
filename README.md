# **MLB Fan Personalized Highlight System - README**

## **📌 Overview**
This system allows MLB fans to receive **personalized highlight clips** based on their favorite **players, teams, and plays**. Users can subscribe to **on-demand** or **scheduled** delivery of highlights and receive **AI-generated insights** along with video content.

- **💡 AI-powered insights**: Summarizes highlights with AI-based analysis.
- **🎥 Video delivery**: Users receive highlight clips with translated commentary.
- **⏰ Flexible subscriptions**: Users can get content on-demand or via a scheduled system.
- **📩 Email notifications**: Users are notified when content is available.

---

# **🖥️ Backend API**
The backend is a **Flask-SocketIO server** running on **Google Cloud App Engine (Flex)**, utilizing **Google Firestore, Pub/Sub, and Cloud Storage** for content delivery.

## **🔄 Public API Endpoints**
All requests should be sent to:

```
https://v2-flex-dot-cloud-hackathon-venky.ue.r.appspot.com
```

### **1️⃣ Chatbot Interface**
Handles user interactions and stores conversations in Firestore.

#### **POST** `/api/chat`
- **Purpose**: Handles user queries and responses.
- **Request Body**:
  ```json
  {
    "message": "Hello",
    "convo_id": "4e21ac56-1111-2222-3333-4444abcdef"
  }
  ```
- **Response**:
  ```json
  {
    "message": "Thanks for your interest! Would you like on-demand or scheduled highlights?"
  }
  ```

---

### **2️⃣ Content Delivery**
Handles retrieving and processing video content.

#### **GET** `/api/content-theatre`
- **Purpose**: Fetches the latest available highlight video and AI insights.
- **Response** (when content is available):
  ```json
  {
    "videoUrl": "https://storage.googleapis.com/homeruns-top-players/Ohtani_highlight.mp4",
    "insightsUrl": "https://storage.googleapis.com/homeruns-top-players/Ohtani_insights.json"
  }
  ```
- **Response** (when no content is available):
  ```json
  {
    "error": "No content available yet"
  }
  ```

---

### **3️⃣ Subscription Management**
Handles user highlight subscriptions.

#### **GET** `/api/subscriptions`
- **Purpose**: Lists all user subscriptions.
- **Response**:
  ```json
  [
    {"id": "1", "name": "Shohei Ohtani Home Runs", "disabled": false},
    {"id": "2", "name": "Top MLB Moments 2023", "disabled": false}
  ]
  ```

#### **POST** `/api/subscriptions/<subscription_id>/disable`
- **Purpose**: Disables a subscription.
- **Response**:
  ```json
  {"message": "Subscription 1 disabled"}
  ```

#### **DELETE** `/api/subscriptions/<subscription_id>`
- **Purpose**: Deletes a subscription.
- **Response**:
  ```json
  {"message": "Subscription 1 deleted"}
  ```

---

### **4️⃣ Pub/Sub Event Listener**
Processes scheduled video jobs and triggers WebSocket events.

#### **POST** `/pubsub`
- **Purpose**: Listens for Google Pub/Sub messages indicating a scheduled highlight job is ready.
- **Request**:
  ```json
  {
    "message": {
      "data": "eyJwbGF5ZXIiOiAiT2h0YW5pIiwgInBsYXkiOiAiaG9tZXJ1bnMiLCAiZGVsaXZlcnlfdHlwZSI6ICJzY2hlZHVsZWQiLCAidGltZSI6ICIyMDowMCIsICJkYXlfb2Zfd2VlayI6IDAsICJ0aW1lem9uZSI6ICJVVENfNiIsICJsYW5ndWFnZSI6ICJl
        bmdsaXNoIn0="
    }
  }
  ```
- **Triggers**:
  - Processes video
  - Saves the content URLs in Firestore
  - Emits a **WebSocket event (`content_ready`)** for real-time updates

---

### **5️⃣ WebSocket Events**
WebSockets are used for **real-time notifications** when content is ready.

- **Event: `"content_ready"`**
  - **Sent by backend** when a highlight is ready.
  - **Frontend receives**:
    ```json
    {
      "videoUrl": "https://storage.googleapis.com/homeruns-top-players/Ohtani_highlight.mp4",
      "insightsUrl": "https://storage.googleapis.com/homeruns-top-players/Ohtani_insights.json"
    }
    ```
- **Event: `"notification"`**
  - **Sent by backend** when a job is scheduled.
  - **Frontend receives**:
    ```json
    {
      "message": "Scheduled Job has been created!!"
    }
    ```

---

# **🌟 Frontend**
The frontend is a **React application** hosted on **Firebase Hosting**.

## **🔹 Components**
### **1️⃣ ChatInterface.jsx**
- The main **chatbot UI** where users interact to set up their preferences.
- Uses **`fetch` API** to talk to `/api/chat`.

### **2️⃣ ContentTheatre.jsx**
- Displays **video highlights and AI insights**.
- Listens for **WebSocket events** (`content_ready`).
- Calls `/api/content-theatre` when loaded.

### **3️⃣ Header.jsx**
- Displays navigation and user profile.
- Allows switching between **Chat and Content Theatre**.

### **4️⃣ Subscriptions.jsx**
- Lists user **subscriptions** and allows them to **disable or delete**.

---

# **🛠 Deployment**
### **Backend (App Engine)**
The backend is deployed on **Google App Engine (Flex)**:
```sh
gcloud app deploy
```

### **Frontend (Firebase Hosting)**
```sh
firebase deploy
```

---

# **📧 Email Notifications**
When a video is ready, an **email is sent** to the user with a link to the **Content Theatre**.

- Uses **SMTP (SendGrid)**
- Example email:
  ```
  Subject: Your Personalized MLB Highlights Are Ready!
  
  Your latest highlights for Shohei Ohtani are ready.
  
  Watch here: https://cloud-hackathon-venky.web.app/content-theatre
  ```

---

# **⚾ Summary**
- **Backend**: Flask-SocketIO, Firestore, Pub/Sub for scheduling, and Cloud Storage for video hosting.
- **Frontend**: React (Firebase Hosting) with WebSockets for real-time updates.
- **Subscriptions**: Users can receive **on-demand** or **scheduled highlights**.
- **Emails**: Users get notified via **SMTP** when content is ready.

---

This README provides a **full overview** of your **MLB Fan Personalized Highlight System**, including **APIs, WebSockets, frontend components, deployment details, and email notifications**. 🚀⚾

