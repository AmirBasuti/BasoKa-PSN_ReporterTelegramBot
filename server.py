from dataclasses import dataclass
import requests
import logging
import time

logger = logging.getLogger(__name__)

class ServerOperationError(Exception):
    pass

@dataclass
class Server:
    name: str
    address: str
    running: bool = False

    async def get_status(self, config):
        retries = 3
        for attempt in range(retries):
            try:
                response = requests.get(
                    f"{config.base_url.format(address=self.address)}{config.endpoints['status']}",
                    timeout=config.default_timeout
                )
                return response.json()
            except requests.RequestException as e:
                logger.error(f"Attempt {attempt + 1} failed for get_status on server {self.name}: {e}", exc_info=True)
                if attempt < retries - 1:
                    time.sleep(2)  # Wait before retrying
                    return None
                else:
                    raise ServerOperationError(f"Status check failed after {retries} attempts: {e}")
        return None

    async def start(self, config):
        retries = 3
        for attempt in range(retries):
            try:
                response = requests.post(
                    f"{config.base_url.format(address=self.address)}{config.endpoints['start']}",
                    timeout=config.default_timeout
                )
                if response.status_code == 200:
                    self.running = True
                    return
                else:
                    logger.error(f"Unexpected status code {response.status_code} for start on server {self.name}")
                    raise ServerOperationError(f"Start operation failed with status code {response.status_code}")
            except requests.RequestException as e:
                logger.error(f"Attempt {attempt + 1} failed for start on server {self.name}: {e}", exc_info=True)
                if attempt < retries - 1:
                    time.sleep(2)  # Wait before retrying
                else:
                    raise ServerOperationError(f"Start operation failed after {retries} attempts: {e}")

    async def stop(self, config):
        retries = 3
        for attempt in range(retries):
            try:
                response = requests.post(
                    f"{config.base_url.format(address=self.address)}{config.endpoints['stop']}",
                    timeout=config.default_timeout
                )
                if response.status_code == 200:
                    self.running = False
                    return
                else:
                    logger.error(f"Unexpected status code {response.status_code} for stop on server {self.name}")
                    raise ServerOperationError(f"Stop operation failed with status code {response.status_code}")
            except requests.RequestException as e:
                logger.error(f"Attempt {attempt + 1} failed for stop on server {self.name}: {e}", exc_info=True)
                if attempt < retries - 1:
                    time.sleep(2)  # Wait before retrying
                else:
                    raise ServerOperationError(f"Stop operation failed after {retries} attempts: {e}")

    async def is_running(self, config):
        retries = 3
        for attempt in range(retries):
            try:
                response = requests.get(
                    f"{config.base_url.format(address=self.address)}{config.endpoints['is_running']}",
                    timeout=config.default_timeout
                )
                if response.status_code == 200:
                    return response.json().get("running", False)
                else:
                    logger.error(f"Unexpected status code {response.status_code} for is_running on server {self.name}")
                    raise ServerOperationError(f"is_running operation failed with status code {response.status_code}")
            except requests.RequestException as e:
                logger.error(f"Attempt {attempt + 1} failed for is_running on server {self.name}: {e}", exc_info=True)
                if attempt < retries - 1:
                    time.sleep(2)  # Wait before retrying
                    return None
                else:
                    raise ServerOperationError(f"is_running operation failed after {retries} attempts: {e}")
        return None

    async def get_log(self, config):
        retries = 3
        for attempt in range(retries):
            try:
                response = requests.get(
                    f"{config.base_url.format(address=self.address)}{config.endpoints['log']}",
                    timeout=config.default_timeout
                )
                if response.status_code == 200:
                    return response.text
                else:
                    logger.error(f"Unexpected status code {response.status_code} for log on server {self.name}")
                    raise ServerOperationError(f"log operation failed with status code {response.status_code}")
            except requests.RequestException as e:
                logger.error(f"Attempt {attempt + 1} failed for log on server {self.name}: {e}", exc_info=True)
                if attempt < retries - 1:
                    time.sleep(2)  # Wait before retrying
                    return None
                else:
                    raise ServerOperationError(f"log operation failed after {retries} attempts: {e}")
        return None