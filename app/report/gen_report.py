"""Generate Markdown Report"""

from pathlib import Path

from aiofiles import open as aioopen

from app.config import settings
import asyncio
from .report_json import JSONReport
from .report_md import MDReport
from .report import ReportFormat, ReportItem


# TODO tidy report writers => open-closed
class ReportWriter:
    _formats: list[ReportFormat]
    _report_record: list[ReportItem]

    def __init__(self, formats: list[ReportFormat], report_record: list[ReportItem]):
        self._formats = formats
        self._report_record = report_record

    async def write_report(self):
        async with asyncio.TaskGroup() as tg:
            if ReportFormat.JSON in self._formats:
                tg.create_task(self._write_report_json())
            if ReportFormat.MD in self._formats:
                tg.create_task(self._write_report_md())

    async def _write_report_json(self):
        reporter = JSONReport(self._report_record)
        async with aioopen(Path(settings.assets_dir) / settings.report_json, "w") as f:
            await f.write(reporter.gen_report())

    async def _write_report_md(self):
        reporter = MDReport(self._report_record)
        async with aioopen(Path(settings.assets_dir) / settings.report_md, "w") as f:
            await f.write(reporter.gen_report())
