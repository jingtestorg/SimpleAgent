import logging
from datetime import datetime

from langchain_core.tools import tool

logger = logging.getLogger(__name__)

# Time-of-day boundaries (24-hour clock)
MORNING_START = 0
MORNING_END = 12
AFTERNOON_END = 17
EVENING_END = 21


def _classify_time_of_day(hour: int) -> str:
    """Classify an hour (0-23) into a time-of-day category."""
    if MORNING_START <= hour < MORNING_END:
        return "morning"
    elif MORNING_END <= hour < AFTERNOON_END:
        return "afternoon"
    elif AFTERNOON_END <= hour < EVENING_END:
        return "evening"
    else:
        return "night"


@tool
def get_time_of_day() -> dict:
    """Get the current time of day category based on the system clock.

    Returns a dict with:
      - category: one of 'morning' (0-11), 'afternoon' (12-16), 'evening' (17-20), or 'night' (21-23)
      - greeting: the corresponding greeting phrase
      - hour: the current hour (0-23)
    """
    try:
        now = datetime.now()
        hour = now.hour
        category = _classify_time_of_day(hour)

        greeting_map = {
            "morning": "Good morning",
            "afternoon": "Good afternoon",
            "evening": "Good evening",
            "night": "Good night",
        }
        greeting = greeting_map[category]

        logger.info("[M2.achieved]: time-of-day greeting generated correctly — category=%s hour=%d", category, hour)
        return {"category": category, "greeting": greeting, "hour": hour}

    except Exception as exc:
        logger.error("[M2.missed]: time classification did not return expected greeting category — %s", exc)
        raise
