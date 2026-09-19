from dataclasses import dataclass
@dataclass
class ScanResult:
    valid: bool
    compatible: bool
    message: str
    checks: list
