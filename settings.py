import config

_personality  = config.PERSONALITY
_summary_hour = config.SUMMARY_HOUR

def get_personality() -> str:
    return _personality

def set_personality(value: str):
    global _personality
    _personality = value

def get_summary_hour() -> int:
    return _summary_hour

def set_summary_hour(hour: int):
    global _summary_hour
    _summary_hour = hour
