
from pathlib import Path
import os
import klotho
import klotho.aws as aws


# Create the Application instance
app = klotho.Application(
    "chat-app",
    project=os.getenv("PROJECT_NAME", "my-project"), # Default to 'my-project' or the environment variable value
    environment=os.getenv("KLOTHO_ENVIRONMENT", "default"), # Default to 'default' or the environment variable value
    default_region=os.getenv("AWS_REGION", "us-east-1"),  # Default to 'us-east-1' or the environment variable value
)

# Define the path to the project root and Dockerfile using pathlib
dir_path = Path(__file__).parent
dockerfile_path = dir_path.parent / "Dockerfile"

fastapi = aws.FastAPI('my-fastapi',
                      context="..",
                      dockerfile=str(dockerfile_path),
                      health_check_path="/",
                      health_check_matcher="200-299",
                      health_check_healthy_threshold=2,
                      health_check_unhealthy_threshold=8,
                )

postgres = aws.Postgres("my-postgres", username="admintest", password="password123!", database_name="mydb",)
fastapi.bind(postgres)