import time
from datetime import datetime, timezone

def get_current_epoch():
    """Get current time as Unix epoch integer"""
    return int(time.time())

def epoch_to_iso8601(epoch_time):
    """Convert epoch time to ISO-8601 format with timezone offset"""
    dt = datetime.fromtimestamp(epoch_time, tz=timezone.utc)
    return dt.astimezone().isoformat()