from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class Config:
    bot_token: str
    default_timeout: int = 10
    base_url: str = "http://{address}"
    authorized_user_ids: List[int] = field(default_factory=list)  # List of authorized user IDs
    endpoints: Dict[str, str] = field(default_factory=lambda: {
        "status": "/status",      # GET - Comprehensive status with process info and login stats
        "start": "/start",        # POST - Start the PSN checker process
        "stop": "/stop",          # POST - Stop the PSN checker process
        "log": "/log",           # GET - Get recent logs (?lines=N parameter)
    })
