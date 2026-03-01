# ContentCraft AI

> **Dual-agent AI platform that turns a brand brief into a complete YouTube content pack in under 60 seconds.**

Built for the **lablab.ai Hackathon** · Powered by GPT-4 + DALL-E 3

---

## What It Does

Fill out one intake form with your brand details and topic. Two AI agents take it from there:

| Agent | Role | Technology |
|-------|------|-----------|
| **Agent 1** | Generates title, script, description, hashtags | GPT-4 |
| **Agent 2** | Creates 3 thumbnail variants | DALL-E 3 + Pillow |

The result is a downloadable **ZIP pack** containing everything you need to publish a YouTube video — ready in seconds.

### Output includes:
- YouTube-optimised video title (60 char limit)
- Full video script with timestamps
- SEO-optimised description (150–200 words)
- 10 relevant hashtags
- 3 thumbnail variants (AI-generated, brand-coloured, minimalist)
- Optimisation tips and publishing checklist

---

## Architecture

```
User (Intake Form)
        │
        ▼
  Flask API (main-app.py)
        │
        ▼
  AgentOrchestrator
    ├── Agent 1 (GPT-4)  ──► Redis (job store)
    │                                │
    └── Agent 2 (DALL-E 3) ◄─────────┘
        │
        ▼
  Pack Assembler ──► ZIP Download
```

Agents communicate via **Redis**. The orchestrator runs Agent 2 in a background thread after Agent 1 completes.

---

## Quick Start

### Prerequisites
- Docker & Docker Compose
- OpenAI API key

### 1. Clone and configure

```bash
git clone <your-repo-url>
cd contentcraft-ai
cp .env.example .env
# Add your API keys to .env
```

### 2. Start all services

```bash
docker-compose up --build -d
```

This starts:
- **Flask app** on port 5000 (4 Gunicorn workers)
- **Redis** on port 6379
- **Nginx** reverse proxy on ports 80/443

### 3. Open the app

```
http://localhost:5000
```

### 4. Run validation suite

```bash
pip install aiohttp
python final-validation.py
```

---

## Local Development (no Docker)

```bash
pip install -r updated-requirements.txt
export OPENAI_API_KEY=sk-your-key-here

# Start Redis (required)
redis-server

# Start the app
python main-app.py
```

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | Your OpenAI API key (GPT-4 + DALL-E 3) |
| `YOUTUBE_API_KEY` | Optional | YouTube Data API v3 (for live hashtag trends) |
| `SECRET_KEY` | Yes | Flask secret key for sessions |
| `REDIS_URL` | No | Defaults to `redis://localhost:6379/0` |

---

## Project Structure

```
contentcraft-ai/
├── agent1-youtube-generator.py   # Agent 1: GPT-4 content generation
├── agent2-visual-generator.py    # Agent 2: DALL-E 3 + Pillow thumbnails
├── agent-orchestrator.py         # Coordinates agent workflow via Redis
├── main-app.py                   # Flask web app (main entry point)
├── optimized-main-app.py         # Production-optimised Flask app
├── social-pack-assembler.py      # Bundles content + visuals into ZIP
├── final-validation.py           # Production readiness test suite
├── integration-test-suite.py     # End-to-end integration tests
├── workflow-optimizer.py         # Performance tuning utilities
├── index.html                    # Main intake form UI
├── complete-ui-interface.html    # Self-contained demo UI (no backend needed)
├── pack-viewer.html              # Results viewer
├── Dockerfile                    # Container definition
├── docker-compose.yml            # Multi-service orchestration
├── nginx.conf                    # Reverse proxy + rate limiting
├── updated-requirements.txt      # Python dependencies
├── .env.example                  # Environment variable template
└── deployment-guide.md           # Full deployment instructions
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Intake form UI |
| `GET` | `/health` | System health check |
| `POST` | `/api/generate-content` | Run Agent 1 (text content) |
| `POST` | `/api/generate-visuals` | Run Agent 2 (thumbnails) |
| `POST` | `/api/generate` | Full pipeline (content + visuals + pack) |
| `GET` | `/api/download/<pack_id>` | Download ZIP pack |
| `GET` | `/api/metrics` | Performance metrics |

---

## Tech Stack

- **AI**: OpenAI GPT-4, DALL-E 3
- **Backend**: Python 3.11, Flask, Gunicorn
- **Storage**: Redis (job state, agent communication)
- **Image Processing**: Pillow
- **Infrastructure**: Docker, Nginx (SSL + rate limiting)
- **Testing**: aiohttp async test suite

---

## Hackathon Context

Built in 5 days for the **lablab.ai AI Agents Hackathon**.

**Day 1** — Agent 1 + intake form
**Day 2** — Agent 2 + orchestrator + Redis pipeline
**Day 3** — Pack assembler + Flask app + UI
**Day 4** — Integration tests + performance optimisation
**Day 5** — Docker deployment + Nginx + final validation

---

## License

MIT
