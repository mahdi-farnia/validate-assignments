"""Generate Markdown Report"""

import asyncio

from src.config import settings
from src.storage import Storage

from .report import ReportFormat, ReportItem
from .report_json import JSONReport
from .report_md import MDReport


# TODO tidy report writers => open-closed
class ReportWriter:
    _formats: list[ReportFormat]
    _report_record: list[ReportItem]

    def __init__(self, formats: list[ReportFormat], report_record: list[ReportItem]):
        self._formats = formats
        self._report_record = report_record

    async def write_report(self, storage: Storage):
        async with asyncio.TaskGroup() as tg:
            if ReportFormat.JSON in self._formats:
                tg.create_task(self._write_report_json(storage))
            if ReportFormat.MD in self._formats:
                tg.create_task(self._write_report_md(storage))

    async def _write_report_json(self, storage: Storage):
        reporter = JSONReport(self._report_record)
        await storage.write_report(
            settings.report_json, bytes(reporter.gen_report(), encoding="utf-8")
        )

    async def _write_report_md(self, storage: Storage):
        reporter = MDReport(self._report_record)
        await storage.write_report(
            settings.report_md, bytes(reporter.gen_report(), encoding="utf-8")
        )
