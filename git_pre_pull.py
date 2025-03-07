import asyncio
import logging
import subprocess
from pathlib import Path
from os import PathLike
from datetime import datetime

# Configure logging
log_file = Path("git_pre_pull.log")
logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
)

async def run_command(*args, cwd: PathLike | None = None, silent: bool = False):
    """Runs a shell command asynchronously and handles errors."""
    process = await asyncio.create_subprocess_exec(
        *args,
        cwd=str(cwd) if cwd else None,
        stdout=asyncio.subprocess.PIPE if silent else None,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        error_msg = stderr.decode().strip() if stderr else "Unknown error"
        raise subprocess.CalledProcessError(process.returncode, args, output=stdout, stderr=error_msg)

def get_iso8601_timestamp() -> str:
    """Returns the current timestamp in ISO 8601 format."""
    return datetime.now().isoformat()

# Configure logging
log_file = Path("git_pre_pull.log")
logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
)

async def git_pre_pull(
    cwd: PathLike | None = None,
    commit_message: str | None = None,
    status_only: bool = False,
    remote: str = "origin",
    branch: str = "main",
) -> None:
    print(f'📦 Pre-pulling {cwd or "."} ...')
    try:
        await run_command("git", "-c", "color.status=always", "status", cwd=cwd)
        await run_command("git", "add", "--all", cwd=cwd, silent=status_only)
        await run_command(
            "git",
            "commit",
            "-m",
            f"{get_iso8601_timestamp() if not commit_message else commit_message}",
            cwd=cwd,
            silent=status_only,
        )
        await run_command("git", "pull", remote, branch, cwd=cwd)
    except subprocess.CalledProcessError as e:
        logging.error(f"Error occurred during Git operations: {e}")
        logging.error("Aborting pre-pull process.")
    except Exception as e:
        logging.exception(f"Unexpected error occurred: {e}")
        logging.error("Aborting pre-pull process.")
    else:
        print("✅ Pre-pull process completed successfully.")

if __name__ == "__main__":
    asyncio.run(git_pre_pull(cwd=Path("."), commit_message="Auto commit"))