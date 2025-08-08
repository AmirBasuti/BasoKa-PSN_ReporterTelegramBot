from telegram import Update
from telegram.ext import ContextTypes
from server_manager import ServerManager
from config import Config
import logging
from functools import wraps

logger = logging.getLogger(__name__)

def authorized_only(func):
    """Decorator to check if user is authorized before executing command"""
    @wraps(func)
    async def wrapper(self, update: Update, *args, **kwargs):
        if not update.effective_user:
            logger.warning("No user information in update")
            return
        
        user_id = update.effective_user.id
        if user_id not in self.config.authorized_user_ids:
            logger.info(f"Unauthorized access attempt from user ID: {user_id}")
            # Silently ignore unauthorized requests (no response)
            return
        
        return await func(self, update, *args, **kwargs)
    return wrapper

class BotHandler:
    def __init__(self, config: Config, server_manager: ServerManager):
        self.config = config
        self.server_manager = server_manager

    @authorized_only
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE = None):
        try:
            if update.message:
                await update.message.reply_text(
                    "🎮 **Welcome to BasoKa PSN Bot!**\n\n"
                    "📋 **Server Management:**\n"
                    "• `/add <name> <ip:port>` - Add PSN server\n"
                    "• `/list` - List all servers\n"
                    "• `/delete <name>` - Remove server\n\n"
                    "🎯 **PSN Checker Control:**\n"
                    "• `/startserver <name>` - Start PSN checker\n"
                    "• `/stopserver <name>` - Stop PSN checker\n"
                    "• `/status <name>` - Get detailed status\n"
                    "• `/is_running <name>` - Quick running check\n\n"
                    "📊 **Monitoring:**\n"
                    "• `/log <name> [lines]` - View recent logs\n"
                    "• `/stats <name>` - Login statistics\n"
                    "• `/statusall` - All servers status\n\n"
                    "⚡ **Bulk Operations:**\n"
                    "• `/startall` - Start all checkers\n"
                    "• `/stopall` - Stop all checkers\n\n"
                    "🔐 *Only authorized users can use this bot*"
                )
            else:
                logger.warning("Update message is None in start command.")
        except Exception as e:
            logger.error(f"Error in start command: {e}", exc_info=True)

    @authorized_only
    async def add(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            if len(context.args) < 2:
                if update.message:
                    await update.message.reply_text("Usage: /add <name> <ip:port>")
                else:
                    logger.warning("Update message is None in add command.")
                return
            self.server_manager.add_server(context.args[0], context.args[1])
            if update.message:
                await update.message.reply_text(f"✅ Server '{context.args[0]}' added.")
            else:
                logger.warning("Update message is None after adding server.")
        except Exception as e:
            logger.error(f"Error in add command: {e}", exc_info=True)

    @authorized_only
    async def status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            if len(context.args) < 1:
                if update.message:
                    await update.message.reply_text("Usage: /status <name>")
                else:
                    logger.warning("Update message is None in status command.")
                return
            server = self.server_manager.get_server(context.args[0])
            if not server:
                if update.message:
                    await update.message.reply_text(f"❌ Server '{context.args[0]}' not found.")
                else:
                    logger.warning("Update message is None when server not found.")
                return

            status = await server.get_status(self.config)
            if update.message:
                await update.message.reply_text(f"ℹ️ Status of '{server.name}': {status}")
            else:
                logger.warning("Update message is None after fetching server status.")
        except Exception as e:
            logger.error(f"Error in status command: {e}", exc_info=True)
            if update.message:
                await update.message.reply_text("⚠️ An error occurred while fetching server status.")
            else:
                logger.warning("Update message is None during error handling in status command.")

    @authorized_only
    async def list(self, update: Update,context: ContextTypes.DEFAULT_TYPE):

        servers = self.server_manager.servers()
        if not servers:
            await update.message.reply_text("No servers found. Use /add to add a server.")
            return
        server_list = "\n".join(f"• {name}" for name in servers)
        await update.message.reply_text(f"Available servers:\n{server_list}")

    @authorized_only
    async def statusall(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        results = []
        for name in self.server_manager.servers():
            server = self.server_manager.get_server(name)
            try:
                status = await server.get_status(self.config)
                results.append(f"✅ {name}: {status}")
            except Exception as e:
                results.append(f"⚠️ {name}: {e}")
        await update.message.reply_text("\n".join(results))

    @authorized_only
    async def delete(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if len(context.args) < 1:
            await update.message.reply_text("Usage: /delete <name>")
            return
        self.server_manager.delete_server(context.args[0])
        await update.message.reply_text(f"✅ Server '{context.args[0]}' deleted.")

    @authorized_only
    async def startserver(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if len(context.args) < 1:
            await update.message.reply_text("Usage: /startserver <name>")
            return
        server = self.server_manager.get_server(context.args[0])
        if not server:
            await update.message.reply_text(f"❌ Server '{context.args[0]}' not found.")
            return
        try:
            await server.start(self.config)
            await update.message.reply_text(f"✅ Server '{server.name}' started.")
        except Exception as e:
            await update.message.reply_text(f"⚠️ Failed to start '{server.name}': {e}")

    @authorized_only
    async def stopserver(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if len(context.args) < 1:
            await update.message.reply_text("Usage: /stopserver <name>")
            return
        server = self.server_manager.get_server(context.args[0])
        if not server:
            await update.message.reply_text(f"❌ Server '{context.args[0]}' not found.")
            return
        try:
            await server.stop(self.config)
            await update.message.reply_text(f"✅ Server '{server.name}' stopped.")
        except Exception as e:
            await update.message.reply_text(f"⚠️ Failed to stop '{server.name}': {e}")

    @authorized_only
    async def startall(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        results = await self.server_manager.start_all(self.config)
        if not results:
            results = ["No servers to start."]
        await update.message.reply_text("\n".join(results))

    @authorized_only
    async def stopall(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        results = await self.server_manager.stop_all(self.config)
        if not results:
            results = ["No servers to stop."]
        await update.message.reply_text("\n".join(results))

    @authorized_only
    async def is_running(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            if len(context.args) < 1:
                if update.message:
                    await update.message.reply_text("Usage: /is_running <name>")
                else:
                    logger.warning("Update message is None in is_running command.")
                return
            server = self.server_manager.get_server(context.args[0])
            if not server:
                if update.message:
                    await update.message.reply_text(f"❌ Server '{context.args[0]}' not found.")
                else:
                    logger.warning("Update message is None when server not found in is_running command.")
                return
            try:
                running_status = await server.is_running(self.config)
                if update.message:
                    await update.message.reply_text(f"✅ Running status of '{server.name}': {running_status}")
                else:
                    logger.warning("Update message is None after checking running status.")
            except Exception as e:
                if update.message:
                    await update.message.reply_text(f"⚠️ Failed to check running status of '{server.name}': {e}")
                logger.error(f"Error checking running status: {e}", exc_info=True)
        except Exception as e:
            logger.error(f"Error in is_running command: {e}", exc_info=True)

    @authorized_only
    async def log(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            if len(context.args) < 1:
                if update.message:
                    await update.message.reply_text("Usage: /log <name>")
                else:
                    logger.warning("Update message is None in log command.")
                return
            server = self.server_manager.get_server(context.args[0])
            if not server:
                if update.message:
                    await update.message.reply_text(f"❌ Server '{context.args[0]}' not found.")
                else:
                    logger.warning("Update message is None when server not found in log command.")
                return
            try:
                log_data = await server.get_log(self.config)
                if update.message:
                    await update.message.reply_text(f"✅ Log of '{server.name}':\n{log_data}")
                else:
                    logger.warning("Update message is None after retrieving log.")
            except Exception as e:
                if update.message:
                    await update.message.reply_text(f"⚠️ Failed to retrieve log of '{server.name}': {e}")
                logger.error(f"Error retrieving log: {e}", exc_info=True)
        except Exception as e:
            logger.error(f"Error in log command: {e}", exc_info=True)

    @authorized_only
    async def stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Get detailed login statistics for a PSN server"""
        try:
            if len(context.args) < 1:
                if update.message:
                    await update.message.reply_text("📋 **Usage**: `/stats <server_name>`\n\nExample: `/stats psn1`")
                return
                
            server = self.server_manager.get_server(context.args[0])
            if not server:
                if update.message:
                    await update.message.reply_text(f"❌ Server '{context.args[0]}' not found.\n\nUse `/list` to see available servers.")
                return

            stats_info = await server.get_statistics(self.config)
            if update.message:
                await update.message.reply_text(stats_info, parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Error in stats command: {e}", exc_info=True)
            if update.message:
                await update.message.reply_text(f"⚠️ Failed to get statistics: {e}")

    @authorized_only
    async def logs(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Enhanced log command with line count parameter"""
        try:
            if len(context.args) < 1:
                if update.message:
                    await update.message.reply_text("📋 **Usage**: `/logs <server_name> [lines]`\n\nExample: `/logs psn1 100`")
                return
                
            server = self.server_manager.get_server(context.args[0])
            if not server:
                if update.message:
                    await update.message.reply_text(f"❌ Server '{context.args[0]}' not found.")
                return
                
            # Get number of lines from second argument, default to 50
            lines = 50
            if len(context.args) > 1:
                try:
                    lines = int(context.args[1])
                    if lines <= 0 or lines > 500:
                        lines = 50
                except ValueError:
                    lines = 50
                    
            log_data = await server.get_log(self.config, lines)
            if update.message:
                await update.message.reply_text(log_data, parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Error in logs command: {e}", exc_info=True)
            if update.message:
                await update.message.reply_text(f"⚠️ Failed to retrieve log: {e}")
