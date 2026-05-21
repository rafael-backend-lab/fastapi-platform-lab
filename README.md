# FastAPI Platform Lab

Professional backend laboratory project built with FastAPI, PostgreSQL, Docker, JWT authentication, audit logging and automated health tests.

## Overview

This repository demonstrates practical backend API architecture with authentication, persistence, Docker based execution and operational validation.

## Tech Stack

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- JWT authentication
- Docker and Docker Compose
- Pytest
- OpenAPI and Swagger documentation

## Main Features

- JWT based authentication
- Protected API routes
- Notes module
- Admin routes
- Audit logging
- PostgreSQL integration
- Docker based local environment
- Health check endpoint
- Automated health test

## Local Execution

Start the application with Docker:

    docker compose up --build

API documentation:

    http://localhost:8005/docs

Health endpoint:

    http://localhost:8005/health

## Environment Variables

Create a local .env file based on .env.example when needed.

## Validation

Run syntax validation:

    python -m compileall .

Validate Docker Compose configuration:

    docker compose config

Run tests:

    python -m pytest

## Security Notes

This is a laboratory and portfolio project. For production usage, secrets must be replaced, credentials rotated, CORS restricted, rate limiting added and dependency scans performed.

## Portfolio Value

This repository demonstrates backend API design, authentication flow, database integration, Docker execution, auditability concerns and clean project documentation.

## Status

Professional portfolio repository maintained under the rafael-backend-lab GitHub profile.
