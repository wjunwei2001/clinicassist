# ClinicAssist Frontend Setup

This is the Next.js frontend for ClinicAssist, a clinical triage assistant application.

## Prerequisites

- Node.js 18+ installed
- Backend FastAPI server running on `http://localhost:8000`

## Installation

1. Install dependencies:
```bash
cd frontend
npm install
```

2. (Optional) Configure the backend API URL:

Create a `.env.local` file in the frontend directory:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

By default, the app connects to `http://localhost:8000`. Change this if your backend is running elsewhere.

## Running the Application

### Development Mode

1. **Start the backend first** (in a separate terminal):
```bash
cd ..
python src/main.py
```
This starts the FastAPI server on `http://localhost:8000`

2. **Start the frontend**:
```bash
npm run dev
```
The frontend will be available at `http://localhost:3000`

### Production Build

```bash
npm run build
npm start
```

## Features

- **Start Button**: Initiates a new conversation session with the backend
- **Chat Interface**: Real-time conversation with the clinical assistant
- **Live Sidebar**: Shows extracted information as the conversation progresses:
  - Patient demographics (name, age, sex)
  - Symptoms (main, onset, associated, additional info)
  - Medical history facts
  - Triage summary (diagnosis, urgency level)
  - Current phase indicator

## Architecture

The frontend communicates with the FastAPI backend via REST API:

- `POST /api/chat/start` - Start a new session
- `POST /api/chat/reply` - Send user messages and receive responses

The backend handles all LangGraph workflow logic, while the frontend focuses on UI/UX.

## Tech Stack

- **Next.js 15** with App Router
- **React 19**
- **TypeScript**
- **Tailwind CSS 4**
- **Client-side rendering** for real-time interactivity

## Troubleshooting

**Issue**: "Failed to start conversation"
- **Solution**: Make sure the backend is running on `http://localhost:8000`
- Check that CORS is enabled in the backend (already configured in `main.py`)

**Issue**: Connection refused
- **Solution**: Verify the backend FastAPI server is running
- Run `python src/main.py` from the project root

**Issue**: Environment variables not loading
- **Solution**: Restart the dev server after creating/modifying `.env.local`

