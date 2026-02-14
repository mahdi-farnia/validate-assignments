"""Main entry for program"""

import logging
import sys

from src.config import settings, StorageType
from src.parse_solution import UnsupportedSolutionFormat, parse_solution
from src.report import ReportFormat, ReportItem, ReportWriter, ValidationStatus
from src.solution_file.reader import read_solution
from src.storage import CompilationError, DiskStorage, RunError, S3Storage, Storage

logger = logging.getLogger(__name__)


def create_storage(t: str) -> Storage:
    match t:
        case StorageType.DISK:
            return DiskStorage()
        case StorageType.S3:
            return S3Storage()
        case _:
            raise ValueError("Unknown storage type")


async def main(report_formats: list[ReportFormat]):
    async with read_solution() as solution_src:
        try:
            solution = await parse_solution(solution_src)
        except UnsupportedSolutionFormat:
            logger.error("Invalid solution.json format!")
            sys.exit(1)

    report_record: list[ReportItem] = []

    idx = 0
    async for source in await create_storage(settings.source_storage).list_sources():
        idx += 1
        # Student Id must be set as source code name => <student_id>.c
        student_id = source.filename

        try:
            logger.info(f"[{idx:2}]  Compiling => {student_id}")
            await source.prepare_resource()
        except CompilationError:
            logger.warning(f"[{idx:2}]  Compilation Failed => {student_id}")
            report_record.append((student_id, ValidationStatus.COMPILATION_FAILED))
            continue

        try:
            if (output_result := await source.run(solution.input)) == solution.output:
                logger.info(f"[{idx:2}]  Successfully Ran => {student_id}")
                report_record.append((student_id, ValidationStatus.SUCCEEDED))
            else:
                logger.debug(
                    f"Solution: {solution.input}\n\tExpected: {solution.output}\n\tActualOutput: {output_result}"
                )
                logger.warning(f"[{idx:2}]  Invalid Output => {student_id}")
                report_record.append((student_id, ValidationStatus.INVALID_OUTPUT))
        except RunError:
            logger.warning(f"[{idx:2}]  Failed To Run => {student_id}")
            report_record.append((student_id, ValidationStatus.RUN_FAILED))

        logger.info(f"[{idx:2}]  Compiled Successfully, Attempting To Run")

    logger.info("Generating Report...")

    await ReportWriter(report_formats, report_record).write_report()


if __name__ == "__main__":
    import asyncio
    import os
    from argparse import ArgumentParser

    logging.basicConfig(
        level=(
            logging.DEBUG
            if os.getenv("DEBUG", "1").lower() in ["1", "yes", "true"]
            else logging.INFO
        )
    )

    parser = ArgumentParser()
    parser.add_argument(
        "-no-md",
        action="store_true",
        default=False,
        help="report in markdown format",
    )
    parser.add_argument(
        "-no-json",
        action="store_true",
        default=False,
        help="report in json format",
    )
    args = parser.parse_args()

    formats = [ReportFormat.JSON, ReportFormat.MD]
    if args.no_md:
        formats.remove(ReportFormat.MD)
    if args.no_json:
        formats.remove(ReportFormat.JSON)

    if len(formats) == 0:
        print("no such report format selected", file=sys.stderr)
        sys.exit()

    asyncio.run(main(formats))
