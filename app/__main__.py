"""Main entry for program"""

import logging
import sys

from app.comp_source import SourceCompileError, comp_source
from app.list_sources import list_sources
from app.parse_solution import UnsupportedSolutionFormat, parse_solution
from app.report import (
    ReportFormat,
    ReportItem,
    ReportWriter,
    ValidationStatus,
)
from app.run_bin import CalledProcessError, run_bin
from app.solution_file.reader import read_solution

logger = logging.getLogger(__name__)


async def main(report_formats: list[ReportFormat]):
    async with read_solution() as solution_src:
        try:
            solution = await parse_solution(solution_src)
        except UnsupportedSolutionFormat:
            logger.error("Invalid solution.json format!")
            sys.exit(1)

    report_record: list[ReportItem] = []

    for idx, source_code in enumerate(await list_sources()):
        # Student Id must be set as source code name => <student_id>.c
        student_id: str = source_code.stem
        try:
            logger.info(f"[{idx:2}]  Compiling => {student_id}")
            compiled_bin = comp_source(source_code)
        except SourceCompileError:
            logger.warning(f"[{idx:2}]  Compilation Failed => {student_id}")
            report_record.append((student_id, ValidationStatus.COMPILATION_FAILED))
            continue

        logger.info(f"[{idx:2}]  Compiled Successfully, Attempting To Run")
        try:
            if (
                output_result := run_bin(compiled_bin, solution.input)
            ) == solution.output:
                logger.info(f"[{idx:2}]  Successfully Ran => {student_id}")
                report_record.append((student_id, ValidationStatus.SUCCEEDED))
            else:
                logger.debug(
                    f"Solution: {solution.input}\n\tExpected: {solution.output}\n\tActualOutput: {output_result}"
                )
                logger.warning(f"[{idx:2}]  Invalid Output => {student_id}")
                report_record.append((student_id, ValidationStatus.INVALID_OUTPUT))
        except CalledProcessError:
            logger.warning(f"[{idx:2}]  Failed To Run => {student_id}")
            report_record.append((student_id, ValidationStatus.RUN_FAILED))

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
