# YuvaAI — AI-Powered Conversational Assistant

**YuvaAI** is an AI-powered conversational assistant built to deliver an intelligent, secure and seamless chat experience through a modern web interface.

Powered by Python, FastAPI, PostgreSQL and Groq, YuvaAI combines AI inference, secure user authentication and persistent conversation management in a modular application architecture.

---

## Overview

YuvaAI is designed to provide users with an interactive AI assistant that supports natural-language conversations while maintaining individual user accounts and persistent chat histories.

The platform combines a lightweight frontend with a Python-based backend, providing a foundation for scalable AI-powered applications.

## Key Features

### AI-Powered Conversations
- Intelligent responses powered by Groq inference.
- Integration with the OpenAI GPT-OSS 20B model.
- Context-aware conversation handling.
- Configurable response generation.
- Support for standard and streaming chat APIs.

### Authentication and Security
- User registration and login.
- JWT-based authentication.
- Secure HTTP-only authentication cookies.
- Argon2 password hashing.
- CSRF protection for state-changing requests.
- Protected user-specific resources.
- Configurable session expiration.

### Conversation Management
- Create and manage conversations.
- Persistent conversation history.
- Retrieve previous messages.
- Delete conversations.
- Individual conversation ownership.

### Usage Management
- Daily request limits.
- Per-minute request limits.
- Database-backed usage tracking.
- User-specific usage records.

### Modern User Interface
- Responsive web interface.
- Light and dark themes.
- Markdown-rendered AI responses.
- Code syntax highlighting.
- Conversation sidebar.
- Interactive chat experience.

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
| Password Security | Argon2 |
| Database Migrations | Alembic |
| HTTP Client | HTTPX |
| Deployment | Railway |
| Version Control | Git, GitHub |

---

## System Architecture

```text
                ┌──────────────────────┐
                │       USER           │
                └──────────┬───────────┘
                           │
                           ▼
                ┌──────────────────────┐
                │   YUVAAI FRONTEND    │
                │                      │
                │   HTML / CSS / JS    │
                └──────────┬───────────┘
                           │
                      REST API
                           │
                           ▼
                ┌──────────────────────┐
                │    FASTAPI BACKEND   │
                │                      │
                │ Authentication       │
                │ Chat Services        │
                │ Conversation APIs    │
                │ Usage Management     │
                └───────┬────────┬─────┘
                        │        │
              ┌─────────┘        └─────────┐
              ▼                            ▼
    ┌──────────────────┐       ┌──────────────────┐
    │   PostgreSQL     │       │    GROQ API      │
    │                  │       │                  │
    │ Users            │       │ AI Inference     │
    │ Conversations    │       │ Response         │
    │ Messages         │       │ Generation       │
    │ Usage Records    │       │                  │
    └──────────────────┘       └──────────────────┘
```

## Project Structure

```text
YuvaAI/
│
├── backend/
│   ├── auth/
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

### Authentication

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/auth/csrf` | Generate CSRF token |
| POST | `/api/auth/register` | Register a user |
| POST | `/api/auth/login` | Authenticate a user |
| GET | `/api/auth/me` | Retrieve authenticated user |
| POST | `/api/auth/logout` | End authenticated session |

### Conversation Management

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/conversations` | Create a conversation |
| GET | `/api/conversations` | Retrieve user conversations |
| GET | `/api/conversations/{id}` | Retrieve conversation history |
| DELETE | `/api/conversations/{id}` | Delete a conversation |

### AI Chat

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/chat` | Generate AI response |
| POST | `/api/chat/stream` | Generate streaming response |

### Monitoring

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Application health check |

---

## Environment Configuration

YuvaAI uses environment-based configuration to manage application settings and external service credentials.

The following variables must be configured in the deployment environment:

| Variable | Purpose |
|---|---|
| `DEBUG` | Application debug configuration |
| `GROQ_API_KEY` | Groq API authentication |
| `GROQ_MODEL` | AI inference model |
| `DATABASE_URL` | PostgreSQL connection |
| `AUTH_SECRET_KEY` | JWT signing secret |
| `AUTH_TOKEN_EXPIRE_MINUTES` | Authentication expiration |

Sensitive credentials must be stored securely in the hosting platform's environment variable management system.

**Never commit API keys, database credentials or authentication secrets to source control.**

---

## Deployment

YuvaAI is designed for cloud deployment with a Python-compatible application hosting environment and a managed PostgreSQL database.

### Deployment Architecture

| Service | Platform |
|---|---|
| Application Hosting | Railway |
| Frontend | Served through the application |
| Backend API | FastAPI |
| Database | PostgreSQL |
| AI Inference | Groq |
| Source Code | GitHub |

### Deployment Requirements

- Python-compatible hosting environment.
- PostgreSQL database instance.
- Groq API credentials.
- Secure authentication secret.
- Configured environment variables.
- Database migrations applied through Alembic.

The application can be deployed through GitHub-connected continuous deployment.

---

## Security Considerations

Security is an important part of YuvaAI's application design.

The implementation includes:

- Argon2-based password hashing.
- JWT-based authentication.
- HTTP-only authentication cookies.
- CSRF token validation.
- User-specific conversation access checks.
- Environment-based configuration.
- Database-backed persistence.

---

## Roadmap

Planned areas of future development include:

- Email verification and account recovery.
- Advanced conversational memory.
- Expanded AI model integrations.
- User profile and account settings.
- Improved streaming interactions.
- Advanced usage analytics.
- Application monitoring and observability.

---

## Author

**Aryan Srivastava**

B.Tech — Computer Science Engineering (Artificial Intelligence & Machine Learning)

GitHub: [@s-aryan08](https://github.com/s-aryan08)

---

## Project Status

YuvaAI is under active development. Features and deployment infrastructure are being continuously improved.

---

**Built with Python, FastAPI, PostgreSQL and Groq.**
