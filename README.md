# YuvaAI — AI-Powered Conversational Assistant

<p align="center">
  <img src="frontend/assets/yuvaai-logo.png" alt="YuvaAI Logo" width="120">
</p>

<h3 align="center">Your AI Companion. Intelligent Conversations, Simplified.</h3>

<p align="center">
  An AI-powered conversational platform combining intelligent responses, secure authentication and persistent conversation management.
</p>

<p align="center">
  <a href="https://yuvaai-production.up.railway.app/">
    <strong>🌐 Live Demo</strong>
  </a>
  &nbsp; | &nbsp;
  <a href="https://github.com/s-aryan08/UII">
    <strong>💻 GitHub Repository</strong>
  </a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white">
  <img src="https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge&logo=fastapi&logoColor=white">
  <img src="https://img.shields.io/badge/PostgreSQL-Database-4169E1?style=for-the-badge&logo=postgresql&logoColor=white">
  <img src="https://img.shields.io/badge/Groq-AI_Inference-F55036?style=for-the-badge">
  <img src="https://img.shields.io/badge/Deployed-Railway-8B5CF6?style=for-the-badge&logo=railway&logoColor=white">
</p>

---

## Overview

**YuvaAI** is a web-based AI conversational assistant designed to deliver an intelligent, secure and seamless user experience.

Built with Python, FastAPI, PostgreSQL and Groq, the platform combines AI inference with user authentication, conversation persistence and usage management.

YuvaAI provides an interactive environment where users can create accounts, communicate with an AI assistant, manage conversations and access their previous chat history.

The project focuses on combining a lightweight frontend with a modular Python backend and a persistent database architecture.

<img width="1918" height="925" alt="image 1" src="https://github.com/user-attachments/assets/ab5fda3d-0575-4ae1-8d25-816984c6226a" />


<img width="1919" height="922" alt="image 2" src="https://github.com/user-attachments/assets/42cc70c3-cb37-41e0-a4a3-3a8906add3ef" />






## Live Application

**Try YuvaAI here:**

### https://yuvaai-production.up.railway.app/

The application is deployed on Railway, with its FastAPI backend serving the web interface and communicating with PostgreSQL and the Groq API.

---

## Key Features

### 🤖 AI-Powered Conversations

- Intelligent natural-language responses.
- Groq-powered AI inference.
- Integration with the `openai/gpt-oss-20b` model.
- Context-aware conversation handling.
- Configurable response generation.
- Standard and streaming chat API support.

### 🔐 Authentication and Security

- User registration and login.
- JWT-based authentication.
- HTTP-only authentication cookies.
- Argon2 password hashing.
- CSRF protection for state-changing requests.
- Protected user-specific resources.
- Configurable authentication session expiration.

### 💬 Conversation Management

- Create new conversations.
- Persistent conversation history.
- Retrieve previous messages.
- Delete conversations.
- Individual conversation ownership.
- Database-backed message storage.

### ⚡ Usage Management

- Daily message limits.
- Per-minute request limits.
- Database-backed usage tracking.
- User-specific usage records.
- Server-side request validation.

### 🎨 Modern User Interface

- Responsive web interface.
- Light and dark themes.
- Markdown-rendered AI responses.
- Code syntax highlighting.
- Interactive conversation sidebar.
- Clean and accessible chat experience.

---

## Technology Stack

| Component | Technology |
|---|---|
| Frontend | HTML5, CSS3, JavaScript |
| Backend | Python, FastAPI |
| AI Inference | Groq API |
| AI Model | OpenAI GPT-OSS 20B |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Authentication | JWT |
| Password Hashing | Argon2 |
| Database Migrations | Alembic |
| HTTP Client | HTTPX |
| Application Server | Uvicorn |
| Cloud Deployment | Railway |
| Version Control | Git and GitHub |

---

## System Architecture

YuvaAI follows a modular client-server architecture in which the frontend communicates with the FastAPI backend through REST APIs.

The backend coordinates authentication, conversation management, AI inference and database operations.

```text
                       ┌──────────────────────┐
                       │        USER          │
                       └──────────┬───────────┘
                                  │
                                  ▼
                       ┌──────────────────────┐
                       │   YUVAAI FRONTEND    │
                       │                      │
                       │    HTML / CSS / JS   │
                       └──────────┬───────────┘
                                  │
                              REST API
                                  │
                                  ▼
                       ┌──────────────────────┐
                       │    FASTAPI BACKEND   │
                       │                      │
                       │   Authentication     │
                       │   Chat Services      │
                       │   Conversation APIs  │
                       │   Usage Management   │
                       └──────────┬───────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
                    ▼                           ▼
          ┌──────────────────┐       ┌──────────────────┐
          │    PostgreSQL    │       │     GROQ API     │
          │                  │       │                  │
          │  Users           │       │  AI Inference    │
          │  Conversations   │       │  GPT-OSS 20B     │
          │  Messages        │       │  Response        │
          │  Usage Records   │       │  Generation      │
          └──────────────────┘       └──────────────────┘
```

### Deployment Architecture

```text
                 ┌──────────────────────┐
                 │       GitHub         │
                 │    Source Code       │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │       Railway        │
                 │                      │
                 │    YuvaAI Service    │
                 │                      │
                 │  ┌────────────────┐  │
                 │  │   Frontend     │  │
                 │  ├────────────────┤  │
                 │  │ FastAPI Backend│  │
                 │  └────────────────┘  │
                 └──────────┬───────────┘
                            │
                   ┌────────┴────────┐
                   │                 │
                   ▼                 ▼
          ┌────────────────┐  ┌────────────────┐
          │   PostgreSQL   │  │    Groq API    │
          │  Persistence   │  │  AI Inference  │
          └────────────────┘  └────────────────┘
```

---

## Project Structure

```text
YuvaAI/
│
├── backend/
│   │
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── auth_routes.py
│   │   ├── auth_service.py
│   │   ├── dependencies.py
│   │   ├── schemas.py
│   │   └── security.py
│   │
│   ├── __init__.py
│   ├── ai_engine.py
│   ├── chat_service.py
│   ├── config.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   └── usage_service.py
│
├── frontend/
│   ├── assets/
│   │   └── yuvaai-logo.png
│   ├── index.html
│   ├── style.css
│   └── app.js
│
├── migrations/
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
│
├── alembic.ini
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## API Reference

YuvaAI provides REST API endpoints for authentication, conversations, chat operations and application monitoring.

### Authentication APIs

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/auth/csrf` | Generate CSRF token |
| POST | `/api/auth/register` | Register a new user |
| POST | `/api/auth/login` | Authenticate a user |
| GET | `/api/auth/me` | Retrieve authenticated user |
| POST | `/api/auth/logout` | Terminate user session |

### Conversation APIs

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/conversations` | Create a conversation |
| GET | `/api/conversations` | Retrieve user conversations |
| GET | `/api/conversations/{id}` | Retrieve conversation history |
| DELETE | `/api/conversations/{id}` | Delete a conversation |

### AI Chat APIs

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/chat` | Generate an AI response |
| POST | `/api/chat/stream` | Generate a streaming response |

### Monitoring APIs

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Check application health |

---

## Database Architecture

YuvaAI uses PostgreSQL for persistent storage and SQLAlchemy as its ORM.

The primary database models include:

| Model | Responsibility |
|---|---|
| User | Stores user account and authentication information |
| Conversation | Stores user-owned conversations |
| Message | Stores conversation messages |
| UsageRecord | Tracks daily user message usage |
| UsageEvent | Tracks individual request events |

Database schema changes are managed through Alembic migrations.

---

## Environment Configuration

YuvaAI uses environment variables for configuration and secure credential management.

The deployment environment requires the following variables:

| Variable | Description |
|---|---|
| `DEBUG` | Application debug configuration |
| `GROQ_API_KEY` | Groq API authentication key |
| `GROQ_MODEL` | AI model identifier |
| `DATABASE_URL` | PostgreSQL database connection |
| `AUTH_SECRET_KEY` | JWT signing secret |
| `AUTH_TOKEN_EXPIRE_MINUTES` | Authentication token expiration |

Sensitive credentials are managed through the hosting platform's environment variable configuration.

**Security guidelines:**

- Never commit `.env` files.
- Never expose API keys or database credentials.
- Use a strong, randomly generated authentication secret.
- Keep production debug mode disabled.
- Use secure HTTPS connections for the public application.

---

## Deployment

YuvaAI is deployed using Railway with a connected PostgreSQL database.

### Deployment Components

| Service | Platform |
|---|---|
| Application Hosting | Railway |
| Frontend Delivery | FastAPI Static File Serving |
| Backend API | FastAPI |
| Database | Railway PostgreSQL |
| AI Inference | Groq |
| Source Code Management | GitHub |

### Deployment Configuration

The application is started using Uvicorn:

```bash
python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

Database migrations are managed using:

```bash
alembic upgrade head
```

Production credentials and configuration values are provided through Railway environment variables.

### Live Deployment

**Production URL:**  
https://yuvaai-production.up.railway.app/

---

## Security Considerations

Security is an important part of YuvaAI's application architecture.

The implementation includes:

- Argon2 password hashing.
- JWT-based authentication.
- HTTP-only authentication cookies.
- CSRF token validation.
- User-specific conversation ownership.
- Protected application resources.
- Environment-based secret management.
- Database-backed persistence.

---

## Future Roadmap

YuvaAI is an evolving project. Potential areas of future development include:

- Email verification and account recovery.
- Advanced conversational memory.
- Additional AI model integrations.
- User profiles and account settings.
- Enhanced real-time streaming experience.
- Advanced usage analytics.
- Application monitoring and observability.
- Further performance and security improvements.

---

## Project Status

**Status: Publicly Deployed — Active Development**

YuvaAI is publicly accessible and its core application infrastructure is deployed on Railway.

The project continues to evolve with improvements to its AI capabilities, user experience, backend architecture and security.

---

## Author

**Aryan Srivastava**

B.Tech — Computer Science Engineering  
Specialization: Artificial Intelligence & Machine Learning

GitHub: [@s-aryan08](https://github.com/s-aryan08)

---

## Acknowledgements

- [FastAPI](https://fastapi.tiangolo.com/)
- [Groq](https://groq.com/)
- [PostgreSQL](https://www.postgresql.org/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Railway](https://railway.com/)

---

<p align="center">
  <strong>YuvaAI — Your AI Companion.</strong>
  <br>
  Built with Python, FastAPI, PostgreSQL and Groq.
  <br><br>
  <a href="https://yuvaai-production.up.railway.app/">
    Experience YuvaAI →
  </a>
</p>
