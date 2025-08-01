from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class Config:
    bot_token: str
    default_timeout: int = 5
    base_url: str = "http://{address}"
    authorized_user_ids: List[int] = field(default_factory=list)  # List of authorized user IDs
    endpoints: Dict[str, str] = field(default_factory=lambda: {
        "is_running": "/is_running",
        "status": "/status",
        "start": "/start",
        "stop": "/stop",
        "log": "/log",
    })
