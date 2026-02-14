import functools
import json
import dataclasses
from typing import override

from .report import ReportItem, ValidationStatus


@dataclasses.dataclass
class JSONRecord:
    score: int
    reason: str


type JSONRecordCollection = dict[str, JSONRecord]


class JSONReport:
    _report_record: list[ReportItem]

    def __init__(self, report_record: list[ReportItem]):
        self._report_record = report_record

    @staticmethod
    def _status2score(status: ValidationStatus) -> int:
        return 100 if status == ValidationStatus.SUCCEEDED else 0

    @staticmethod
    def _status2reason(status: ValidationStatus) -> str:
        return ValidationStatus.to_str(status)

    def gen_report(self) -> str:
        def mk_json(
            acc: JSONRecordCollection, curr: ReportItem
        ) -> JSONRecordCollection:
            id, status = curr
            acc[id] = JSONRecord(
                score=self._status2score(status), reason=self._status2reason(status)
            )
            return acc

        return json.dumps(
            functools.reduce(mk_json, self._report_record, dict()),
            cls=self.JSONDataclassEncoderExtension,
        )

    class JSONDataclassEncoderExtension(json.JSONEncoder):
        @override
        def default(self, o: object):
            if dataclasses.is_dataclass(o):
                return dataclasses.asdict(o)  # type: ignore
            return super().default(o)
