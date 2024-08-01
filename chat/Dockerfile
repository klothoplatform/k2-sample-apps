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

# Copy the built frontend files from the local machine
COPY frontend/build /app/frontend/build

# Command to run the application
CMD ["sh", "-c", "sleep 10 && pipenv run alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 80"]
