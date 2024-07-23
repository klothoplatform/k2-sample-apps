# Stage 1: Build the frontend
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

COPY frontend/package.json ./package.json
COPY frontend/package-lock.json ./package-lock.json
RUN npm install

COPY frontend/ ./
RUN npm run build

# Stage 2: Build the backend and combine with frontend
FROM python:3.12-slim

WORKDIR /app

# Install pipenv and Python dependencies
COPY Pipfile ./
COPY Pipfile.lock ./
RUN pip install pipenv && pipenv install --deploy --system

# Copy backend files
COPY alembic alembic
COPY app app
COPY alembic.ini .

# Copy the built frontend files
COPY --from=frontend-builder /app/frontend/build ./frontend/build

# Command to run the application
CMD ["sh", "-c", "sleep 10 && pipenv run alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 80"]
