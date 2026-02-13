from subprocess import run as run_subprocess, CalledProcessError
from datetime import timedelta
from pathlib import Path

from src.config import settings


def run_bin(
    dest: Path,
    stdin_lines: list[str],
    timeout: timedelta = timedelta(seconds=settings.run_timeout_sec),
) -> list[str]:
    """
    Docstring for run_bin

    :param dest: Binary to execute
    :type dest: Path
    :param stdin_lines: Input lines
    :type stdin_lines: list[str]
    :param timeout: How much to wait
    :type timeout: timedelta
    :raise NotSuccessfulExit:
    :return: Stdout Lines
    :rtype: list[str]
    """
    result = run_subprocess(
        [dest.as_posix()],
        input="\n".join(stdin_lines),
        text=True,
        capture_output=True,
        check=True,
        timeout=timeout.seconds,
    )

    return result.stdout.splitlines()
