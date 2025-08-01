from telegram import Update
from telegram.ext import ContextTypes
from server_manager import ServerManager
from config import Config
import logging

logger = logging.getLogger(__name__)

class BotHandler:
    def __init__(self, config: Config, server_manager: ServerManager):
        self.config = config
        self.server_manager = server_manager

    @staticmethod
    async def start(update: Update):
        try:
            if update.message:
                await update.message.reply_text(
                    "👋 Welcome to the Server Manager Basoka Bot! Use\n"
                    "/add, \n"
                    "/list, \n"
                    "/status, \n"
                    "/stopall \n"
                    "/startall, \n"
                    "/stopserver, \n"
                    "/startserver,\n"
                    "to manage your servers."
                )
            else:
                logger.warning("Update message is None in start command.")
        except Exception as e:
            logger.error(f"Error in start command: {e}", exc_info=True)

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

    async def list(self, update: Update,context: ContextTypes.DEFAULT_TYPE):

        servers = self.server_manager.servers()
        if not servers:
            await update.message.reply_text("No servers found. Use /add to add a server.")
            return
        server_list = "\n".join(f"• {name}" for name in servers)
        await update.message.reply_text(f"Available servers:\n{server_list}")

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

    async def delete(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if len(context.args) < 1:
            await update.message.reply_text("Usage: /delete <name>")
            return
        self.server_manager.delete_server(context.args[0])
        await update.message.reply_text(f"✅ Server '{context.args[0]}' deleted.")

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

    async def startall(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        results = await self.server_manager.start_all(self.config)
        if not results:
            results = ["No servers to start."]
        await update.message.reply_text("\n".join(results))

    async def stopall(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        results = await self.server_manager.stop_all(self.config)
        if not results:
            results = ["No servers to stop."]
        await update.message.reply_text("\n".join(results))

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
                    await update.message.reply_text(f"✅ Log of '{server.name}':\n{log_data['log']}")
                else:
                    logger.warning("Update message is None after retrieving log.")
            except Exception as e:
                if update.message:
                    await update.message.reply_text(f"⚠️ Failed to retrieve log of '{server.name}': {e}")
                logger.error(f"Error retrieving log: {e}", exc_info=True)
        except Exception as e:
            logger.error(f"Error in log command: {e}", exc_info=True)
