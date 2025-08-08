from dataclasses import dataclass
import requests
import logging
import time
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class ServerOperationError(Exception):
    pass

@dataclass
class Server:
    name: str
    address: str
    running: bool = False

    def _make_request(self, method: str, endpoint: str, config, retries: int = 3) -> Optional[Dict[str, Any]]:
        """Make HTTP request with retry logic"""
        for attempt in range(retries):
            try:
                url = f"{config.base_url.format(address=self.address)}{endpoint}"
                
                if method.upper() == 'GET':
                    response = requests.get(url, timeout=config.default_timeout)
                elif method.upper() == 'POST':
                    response = requests.post(url, timeout=config.default_timeout)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                response.raise_for_status()
                return response.json()
                
            except requests.RequestException as e:
                logger.error(f"Attempt {attempt + 1} failed for {method} {endpoint} on server {self.name}: {e}")
                if attempt < retries - 1:
                    time.sleep(2)  # Wait before retrying
                else:
                    raise ServerOperationError(f"{method} {endpoint} failed after {retries} attempts: {e}")
        return None

    async def get_status(self, config) -> Dict[str, Any]:
        """Get comprehensive server status from Flask app"""
        try:
            result = self._make_request('GET', config.endpoints['status'], config)
            if result:
                # Format the response for better readability
                process_info = result.get('process_info', {})
                login_stats = result.get('login_stats', {})
                
                status_text = f"🖥️ **Server Status**: {result.get('server_status', 'unknown')}\n"
                status_text += f"🔄 **Process**: {'Running' if process_info.get('running') else 'Stopped'}\n"
                
                if process_info.get('pid'):
                    status_text += f"🆔 **PID**: {process_info['pid']}\n"
                
                # Add login statistics if available
                if login_stats and 'total_attempts' in login_stats:
                    status_text += f"\n📊 **Login Statistics**:\n"
                    status_text += f"✅ Success: {login_stats.get('success_count', 0)}\n"
                    status_text += f"❌ Failed: {login_stats.get('failed_count', 0)}\n"
                    status_text += f"🔄 Retries: {login_stats.get('retry_count', 0)}\n"
                    status_text += f"📈 Total: {login_stats.get('total_attempts', 0)}\n"
                
                status_text += f"\n🕐 **Last Updated**: {result.get('timestamp', 'unknown')}"
                return status_text
            return "❌ Failed to get status"
        except Exception as e:
            logger.error(f"Error getting status for {self.name}: {e}")
            return f"❌ Error: {str(e)}"

    async def start(self, config) -> str:
        """Start the PSN checker process"""
        try:
            result = self._make_request('POST', config.endpoints['start'], config)
            if result:
                status = result.get('status', 'unknown')
                message = result.get('message', '')
                
                if status == 'started':
                    self.running = True
                    pid = result.get('pid', 'unknown')
                    return f"✅ PSN Checker started successfully (PID: {pid})"
                elif status == 'already_running':
                    return f"ℹ️ PSN Checker is already running"
                else:
                    return f"⚠️ Start failed: {message}"
            return "❌ Failed to start"
        except Exception as e:
            logger.error(f"Error starting {self.name}: {e}")
            return f"❌ Error: {str(e)}"

    async def stop(self, config) -> str:
        """Stop the PSN checker process"""
        try:
            result = self._make_request('POST', config.endpoints['stop'], config)
            if result:
                status = result.get('status', 'unknown')
                message = result.get('message', '')
                
                if status == 'stopped':
                    self.running = False
                    return f"✅ PSN Checker stopped successfully"
                elif status == 'not_running':
                    return f"ℹ️ PSN Checker was not running"
                else:
                    return f"⚠️ Stop failed: {message}"
            return "❌ Failed to stop"
        except Exception as e:
            logger.error(f"Error stopping {self.name}: {e}")
            return f"❌ Error: {str(e)}"

    async def is_running(self, config) -> str:
        """Check if the PSN checker process is running"""
        try:
            result = self._make_request('GET', config.endpoints['status'], config)
            if result:
                process_info = result.get('process_info', {})
                is_running = process_info.get('running', False)
                pid = process_info.get('pid')
                
                if is_running and pid:
                    return f"✅ Running (PID: {pid})"
                elif is_running:
                    return f"✅ Running"
                else:
                    return f"❌ Not running"
            return "❓ Status unknown"
        except Exception as e:
            logger.error(f"Error checking running status for {self.name}: {e}")
            return f"❌ Error: {str(e)}"

    async def get_log(self, config, lines: int = 50) -> str:
        """Get recent logs from the PSN checker"""
        try:
            # Add lines parameter to the log endpoint
            endpoint = f"{config.endpoints['log']}?lines={lines}"
            result = self._make_request('GET', endpoint, config)
            
            if result:
                log_content = result.get('log', 'No log content')
                lines_count = result.get('lines_count', 0)
                
                if 'error' in result:
                    return f"❌ Log Error: {result['error']}"
                
                if lines_count == 0:
                    return "📝 No log entries found"
                
                # Truncate very long logs for Telegram
                if len(log_content) > 4000:
                    log_content = log_content[-4000:] + "\n\n... (truncated)"
                
                return f"📝 **Latest {lines_count} log lines**:\n\n```\n{log_content}\n```"
            return "❌ Failed to get logs"
        except Exception as e:
            logger.error(f"Error getting logs for {self.name}: {e}")
            return f"❌ Error: {str(e)}"

    async def get_statistics(self, config) -> str:
        """Get detailed login statistics"""
        try:
            result = self._make_request('GET', config.endpoints['status'], config)
            if result:
                login_stats = result.get('login_stats', {})
                
                if not login_stats or 'total_attempts' not in login_stats:
                    return "📊 No statistics available"
                
                stats_text = "📊 **Detailed Login Statistics**:\n\n"
                stats_text += f"✅ **Successful Logins**: {login_stats.get('success_count', 0)}\n"
                stats_text += f"❌ **Failed Logins**: {login_stats.get('failed_count', 0)}\n"
                stats_text += f"🔄 **Retry Attempts**: {login_stats.get('retry_count', 0)}\n"
                stats_text += f"📈 **Total Attempts**: {login_stats.get('total_attempts', 0)}\n\n"
                
                # Calculate success rate
                total = login_stats.get('total_attempts', 0)
                success = login_stats.get('success_count', 0)
                if total > 0:
                    success_rate = (success / total) * 100
                    stats_text += f"📊 **Success Rate**: {success_rate:.1f}%\n\n"
                
                stats_text += f"🕐 **Last Updated**: {login_stats.get('last_updated', 'unknown')}"
                return stats_text
            return "❌ Failed to get statistics"
        except Exception as e:
            logger.error(f"Error getting statistics for {self.name}: {e}")
            return f"❌ Error: {str(e)}"