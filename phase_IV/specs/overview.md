# Project Overview

## Vision

Transform the Phase I CLI Todo App into a full-stack web application with user authentication, RESTful API backend, and a modern React-based frontend. The application will maintain its core task management capabilities while adding secure multi-user support and a responsive web interface.

## Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.12+)
- **ORM**: SQLModel (SQLAlchemy + Pydantic)
- **Database**: Neon DB (PostgreSQL cloud-hosted)
- **Authentication**: JWT with Better Auth integration
- **Server**: Uvicorn (ASGI server)
- **Agentic**: OpenAPI/Swagger documentation for AI Agent skill discovery

### Frontend
- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript
- **Authentication**: Better Auth (client-side)
- **Styling**: Tailwind CSS
- **State Management**: React Query (TanStack Query)

### Infrastructure
- **Database Hosting**: Neon (PostgreSQL)
- **Package Management**: pnpm (recommended) or npm
- **Environment**: WSL2 (Linux) / Windows

## Architecture

```
hackathon-todo-fullstack/
├── backend/                 # FastAPI application
│   ├── src/
│   │   ├── models/         # SQLModel database models
│   │   ├── routers/        # API route handlers
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic
│   │   ├── auth/           # Authentication utilities
│   │   └── main.py         # Application entry point
│   ├── requirements.txt
│   └── pyproject.toml
│
├── frontend/               # Next.js application
│   ├── src/
│   │   ├── app/           # App Router pages
│   │   ├── components/    # React components
│   │   ├── lib/           # Utilities & API client
│   │   ├── hooks/         # Custom React hooks
│   │   └── types/         # TypeScript types
│   ├── package.json
│   └── tailwind.config.ts
│
├── specs/                  # Specification documents
│   ├── overview.md        # This file
│   ├── features/          # Feature specifications
│   ├── api/               # API documentation
│   ├── database/          # Database schema
│   └── ui/                # UI/UX specifications
│
└── CLAUDE.md              # Agentic workflow rules
```

## Success Criteria

- All CRUD operations accessible via REST API with JWT protection
- User registration and login functionality
- Tasks stored in Neon PostgreSQL with proper relationships
- Responsive web UI with intuitive task management
- Code generated from specs, not written manually
- **Agentic**: API documented with OpenAPI/Swagger for AI Agent skill discovery

## Goals

1. **User Authentication**: Implement secure JWT-based authentication with Better Auth
2. **RESTful API**: Create a clean API layer for all task operations
3. **Persistent Storage**: Migrate from JSON file to Neon PostgreSQL database
4. **Web Interface**: Build a responsive, modern UI with Next.js 15
5. **Multi-User Support**: Enable user-specific task management
6. **Type Safety**: Ensure end-to-end type safety across frontend and backend
7. **Agentic Compatibility**: API fully documented for AI Agent skill discovery

## Architecture

```
hackathon-todo-fullstack/
├── backend/                 # FastAPI application
│   ├── src/
│   │   ├── models/         # SQLModel database models
│   │   ├── routers/        # API route handlers
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic
│   │   ├── auth/           # Authentication utilities
│   │   ├── agent/          # Agent/Skill definitions for AI agents
│   │   └── main.py         # Application entry point
│   ├── requirements.txt
│   └── pyproject.toml
│
├── frontend/               # Next.js application
│   ├── src/
│   │   ├── app/           # App Router pages
│   │   ├── components/    # React components
│   │   ├── lib/           # Utilities & API client
│   │   ├── hooks/         # Custom React hooks
│   │   └── types/         # TypeScript types
│   ├── package.json
│   └── tailwind.config.ts
│
├── specs/                  # Specification documents
│   ├── overview.md        # This file
│   ├── features/          # Feature specifications
│   ├── api/               # API documentation
│   ├── database/          # Database schema
│   ├── ui/                # UI/UX specifications
│   └── agent/             # Agent/Skill specifications
│
└── CLAUDE.md              # Agentic workflow rules
