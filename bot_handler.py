import logging
from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes

# Assuming these modules are correctly implemented
from server_manager import ServerManager
from config import Config

logger = logging.getLogger(__name__)

# --- Constants for consistent replies ---
CMD_USAGE_ADD = "📋 **Usage**: `/add <name> <ip:port>`"
CMD_USAGE_DELETE = "📋 **Usage**: `/delete <name>`"
CMD_USAGE_STATUS = "📋 **Usage**: `/status <name>`"
CMD_USAGE_START = "📋 **Usage**: `/startserver <name>`"
CMD_USAGE_STOP = "📋 **Usage**: `/stopserver <name>`"
CMD_USAGE_IS_RUNNING = "📋 **Usage**: `/is_running <name>`"
CMD_USAGE_LOG = "📋 **Usage**: `/log <name>`"
CMD_USAGE_STATS = "📋 **Usage**: `/stats <name>`"
SERVER_NOT_FOUND = "❌ Server '{name}' not found.\n\nUse `/list` to see available servers."
NO_SERVERS_FOUND = "❌ No servers found. Use `/add` to add a server."


def authorized_only(func):
    """Decorator to check if user is authorized before executing a command."""

    @wraps(func)
    async def wrapper(self, update: Update, *args, **kwargs):
        if not update.effective_user:
            logger.warning("No user information in update.")
            return

        user_id = update.effective_user.id
        if user_id not in self.config.authorized_user_ids:
            logger.info(f"Unauthorized access attempt from user ID: {user_id}")
            # Silently ignore unauthorized requests
            return

        return await func(self, update, *args, **kwargs)

    return wrapper



class BotHandler:
    """Handles all bot commands and interactions."""

    def __init__(self, config: Config, server_manager: ServerManager):
        self.config = config
        self.server_manager = server_manager

    async def _reply_or_log(self, update: Update, text: str, **kwargs):
        """Helper to safely send a reply or log a warning if message is None."""
        if update.message:
            await update.message.reply_text(text, parse_mode='Markdown', **kwargs)
        else:
            logger.warning(f"Failed to send reply '{text}'. Update message is None.")

    async def _handle_missing_args(self, update: Update, usage_message: str, args: list, min_args: int):
        """Helper to handle commands with missing arguments."""
        if len(args) < min_args:
            await self._reply_or_log(update, usage_message)
            return True
        return False

    async def _get_server_or_reply(self, update: Update, server_name: str):
        """Helper to fetch a server and send a reply if it's not found."""
        server = self.server_manager.get_server(server_name)
        if not server:
            await self._reply_or_log(update, SERVER_NOT_FOUND.format(name=server_name))
        return server

    # --- Command Handlers ---

    @authorized_only
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE = None):
        """Sends a welcome message with a list of all available commands."""
        welcome_message = (
            "🎮 **Welcome to BasoKa PSN Bot!**\n\n"
            "📋 **Server Management:**\n"
            "• `/add <name> <ip:port>` - Add a new PSN server\n"
            "• `/list` - List all configured servers\n"
            "• `/delete <name>` - Remove a server\n\n"
            "🎯 **PSN Checker Control:**\n"
            "• `/startserver <name>` - Start the PSN checker for a server\n"
            "• `/stopserver <name>` - Stop the PSN checker for a server\n"            
            "• `/status <name>` - Get detailed status of a server\n"
            "• `/stats <name>` - Get detailed login statistics for a server\n"
            "• `/is_running` - Quick check if a servers is running\n\n"
            "📊 **Monitoring:**\n"
            "• `/log <name>` - View recent logs (sends file)\n"
            "⚡ **Bulk Operations:**\n"
            "• `/startall` - Start all checkers\n"
            "• `/statusall` - Get status of all servers\n"
            "• `/stopall` - Stop all checkers\n\n"
            "🔐 *Only authorized users can use this bot*"
        )
        await self._reply_or_log(update, welcome_message)

    @authorized_only
    async def add(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Adds a new server to the configuration."""
        if await self._handle_missing_args(update, CMD_USAGE_ADD, context.args, 2):
            return

        server_name, ip_port = context.args[0], context.args[1]
        try:
            self.server_manager.add_server(server_name, ip_port)
            await self._reply_or_log(update, f"✅ Server '{server_name}' added successfully.")
        except Exception as e:
            logger.error(f"Error adding server '{server_name}': {e}", exc_info=True)
            await self._reply_or_log(update, f"⚠️ Failed to add server '{server_name}': {e}")

    @authorized_only
    async def list(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Lists all configured servers."""
        servers = self.server_manager.servers()
        if not servers:
            await self._reply_or_log(update, NO_SERVERS_FOUND)
            return

        server_list = "\n".join(f"• `{name}`" for name in servers)
        await self._reply_or_log(update, f"📋 **Available Servers:**\n{server_list}")

    @authorized_only
    async def delete(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Deletes a server from the configuration."""
        if await self._handle_missing_args(update, CMD_USAGE_DELETE, context.args, 1):
            return

        server_name = context.args[0]
        try:
            self.server_manager.delete_server(server_name)
            await self._reply_or_log(update, f"✅ Server '{server_name}' deleted.")
        except KeyError:
            await self._reply_or_log(update, SERVER_NOT_FOUND.format(name=server_name))
        except Exception as e:
            logger.error(f"Error deleting server '{server_name}': {e}", exc_info=True)
            await self._reply_or_log(update, f"⚠️ Failed to delete server '{server_name}': {e}")

    @authorized_only
    async def status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Gets the detailed status of a specific server."""
        if await self._handle_missing_args(update, CMD_USAGE_STATUS, context.args, 1):
            return

        server_name = context.args[0]
        server = await self._get_server_or_reply(update, server_name)
        if not server:
            return

        try:
            status_text = await server.get_status(self.config)
            await self._reply_or_log(update, f"ℹ️ **Status of '{server_name}':**\n\n{status_text}")
        except Exception as e:
            logger.error(f"Error fetching status for '{server_name}': {e}", exc_info=True)
            await self._reply_or_log(update, "⚠️ An error occurred while fetching server status.")

    @authorized_only
    async def statusall(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Gets the status of all configured servers."""
        results = []
        if not self.server_manager.servers():
            await self._reply_or_log(update, NO_SERVERS_FOUND)
            return

        for name in self.server_manager.servers():
            server = self.server_manager.get_server(name)
            try:
                status_text = await server.get_status(self.config)
                results.append(f"✅ **{name}**:\n{status_text}\n")
            except Exception as e:
                results.append(f"⚠️ **{name}**: Failed to get status - {e}\n")

        await self._reply_or_log(update, "📋 **All Servers Status:**\n\n" + "\n".join(results))

    @authorized_only
    async def startserver(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Starts a specific server."""
        if await self._handle_missing_args(update, CMD_USAGE_START, context.args, 1):
            return

        server_name = context.args[0]
        server = await self._get_server_or_reply(update, server_name)
        if not server:
            return

        try:
            await server.start(self.config)
            await self._reply_or_log(update, f"✅ Server '{server_name}' started successfully.")
        except Exception as e:
            logger.error(f"Error starting server '{server_name}': {e}", exc_info=True)
            await self._reply_or_log(update, f"⚠️ Failed to start '{server_name}': {e}")

    @authorized_only
    async def stopserver(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Stops a specific server."""
        if await self._handle_missing_args(update, CMD_USAGE_STOP, context.args, 1):
            return

        server_name = context.args[0]
        server = await self._get_server_or_reply(update, server_name)
        if not server:
            return

        try:
            await server.stop(self.config)
            await self._reply_or_log(update, f"✅ Server '{server_name}' stopped successfully.")
        except Exception as e:
            logger.error(f"Error stopping server '{server_name}': {e}", exc_info=True)
            await self._reply_or_log(update, f"⚠️ Failed to stop '{server_name}': {e}")

    @authorized_only
    async def startall(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Starts all configured servers."""
        results = await self.server_manager.start_all(self.config)
        if not results:
            await self._reply_or_log(update, "❌ No servers to start.")
            return

        status_lines = [f"• {line}" for line in results]
        await self._reply_or_log(update, "✅ **Starting all servers...**\n\n" + "\n".join(status_lines))

    @authorized_only
    async def stopall(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Stops all configured servers."""
        results = await self.server_manager.stop_all(self.config)
        if not results:
            await self._reply_or_log(update, "❌ No servers to stop.")
            return

        status_lines = [f"• {line}" for line in results]
        await self._reply_or_log(update, "✅ **Stopping all servers...**\n\n" + "\n".join(status_lines))

    @authorized_only
    async def is_running(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Checks the running status of all servers."""
        servers = self.server_manager.servers()
        if not servers:
            await self._reply_or_log(update, NO_SERVERS_FOUND)
            return

        try:
            results = []
            for server_name in servers:
                server = self.server_manager.get_server(server_name)
                try:
                    running_status = await server.is_running(self.config)
                    status_emoji = "✅" if running_status else "❌"
                    status_text = "Running" if running_status else "Not Running"
                    results.append(f"{status_emoji} **{server_name}**: {status_text}")
                except Exception as e:
                    logger.error(f"Error checking status for '{server_name}': {e}", exc_info=True)
                    results.append(f"⚠️ **{server_name}**: Error - {str(e)}")

            await self._reply_or_log(update, "📊 **Servers Running Status:**\n\n" + "\n".join(results))
        except Exception as e:
            logger.error(f"Error checking running status for all servers: {e}", exc_info=True)
            await self._reply_or_log(update, f"⚠️ Failed to check running status: {e}")

    @authorized_only
    async def log(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Retrieves and sends log files for a specific server."""
        if await self._handle_missing_args(update, CMD_USAGE_LOG, context.args, 1):
            return

        server_name = context.args[0]
        server = await self._get_server_or_reply(update, server_name)
        if not server:
            return

        try:
            # Inform the user that we're processing their request
            if update.message:
                status_message = await update.message.reply_text("⏳ Downloading log files. Please wait...")

            # Get logs (now returns a dictionary with file paths)
            log_result = await server.get_log(self.config)

            if log_result.get("status") == "error":
                await status_message.edit_text(f"⚠️ {log_result.get('message')}")
                return

            files = log_result.get("files", {})
            if not files:
                await status_message.edit_text(f"⚠️ No log files found for '{server_name}'")
                return

            # Update the status message
            await status_message.edit_text("✅ Log files downloaded successfully. Sending files...")

            # Send files one by one
            for filename, filepath in files.items():
                if update.message:
                    with open(filepath, 'rb') as file:
                        await update.message.reply_document(
                            document=file,
                            filename=filename,
                            caption=f"📄 Log file: `{filename}` for server `{server_name}`"
                        )

            # Final confirmation message
            await self._reply_or_log(update, f"✅ All log files for `{server_name}` have been sent.")

        except Exception as e:
            logger.error(f"Error retrieving logs for '{server_name}': {e}", exc_info=True)
            if update.message:
                await update.message.reply_text(f"⚠️ Failed to retrieve logs: {e}")

    @authorized_only
    async def stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Gets detailed login statistics for a PSN server."""
        if await self._handle_missing_args(update, CMD_USAGE_STATS, context.args, 1):
            return

        server_name = context.args[0]
        server = await self._get_server_or_reply(update, server_name)
        if not server:
            return

        try:
            stats_info = await server.get_statistics(self.config)
            await self._reply_or_log(update, stats_info)
        except Exception as e:
            logger.error(f"Error getting stats for '{server_name}': {e}", exc_info=True)
            await self._reply_or_log(update, f"⚠️ Failed to get statistics: {e}")