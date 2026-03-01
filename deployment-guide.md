# Content Generation Platform — Deployment Guide

## Prerequisites
- Docker & Docker Compose installed
- OpenAI API key
- YouTube Data API v3 key
- Domain with SSL certificate (for production)

---

## Environment Setup

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=sk-your-openai-key
YOUTUBE_API_KEY=your-youtube-api-key
SECRET_KEY=your-secure-random-secret
FLASK_ENV=production
```

---

## Deployment Steps

### 1. Clone & Configure
```bash
git clone <repo-url>
cd content-platform
cp .env.example .env
# Fill in your API keys in .env
```

### 2. SSL Certificates
```bash
mkdir -p nginx/ssl
# Place your cert.pem and key.pem in nginx/ssl/
# For local testing, generate self-signed:
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/key.pem -out nginx/ssl/cert.pem
```

### 3. Build & Launch
```bash
docker-compose up --build -d
```

### 4. Run Final Validation
```bash
pip install aiohttp
python final-validation.py
```

### 5. Monitor Logs
```bash
docker-compose logs -f web
docker-compose logs -f redis
```

---

## API Endpoints Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | System health check |
| POST | `/api/validate-form` | Validate intake form |
| POST | `/api/generate-content` | Agent 1 — content generation |
| POST | `/api/generate-visuals` | Agent 2 — visual generation |
| POST | `/api/generate` | Full pipeline (content + visuals + pack) |
| GET | `/api/download/<pack_id>` | Download ZIP pack |
| GET | `/api/metrics` | Performance metrics |
| DELETE | `/api/cache` | Clear Redis cache |

---

## Workflow Summary

```
User Input (Intake Form)
        ↓
  Agent 1 (YouTube Content)
  • Title, Description, Script
  • Hashtags (YouTube Data API)
        ↓
  Agent 2 (Visual Generator)
  • 3 Thumbnail Variants
  • Brand Color Application
  • DALL-E Image Generation
        ↓
  Pack Assembler
  • ZIP Bundle (content + visuals)
  • Optimization Tips
  • Publishing Checklist
        ↓
  User Downloads YouTube Pack
```

---

## Scaling Considerations (Post-MVP)
- Increase Gunicorn workers for higher concurrency
- Add Celery for async task queuing
- Integrate TikTok & Instagram APIs
- Add user authentication & saved packs history
- Implement real-time hashtag trend scoring
