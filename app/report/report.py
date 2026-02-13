from enum import IntEnum


class ValidationStatus(IntEnum):
    """Status of a given source code"""

    COMPILATION_FAILED = 0
    RUN_FAILED = 1
    INVALID_OUTPUT = 2
    SUCCEEDED = 3

    @staticmethod
    def to_str(value: ValidationStatus):
        match value:
            case ValidationStatus.COMPILATION_FAILED:
                return "compile error"
            case ValidationStatus.RUN_FAILED:
                return "runtime error"
            case ValidationStatus.INVALID_OUTPUT:
                return "invalid output"
            case ValidationStatus.SUCCEEDED:
                return "success"
            case _:
                return "UNKNOWN"


class ReportFormat(IntEnum):
    JSON = 0
    MD = 1


type StudentId = str
type ReportItem = tuple[StudentId, ValidationStatus]
