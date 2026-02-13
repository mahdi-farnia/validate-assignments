import pytest
import json
from src.report.report_json import ReportItem, ValidationStatus, JSONReport

valid_cases: list[tuple[str, list[ReportItem], dict]] = [
    (
        "Simple",
        [
            ("1", ValidationStatus.COMPILATION_FAILED),
            ("2", ValidationStatus.INVALID_OUTPUT),
            ("3", ValidationStatus.RUN_FAILED),
            ("4", ValidationStatus.SUCCEEDED),
        ],
        {
            "1": {
                "reason": ValidationStatus.to_str(ValidationStatus.COMPILATION_FAILED),
                "score": 0,
            },
            "2": {
                "reason": ValidationStatus.to_str(ValidationStatus.INVALID_OUTPUT),
                "score": 0,
            },
            "3": {
                "reason": ValidationStatus.to_str(ValidationStatus.RUN_FAILED),
                "score": 0,
            },
            "4": {
                "reason": ValidationStatus.to_str(ValidationStatus.SUCCEEDED),
                "score": 100,
            },
        },
    )
]


@pytest.mark.parametrize(
    ["input", "output"],
    ids=(c[0] for c in valid_cases),
    argvalues=((c[1], c[2]) for c in valid_cases),
)
def test_json_report(input: list[ReportItem], output: dict):
    assert json.loads(JSONReport(input).gen_report()) == output
