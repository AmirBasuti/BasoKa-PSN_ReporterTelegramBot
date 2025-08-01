# 🤖 BasoKa PSN Bot

A secure Telegram bot for remote server management with user authorization. Control your servers directly from Telegram with peace of mind.

## ✨ Features

- 🔐 **User Authorization**: Only authorized users can interact with the bot
- 🖥️ **Server Management**: Start, stop, monitor multiple servers
- 🔇 **Silent Security**: Unauthorized users get no response (stealth mode)
- 📊 **Real-time Status**: Check server health and running status
- 📝 **Server Logs**: View server logs remotely
- 🚀 **Bulk Operations**: Start/stop all servers at once

## 🚀 Quick Start

### 1. Clone & Setup
```bash
git clone https://github.com/AmirBasuti/BasoKa-PSN-Bot.git
cd BasoKa-PSN-Bot
```

### 2. Install uv (Fast Python Package Manager)
If you don't have uv installed:

**Windows:**
```powershell
pip install uv
```
uv dovumentation: [uv Docs](https://docs.astral.sh/uv/)

### 3. Install Dependencies
```bash
uv sync
```

### 4. Configure Environment
```bash
cp .env.example .env
```

Edit `.env` file:
```env
BOT_TOKEN=your_bot_token_from_botfather
AUTHORIZED_USER_IDS=123456789,987654321
```

### 5. Run the Bot
```bash
uv run python main.py
```

## 🔧 Configuration

### Getting Your Bot Token
1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Create a new bot with `/newbot`
3. Copy the token to your `.env` file

### Getting User IDs for Authorization
1. Send any message to [@userinfobot](https://t.me/userinfobot)
2. Copy your numeric ID
3. Add it to `AUTHORIZED_USER_IDS` in `.env`

**Example**: `AUTHORIZED_USER_IDS=123456789,987654321,555777888`

## 📱 Bot Commands

| Command        | Description                  | Usage                             |
|----------------|------------------------------|-----------------------------------|
| `/start`       | Welcome message and help     | `/start`                          |
| `/add`         | Add a new server             | `/add server1 192.168.1.100:8080` |
| `/list`        | Show all servers             | `/list`                           |
| `/status`      | Check specific server status | `/status server1`                 |
| `/statusall`   | Check all servers status     | `/statusall`                      |
| `/startserver` | Start a specific server      | `/startserver server1`            |
| `/stopserver`  | Stop a specific server       | `/stopserver server1`             |
| `/startall`    | Start all servers            | `/startall`                       |
| `/stopall`     | Stop all servers             | `/stopall`                        |
| `/is_running`  | Check if server is running   | `/is_running server1`             |
| `/delete`      | Remove a server              | `/delete server1`                 |
| `/log`         | View server logs             | `/log server1`                    |

## 🔒 Security Features

### Authorization System
- **Whitelist Only**: Only pre-approved user IDs can use the bot
- **Silent Rejection**: Unauthorized users receive no response
- **No Exposure**: Bot appears offline to unauthorized users

### Security Best Practices
```env
# Use environment variables for sensitive data
BOT_TOKEN=your_secret_token_here

# Limit access to specific users only
AUTHORIZED_USER_IDS=your_user_id,admin_user_id
```

## 🏗️ Project Structure

```
BasoKa-PSN-Bot/
├── main.py              # Entry point and bot setup
├── bot_handler.py       # Command handlers with authorization
├── config.py           # Configuration management
├── server_manager.py   # Server operations
├── server.py          # Server class definition
├── servers.json       # Server storage (auto-generated)
├── .env.example       # Environment template
└── README.md         # This file
```

## 🛠️ Development

### Why uv?
This project uses [uv](https://docs.astral.sh/uv/) for dependency management because it's:
- ⚡ **10-100x faster** than pip
- 🔒 **More secure** with lockfile support
- 🎯 **Better dependency resolution**
- 🔄 **Cross-platform consistency**

### Adding New Commands
1. Add method to `BotHandler` class in `bot_handler.py`
2. Apply `@authorized_only` decorator for security
3. Register handler in `main.py`

```python
@authorized_only
async def your_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Your command logic here
    pass
```

### Adding Dependencies
```bash
uv add package_name
```

### Development Workflow
```bash
# Install dev dependencies
uv sync --dev

# Run the bot
uv run python main.py

# Run tests (if available)
uv run pytest

# Format code (if you add formatters)
uv run black .
```

### Server Configuration
Servers are stored in `servers.json` with this structure:
```json
{
  "server_name": "ip:port"
}
```

## 🔍 Troubleshooting

### Common Issues

**Bot not responding to commands:**
- Check if your user ID is in `AUTHORIZED_USER_IDS`
- Verify bot token is correct
- Ensure the bot is running

**Environment variable errors:**
- Copy `.env.example` to `.env`
- Set all required variables
- Restart the bot after changes

**Dependency installation issues:**
- Try `uv sync --reinstall` to reinstall all packages
- Check Python version compatibility (3.8+)

**uv command not found:**
- Install uv using the installation commands above
- Restart your terminal/command prompt
- Add uv to your PATH if needed

**Server connection issues:**
- Verify server IP and port
- Check firewall settings
- Ensure server endpoints are accessible

### Logs
The bot logs all activities. Check console output for debugging information.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request


## 🙋‍♂️ Support

- 🐛 **Issues**: [GitHub Issues](https://github.com/AmirBasuti/BasoKa-PSN-Bot/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/AmirBasuti/BasoKa-PSN-Bot/discussions)

---

**⚡ Pro Tip**: Keep your `.env` file secure and never commit it to version control!
