import subprocess
import sys
import time
import os
import shutil
import argparse
from contextlib import contextmanager

DOCKER_COMPOSE_FILE = "docker-compose.yml"
DB_SERVICE = "db"
WEB_SERVICE = "web"

def run_command(command, env=None):
    print(f"Running command: {' '.join(command)}")
    try:
        result = subprocess.run(command, check=True, env=env)
        print(result.stdout.decode('utf-8') if result.stdout else "")
        print(result.stderr.decode('utf-8') if result.stderr else "")
    except subprocess.CalledProcessError as e:
        print(f"Command failed with return code {e.returncode}")
        sys.exit(e.returncode)

def up():
    print("Starting the environment...")
    run_command(["docker-compose", "-f", DOCKER_COMPOSE_FILE, "up", "--build", "-d"])

def up_logs():
    print("Starting the environment with logs...")
    run_command(["docker-compose", "-f", DOCKER_COMPOSE_FILE, "up", "--build"])

def down():
    print("Stopping the environment...")
    run_command(["docker-compose", "-f", DOCKER_COMPOSE_FILE, "down"])

@contextmanager
def start_stop_db():
    start_db()
    try:
        yield
    finally:
        stop_db()

def start_db():
    print("Starting the database service...")
    run_command(["docker-compose", "-f", DOCKER_COMPOSE_FILE, "up", "-d", DB_SERVICE])
    time.sleep(5)  # Wait for the DB to be ready

def stop_db():
    print("Stopping the database service...")
    run_command(["docker-compose", "-f", DOCKER_COMPOSE_FILE, "stop", DB_SERVICE])

def alembic_cmd(cmd):
    print(f"Running Alembic command: {' '.join(cmd)}")
    env = os.environ.copy()
    env["ALEMBIC_CONFIG"] = "alembic.ini"
    run_command(["docker-compose", "-f", DOCKER_COMPOSE_FILE, "run", "--rm", WEB_SERVICE] + cmd, env=env)

def alembic_init():
    alembic_cmd(["pipenv", "run", "alembic", "init", "alembic"])

def alembic_revision():
    alembic_cmd(["pipenv", "run", "alembic", "revision", "--autogenerate", "-m", "Initial migration"])

def alembic_upgrade():
    alembic_cmd(["pipenv", "run", "alembic", "upgrade", "head"])

def alembic_downgrade(rev):
    alembic_cmd(["pipenv", "run", "alembic", "downgrade", rev])

def clean_db():
    print("Cleaning up the database...")
    with start_stop_db():
        run_command(["docker-compose", "exec", DB_SERVICE, "psql", "-U", "admintest", "-d", "postgres", "-c", "DROP DATABASE IF EXISTS dbname;"])
        run_command(["docker-compose", "exec", DB_SERVICE, "psql", "-U", "admintest", "-d", "postgres", "-c", "CREATE DATABASE dbname;"])

def regenerate_migrations():
    clean_db()
    print("Removing old migration files...")
    versions_dir = os.path.join("alembic", "versions")
    if os.path.exists(versions_dir):
        shutil.rmtree(versions_dir)
    os.makedirs(versions_dir)
    print("Regenerating migrations...")
    with start_stop_db():
        alembic_revision()
        alembic_upgrade()

def build_frontend():
    print("Building frontend...")
    run_command(["docker-compose", "run", "--rm", "frontend-builder", "npm", "run", "build"])

def main():
    parser = argparse.ArgumentParser(description="Manage Docker and Alembic operations.")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("up", help="Start the environment.")
    subparsers.add_parser("up-logs", help="Start the environment with logs.")
    subparsers.add_parser("down", help="Stop the environment.")
    
    alembic_parser = subparsers.add_parser("alembic", help="Run Alembic commands.")
    alembic_parser.add_argument("alembic_cmd", nargs=argparse.REMAINDER, help="Alembic command to run.")
    
    subparsers.add_parser("alembic-init", help="Initialize Alembic.")
    subparsers.add_parser("alembic-revision", help="Create a new Alembic migration.")
    subparsers.add_parser("alembic-upgrade", help="Upgrade the database.")
    
    alembic_downgrade_parser = subparsers.add_parser("alembic-downgrade", help="Downgrade the database.")
    alembic_downgrade_parser.add_argument("revision", help="Revision to downgrade to.")
    
    subparsers.add_parser("clean-db", help="Clean up the database.")
    subparsers.add_parser("regenerate-migrations", help="Clean up the database and regenerate migrations.")
    subparsers.add_parser("build-frontend", help="Build the frontend.")

    args = parser.parse_args()

    if args.command == "up":
        up()
    elif args.command == "up-logs":
        up_logs()
    elif args.command == "down":
        down()
    elif args.command == "alembic":
        with start_stop_db():
            alembic_cmd(args.alembic_cmd)
    elif args.command == "alembic-init":
        alembic_init()
    elif args.command == "alembic-revision":
        with start_stop_db():
            alembic_revision()
    elif args.command == "alembic-upgrade":
        with start_stop_db():
            alembic_upgrade()
    elif args.command == "alembic-downgrade":
        with start_stop_db():
            alembic_downgrade(args.revision)
    elif args.command == "clean-db":
        clean_db()
    elif args.command == "regenerate-migrations":
        regenerate_migrations()
    elif args.command == "build-frontend":
        build_frontend()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
