import subprocess
import sys
import os
import argparse
from contextlib import contextmanager

DOCKER_COMPOSE_FILE = "docker-compose.yml"
DB_SERVICE = "db"
WEB_SERVICE = "web"

def run_command(command, env=None):
    print(f"Running command: {' '.join(command)}")
    try:
        result = subprocess.run(command, check=True, env=env)
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


def alembic_cmd(cmd):
    print(f"Running Alembic command: {' '.join(cmd)}")
    env = os.environ.copy()
    env["ALEMBIC_CONFIG"] = "alembic.ini"
    run_command(["docker-compose", "-f", DOCKER_COMPOSE_FILE, "run", "--rm", WEB_SERVICE] + cmd, env=env)

def alembic_revision(message):
    alembic_cmd(["pipenv", "run", "alembic", "revision", "--autogenerate", "-m", message])

def alembic_upgrade():
    alembic_cmd(["pipenv", "run", "alembic", "upgrade", "head"])

def alembic_downgrade(rev):
    alembic_cmd(["pipenv", "run", "alembic", "downgrade", rev])

def main():
    parser = argparse.ArgumentParser(description="Manage Docker and Alembic operations.")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("up", help="Start the environment.")
    subparsers.add_parser("up-logs", help="Start the environment with logs.")
    subparsers.add_parser("down", help="Stop the environment.")
    
    alembic_revision_parser = subparsers.add_parser("alembic-revision", help="Create a new Alembic migration.")
    alembic_revision_parser.add_argument("message", help="Message for the Alembic migration.")
    
    subparsers.add_parser("alembic-upgrade", help="Upgrade the database.")
    
    alembic_downgrade_parser = subparsers.add_parser("alembic-downgrade", help="Downgrade the database.")
    alembic_downgrade_parser.add_argument("revision", help="Revision to downgrade to.")
  

    args = parser.parse_args()

    if args.command == "up":
        up()
    elif args.command == "up-logs":
        up_logs()
    elif args.command == "down":
        down()
    elif args.command == "alembic-revision":
        alembic_revision(args.message)
    elif args.command == "alembic-upgrade":
        alembic_upgrade()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
