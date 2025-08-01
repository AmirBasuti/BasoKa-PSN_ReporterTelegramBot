import json
import logging
from typing import Dict, Optional
from server import Server

logger = logging.getLogger(__name__)

class ServerManager:
    def __init__(self, file_path: str = "servers.json"):
        self.file_path = file_path
        self._initialize_file()

    def _initialize_file(self):
        try:
            with open(self.file_path, "x") as f:
                json.dump({}, f)
        except FileExistsError:
            pass

    def _read_servers(self) -> Dict[str, Dict]:
        try:
            with open(self.file_path, "r") as f:
                servers = json.load(f)
                logger.info(f"Successfully read servers from {self.file_path}: {servers}")
                return servers
        except FileNotFoundError:
            logger.warning(f"Server file {self.file_path} not found. Returning empty dictionary.")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON from {self.file_path}: {e}", exc_info=True)
            return {}

    def _write_servers(self, servers: Dict[str, Dict]) -> None:
        try:
            with open(self.file_path, "w") as f:
                json.dump(servers, f, indent=4)
                logger.info(f"Successfully wrote servers to {self.file_path}: {servers}")
        except Exception as e:
            logger.error(f"Error writing to server file {self.file_path}: {e}", exc_info=True)

    def servers(self):
        return self._read_servers().keys()

    def add_server(self, name: str, address: str) -> None:
        try:
            servers = self._read_servers()
            servers[name] = {"address": address, "running": False}
            self._write_servers(servers)
        except Exception as e:
            logger.error(f"Error adding server {name}: {e}", exc_info=True)

    def delete_server(self, name: str) -> None:
        try:
            servers = self._read_servers()
            servers.pop(name, None)
            self._write_servers(servers)
        except Exception as e:
            logger.error(f"Error deleting server {name}: {e}", exc_info=True)

    def get_server(self, name: str) -> Optional[Server]:
        try:
            servers = self._read_servers()
            server_data = servers.get(name)
            if server_data:
                return Server(name=name, address=server_data["address"], running=server_data["running"])
            return None
        except Exception as e:
            logger.error(f"Error retrieving server {name}: {e}", exc_info=True)
            return None


    async def start_all(self, config):
        results = []
        servers = self._read_servers()
        for name, data in servers.items():
            server = Server(name=name, address=data["address"])
            try:
                await server.start(config)
                data["running"] = True
                results.append(f"▶️ Started '{name}'")
            except Exception as e:
                results.append(f"⚠️ Failed to start '{name}': {e}")
        self._write_servers(servers)
        return results

    async def stop_all(self, config):
        results = []
        servers = self._read_servers()
        for name, data in servers.items():
            server = Server(name=name, address=data["address"])
            try:
                await server.stop(config)
                data["running"] = False
                results.append(f"⏹️ Stopped '{name}'")
            except Exception as e:
                results.append(f"⚠️ Failed to stop '{name}': {e}")
        self._write_servers(servers)
        return results

