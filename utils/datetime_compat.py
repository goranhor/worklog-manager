"""DateTime compatibility utilities for Python 3.6 support."""

import re
from datetime import datetime


def fromisoformat_compat(date_string: str) -> datetime:
    """
    Compatibility function for datetime.fromisoformat() which was introduced in Python 3.7.

    This function provides equivalent functionality for Python 3.6.

    Args:
        date_string: ISO format date string

    Returns:
        datetime object

    Raises:
        ValueError: If the date string format is invalid
    """
    # Handle various ISO format patterns
    patterns = [
        # Full datetime with microseconds and timezone (T separator)
        r'^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})\.(\d+)([+-]\d{2}:\d{2}|Z)?$',
        # Full datetime with timezone (T separator)
        r'^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})([+-]\d{2}:\d{2}|Z)?$',
        # Full datetime without timezone (T separator)
        r'^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})\.(\d+)$',
        r'^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})$',
        # Full datetime with microseconds and timezone (space separator)
        r'^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})\.(\d+)([+-]\d{2}:\d{2}|Z)?$',
        # Full datetime with timezone (space separator)
        r'^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})([+-]\d{2}:\d{2}|Z)?$',
        # Full datetime without timezone (space separator)
        r'^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})\.(\d+)$',
        r'^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})$',
        # Date only
        r'^(\d{4})-(\d{2})-(\d{2})$',
        # Time only (assuming today's date)
        r'^(\d{2}):(\d{2}):(\d{2})\.(\d+)$',
        r'^(\d{2}):(\d{2}):(\d{2})$',
    ]

    date_string = date_string.strip()

    # Try each pattern
    for index, pattern in enumerate(patterns):
        match = re.match(pattern, date_string)
        if match:
            groups = match.groups()

            if index == 0:
                year, month, day, hour, minute, second, microsecond, tz = groups
                return datetime(
                    int(year),
                    int(month),
                    int(day),
                    int(hour),
                    int(minute),
                    int(second),
                    int(microsecond.ljust(6, '0')[:6]),
                )

            if index == 1:
                year, month, day, hour, minute, second, tz = groups
                return datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))

            if index == 2:
                year, month, day, hour, minute, second, microsecond = groups
                return datetime(
                    int(year),
                    int(month),
                    int(day),
                    int(hour),
                    int(minute),
                    int(second),
                    int(microsecond.ljust(6, '0')[:6]),
                )

            if index == 3:
                year, month, day, hour, minute, second = groups
                return datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))

            if index == 4:
                year, month, day, hour, minute, second, microsecond, tz = groups
                return datetime(
                    int(year),
                    int(month),
                    int(day),
                    int(hour),
                    int(minute),
                    int(second),
                    int(microsecond.ljust(6, '0')[:6]),
                )

            if index == 5:
                year, month, day, hour, minute, second, tz = groups
                return datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))

            if index == 6:
                year, month, day, hour, minute, second, microsecond = groups
                return datetime(
                    int(year),
                    int(month),
                    int(day),
                    int(hour),
                    int(minute),
                    int(second),
                    int(microsecond.ljust(6, '0')[:6]),
                )

            if index == 7:
                year, month, day, hour, minute, second = groups
                return datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))

            if index == 8:
                year, month, day = groups
                return datetime(int(year), int(month), int(day))

            if index == 9:
                hour, minute, second, microsecond = groups
                today = datetime.today().date()
                return datetime.combine(
                    today,
                    datetime.min.time().replace(
                        hour=int(hour),
                        minute=int(minute),
                        second=int(second),
                        microsecond=int(microsecond.ljust(6, '0')[:6]),
                    ),
                )

            if index == 10:
                hour, minute, second = groups
                today = datetime.today().date()
                return datetime.combine(
                    today,
                    datetime.min.time().replace(
                        hour=int(hour),
                        minute=int(minute),
                        second=int(second),
                    ),
                )

    # If no pattern matches, try the native Python 3.6 strptime as fallback
    try:
        for fmt in ['%Y-%m-%dT%H:%M:%S.%f', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d', '%H:%M:%S']:
            try:
                return datetime.strptime(date_string, fmt)
            except ValueError:
                continue
    except Exception:
        pass

    raise ValueError(f"Invalid isoformat string: '{date_string}'")


def datetime_fromisoformat(date_string: str) -> datetime:
    """Compatibility wrapper for datetime.fromisoformat()."""
    if hasattr(datetime, 'fromisoformat'):
        return datetime.fromisoformat(date_string)
    return fromisoformat_compat(date_string)
