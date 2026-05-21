# API Overview

## Core Modules

- main.py: application entrypoint and router registration
- auth.py: authentication routes and current user logic
- security.py: JWT generation and validation
- db.py: database engine and session configuration
- models.py: SQLAlchemy models
- schemas.py: Pydantic schemas
- notes.py: notes module
- admin_routes.py: admin routes
- audit.py: audit logic
- audit_log.py: audit persistence model
- audit_routes.py: audit API routes
- ai_routes.py: AI related API routes

## Operational Endpoints

- /health: basic health check
- /docs: Swagger and OpenAPI documentation

The exact API contract is exposed by FastAPI at /docs when the application is running.
