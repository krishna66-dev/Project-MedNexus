# 🏥 MedNexus - SIH 2026: Merged Frontend + Flask Backend

![SIH Badge](https://img.shields.io/badge/Smart_India_Hackathon-2026-blue)
![Framework](https://img.shields.io/badge/Frontend-SvelteKit-ff3e00?logo=svelte)
![Backend](https://img.shields.io/badge/Backend-Flask-000000?logo=flask)

> **Empowering healthcare triage through intelligent systems and unified front-backend integration.**

MedNexus is a streamlined patient verification and medical triage platform designed for the Smart India Hackathon 2026. The UI utilizes the custom MedNexus design supplied for the project, perfectly integrated with a powerful backend triage engine.

---

## ⚙️ Tech Stack
*   **Frontend:** SvelteKit, Vite
*   **Backend:** Python, Flask (`app11.py`)
*   **Database:** PostgreSQL

---

## 🚀 Installation & Setup

This repository contains the merged SvelteKit frontend and Flask backend. Follow these instructions carefully to ensure the API and triage engine communicate correctly.

### 1. Clone the Repository
```bash
git clone [https://github.com/krishna66-dev/MedNexus-SIH-2026.git](https://github.com/krishna66-dev/MedNexus-SIH-2026.git)
cd MedNexus-SIH-2026

2. Backend Setup
The Flask backend (app11.py) is responsible for maintaining PostgreSQL patient verification and running the core existing triage engine.
  (i)  Navigate to the backend directory:
         cd backend
  (ii) Install necessary Python dependencies (ensure your virtual environment is active if you use one):
          pip install -r requirements.txt
  (iii) Run the application using the specific execution file:
         python app11.py

The backend will now be running at: http://127.0.0.1:5000
(Note: The Flask backend is configured to accept the Vite origin through the FRONTEND_URL environment variable, which defaults to http://localhost:5173).

3. Frontend Setup
The frontend leverages SvelteKit and connects to the Flask backend's / verification and /triage endpoints.
(i) Open a new terminal and navigate to your frontend directory.
(ii) Install Node dependencies:
     npm install
(iii) Crucial Route Setup: Ensure you replace your SvelteKit route file with the correct layout:
      src/routes/+page.svelte
(iv) Environment Variables: Create a .env file in the frontend root directory to link the Vite app to the Flask API:
     Code snippet
     VITE_API_URL=[http://127.0.0.1:5000](http://127.0.0.1:5000)
(v) Start the SvelteKit development server:
    Bash
    npm run dev

⚠️ Important Triage Logic & Architecture
To maintain medical accuracy, the existing Flask triage engine remains the absolute decision source. Please note the following architectural rules:

 • No Client-Side Evaluation: The Svelte UI no longer uses its old local severity function for normal triage. Instead, it submits all symptoms directly to Flask for evaluation.

 • Pain-Safety Protocol: Pain-related cases can enter the existing Flask pain-safety flow. The current Svelte merge detects that specific path and actively asks the user to continue through the backend safety step, rather than inventing a new medical rule on the client side.
