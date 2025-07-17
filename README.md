# Social Media Post Generator From Audio

Generate engaging social-media copy straight from an audio recording ✨  
This project transcribes speech using OpenAI Whisper and turns the text into platform-specific posts with Google FLAN-T5.  A React + Vite front-end lets you record / upload audio and preview the generated posts in real-time, while a Flask back-end orchestrates transcription, generation and storage.

## Features

* 🔈 **Speech-to-Text** – Accurate multilingual transcription via Whisper.
* 🤖 **AI Copywriting** – FLAN-T5 converts transcripts into tailored posts for Twitter, LinkedIn, Instagram & more.
* 🎯 **Platform Templates** – Tone, length, hashtags & mentions optimised per platform.
* ♻️ **Regeneration & Editing** – Regenerate a single post with a new tone without re-transcribing.
* 📦 **Persistent Storage** – JSON file store keeps uploads, transcripts and generated posts.
* 🖥️ **Modern Front-End** – React, Vite, Tailwind-ready UI with drag-and-drop upload and progress feedback.
* 🔒 **CORS & Env Config** – Secure, environment-driven configuration for easy deployment.

## Project Structure

```
Social Media Post Generator from Audio/
├── backend/            # Flask API & AI services
│   ├── app.py          # Main Flask application
│   ├── services/       # Whisper, FLAN-T5, upload helpers, post templates
│   ├── models/         # Saved ML models / checkpoints
│   ├── templates/      # Social-platform prompt templates
│   └── requirements.txt
├── frontend/           # React (Vite) SPA
│   ├── src/            # Components, hooks, assets
│   ├── public/
│   └── package.json
├── uploads/            # Audio files, transcripts & generated posts (JSON)
├── .env.example        # Sample environment variables
├── .gitignore          # Ignores tests, caches, node_modules, etc.
├── run_backend.bat     # Convenience script (Windows)
├── setup.bat           # One-shot environment setup script
└── README.md           # You are here 👋
```

## Quick Start

### 1. Clone & Install
```bash
# clone your fork
$ git clone https://github.com/namm9an/Social-Media-Post-Generator-From-Audio.git
$ cd Social-Media-Post-Generator-From-Audio

# Python backend
$ python -m venv venv && source venv/bin/activate   # on Windows: venv\Scripts\activate
$ pip install -r backend/requirements.txt

# Node frontend
$ cd frontend
$ npm install
```

### 2. Environment Variables
Copy `.env.example` files and fill in as needed:
```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```
Key variables:
* `WHISPER_MODEL` – whisper model size (`base`, `small`, `medium`, `large`)
* `UPLOAD_FOLDER`, `DATA_FOLDER` – storage paths for audio & JSON
* `CORS_ORIGINS` – comma-separated allowed origins

### 3. Run Locally
```bash
# Terminal 1 – backend
$ python backend/app.py

# Terminal 2 – frontend
$ cd frontend && npm run dev
```
Visit `http://localhost:5173` and start generating posts!

## API Reference (Backend)
| Method | Endpoint | Purpose |
| ------ | -------- | ------- |
| POST   | `/api/upload`               | Upload audio file |
| POST   | `/api/transcribe`           | Start transcription (`file_id`) |
| GET    | `/api/transcription/:id`    | Poll transcription result |
| POST   | `/api/generate-posts`       | Generate posts from `transcription_id` + platform list |
| POST   | `/api/regenerate`           | (Re)generate a single post with a new tone |
| GET    | `/api/posts/:id`            | Retrieve previously generated posts |
| GET    | `/api/health`               | Simple service health check |

All responses are JSON; see `backend/app.py` for schemas.

## Running Tests
Test files are excluded from the public repository for brevity.  Locally you can run:
```bash
pytest
```

## Deployment
The app is platform-agnostic; you can deploy backend & frontend separately (e.g. Render + Netlify) or together via Docker.

### Docker (optional)
```bash
# build
$ docker compose up --build
```
*(A sample `docker-compose.yml` is left to you as an exercise.)*

## Contributing
Pull requests welcome!  Please open an issue first to discuss what you would like to change.

1. Fork the repo
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Open a PR 🚀

## License
[MIT](LICENSE)
