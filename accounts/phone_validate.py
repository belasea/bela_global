import re

# Define phone regex patterns per country
PHONE_PATTERNS = {
    'bd': r'^01[3-9]\d{8}$',       # Bangladesh: 01 + 9 digits
    'usa': r'^\+?1?\d{10}$',       # USA: optional +1, 10 digits
    'canada': r'^\+?1?\d{10}$',    # Canada: same as USA
    'uk': r'^\+?44\d{10}$',        # UK: +44 followed by 10 digits
}

def validate_phone_number(phone: str) -> bool:
    """
    Validate a phone number for BD, USA, Canada, UK formats.

    Args:
        phone (str): The phone number to validate

    Returns:
        bool: True if valid, False otherwise
    """
    if not phone:
        return False

    # Clean number: remove spaces and dashes
    digits = phone.strip().replace(" ", "").replace("-", "")

    # Check against each country's regex
    for pattern in PHONE_PATTERNS.values():
        if re.fullmatch(pattern, digits):
            # Check all digits not the same
            if len(set(digits.lstrip('+'))) == 1:
                return False

            # Check too many repeating digits (>70%)
            from collections import Counter
            counts = Counter(digits.lstrip('+'))
            most_common_count = counts.most_common(1)[0][1]
            if most_common_count / len(digits.lstrip('+')) > 0.7:
                return False

            # Reject sequential digits of length 5+
            seq = "0123456789"
            rev_seq = seq[::-1]
            num = digits.lstrip('+')
            for i in range(len(num) - 4):
                if num[i:i+5] in seq or num[i:i+5] in rev_seq:
                    return False

            # Passed all checks
            return True

    # Not matching any pattern
    return False
