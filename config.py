from dataclasses import dataclass, field
from typing import Dict

@dataclass
class Config:
    bot_token: str
    default_timeout: int = 5
    base_url: str = "http://{address}"
    endpoints: Dict[str, str] = field(default_factory=lambda: {
        "is_running": "/is_running",
        "status": "/status",
        "start": "/start",
        "stop": "/stop",
        "log": "/log",
    })
