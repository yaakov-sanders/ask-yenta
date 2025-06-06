# AskYenta - Your AI Relationship Insight Assistant

AskYenta is a contextual AI-powered web app that helps users understand themselves and their relationships better. It combines persistent memory, smart conversation tracking, and personal insights — all with a nosy best friend vibe.

## Features

- 🧠 Personalized memory for each user across chats
- 💬 Observes shared conversations between users to build relationship insights
- 🔒 Privacy-respecting design with user-controlled connections
- 🤖 Smart conversation tracking and analysis
- 🎯 Personalized insights and recommendations
- 🌙 Dark mode support
- 📱 Responsive design for all devices

## Technology Stack

### Backend
- ⚡ [**FastAPI**](https://fastapi.tiangolo.com) - Modern, fast web framework for building APIs
- 🧰 [SQLModel](https://sqlmodel.tiangolo.com) - SQL database ORM
- 🔍 [Pydantic](https://docs.pydantic.dev) - Data validation and settings management
- 💾 [PostgreSQL](https://www.postgresql.org) - Robust SQL database
- 🤖 [Letta](https://github.com/yourusername/letta) - LLM agent framework for intelligent conversations

### Frontend
- 🚀 [React](https://react.dev) with TypeScript
- 🎨 [Chakra UI](https://chakra-ui.com) - Modern component library
- 🦇 Dark mode support
- 🧪 [Playwright](https://playwright.dev) for End-to-End testing

### Infrastructure
- 🐋 [Docker Compose](https://www.docker.com) for development and production
- 📞 [Traefik](https://traefik.io) as reverse proxy
- 🔒 JWT authentication
- 📫 Email-based password recovery
- ✅ Comprehensive test suite with Pytest
- 🏭 CI/CD with GitHub Actions

## Use Case

Whether you're chatting one-on-one with Yenta or in a group with someone new, Yenta helps surface what's really going on — emotionally, contextually, and historically.

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Node.js (for frontend development)
- Python 3.8+ (for backend development)

### Development Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ask-yenta.git
cd ask-yenta
```

2. Set up environment variables:
```bash
cp .env.example .env
```

3. Start the development environment:
```bash
docker-compose up -d
```

4. Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Configuration

Before deploying, update the following environment variables:
- `SECRET_KEY`
- `FIRST_SUPERUSER_PASSWORD`
- `POSTGRES_PASSWORD`

Generate secure keys using:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Coming Soon

- Multi-agent conversation views
- Deeper profile insights
- Custom tools for user data retrieval and summarization

## Development

- Backend development: See [backend/README.md](./backend/README.md)
- Frontend development: See [frontend/README.md](./frontend/README.md)
- General development: See [development.md](./development.md)

## Deployment

For deployment instructions, see [deployment.md](./deployment.md).

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Security

For security concerns, please see [SECURITY.md](SECURITY.md).
