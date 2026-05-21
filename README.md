# FastAPI Platform Lab

Backend laboratory project built with FastAPI, PostgreSQL, Docker, JWT authentication, admin routes, notes, audit logging and automated health tests.

## Purpose

This repository is a clean professional backend lab focused on:

- API architecture with FastAPI
- Authentication with JWT
- PostgreSQL integration
- Docker based local environment
- Admin and notes modules
- Audit logging
- Basic automated tests
- Production oriented structure for study and portfolio use

## Stack

- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- Docker
- Pytest
- JWT authentication

## Local execution

Run locally with Docker:

    docker compose up --build

Health endpoint:

    http://localhost:8005/health

API docs:

    http://localhost:8005/docs

## Security note

This is a laboratory project. Real production deployments must define secrets through environment variables, rotate credentials and avoid default development values.

## Status

Clean import prepared for a new professional GitHub profile.
