import re
from typing import Optional, Tuple

class DateRulesChecker:
    """Checks statutory timeline constraints, SLAs, and deadline presence."""

    HOUR_PATTERNS = [
        r"(?:within|no later than)\s+(?P<hours>\d+)\s+hours",
        r"(?P<hours>\d+)\s*-\s*hour",
        r"(?P<hours>\d+)\s+hrs",
    ]

    DAY_PATTERNS = [
        r"(?:within|no later than)\s+(?P<days>\d+)\s+(?:business\s+)?days",
        r"(?P<days>\d+)\s*-\s*day",
    ]

    def extract_timeframe_hours(self, text: str) -> Optional[int]:
        text_lower = text.lower()

        for pattern in self.HOUR_PATTERNS:
            match = re.search(pattern, text_lower)
            if match:
                return int(match.group("hours"))

        for pattern in self.DAY_PATTERNS:
            match = re.search(pattern, text_lower)
            if match:
                return int(match.group("days")) * 24

        if "without undue delay" in text_lower or "immediately" in text_lower or "as soon as reasonably possible" in text_lower:
            return 24 # Standard statutory default for immediate notice

        return None

    def verify_sla_compliance(self, text: str, max_allowed_hours: int) -> Tuple[bool, Optional[int], str]:
        extracted_hours = self.extract_timeframe_hours(text)

        if extracted_hours is None:
            return False, None, "No explicit notification timeframe SLA found in clause."

        if extracted_hours <= max_allowed_hours:
            return True, extracted_hours, f"Timeframe of {extracted_hours} hours meets required maximum threshold of {max_allowed_hours} hours."
        else:
            return False, extracted_hours, f"Timeframe of {extracted_hours} hours EXCEEDS maximum allowed threshold of {max_allowed_hours} hours."

date_rules_checker = DateRulesChecker()
