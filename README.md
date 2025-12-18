# IPRN Telegram Bot

A simple Telegram bot with inline keyboard menu functionality, built with Python and the `python-telegram-bot` library.

## Features

- 🤖 Simple and intuitive inline keyboard menu
- 📊 Status, Info, Settings, and Help menu options
- 🔄 Easy management with `manage.sh` script
- 🚀 Systemd integration for autostart
- 📝 Comprehensive logging
- 🔐 Environment-based configuration

## Prerequisites

- Python 3.7 or higher
- pip (Python package installer)
- A Telegram Bot Token (get it from [@BotFather](https://t.me/BotFather))
- Linux system with systemd (for autostart feature)

## Quick Start

### 1. Get Your Bot Token

1. Open Telegram and search for [@BotFather](https://t.me/BotFather)
2. Send `/newbot` command
3. Follow the instructions to create your bot
4. Copy the bot token provided by BotFather

### 2. Install the Bot

```bash
# Clone the repository (if not already done)
cd iprn.pro

# Install dependencies and setup environment
./manage.sh install
```

### 3. Configure the Bot

```bash
# Copy the example environment file
cp .env.example .env

# Edit the .env file and add your bot token
nano .env
# or
vim .env
```

Replace `your_bot_token_here` with your actual bot token from BotFather.

### 4. Start the Bot

```bash
./manage.sh start
```

## Management Commands

The `manage.sh` script provides the following commands:

### Basic Operations

```bash
# Install dependencies and setup environment
./manage.sh install

# Start the bot
./manage.sh start

# Stop the bot
./manage.sh stop

# Restart the bot
./manage.sh restart

# Check bot status
./manage.sh status

# View logs (last 50 lines)
./manage.sh logs

# Follow logs in real-time (Ctrl+C to stop)
./manage.sh logs -f
```

### Autostart (Systemd)

```bash
# Enable autostart (bot will start on system boot)
sudo ./manage.sh autostart

# Check autostart status
./manage.sh autostart-status
# or with sudo for detailed info
sudo ./manage.sh autostart-status

# Disable autostart
sudo ./manage.sh disable-autostart
```

### Help

```bash
# Show help message with all available commands
./manage.sh help
```

## Bot Features

Once the bot is running, you can interact with it on Telegram:

### Commands

- `/start` - Display the main menu with inline keyboard
- `/menu` - Show the menu again
- `/help` - Display help information

### Inline Keyboard Menu

The bot provides an interactive inline keyboard with the following options:

- **📊 Status** - Check bot status and system information
- **ℹ️ Info** - View bot information and version
- **⚙️ Settings** - Access settings menu (customizable)
- **❓ Help** - Display help and available commands
- **🔄 Refresh Menu** - Refresh the main menu

## Project Structure

```
iprn.pro/
├── bot.py              # Main bot application
├── manage.sh           # Management script
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variables template
├── .env               # Your configuration (create from .env.example)
├── .gitignore         # Git ignore rules
├── venv/              # Virtual environment (created by manage.sh)
├── bot.pid            # Process ID file (when running)
└── bot.log            # Bot logs (when running)
```

## Development

### Adding New Features

The bot is designed to be easily extensible. To add new menu options:

1. Edit `bot.py`
2. Add new buttons to the keyboard in the relevant functions
3. Add corresponding handlers in the `button_handler` function
4. Restart the bot with `./manage.sh restart`

### Example: Adding a New Button

```python
# In the keyboard definition
InlineKeyboardButton("🆕 New Feature", callback_data='new_feature')

# In the button_handler function
responses = {
    # ... existing responses ...
    'new_feature': "This is a new feature!",
}
```

## Troubleshooting

### Bot doesn't start

1. Check if the token is correctly set in `.env` file
2. Verify virtual environment is created: `ls -la venv/`
3. Check logs: `./manage.sh logs`
4. Ensure Python 3.7+ is installed: `python3 --version`

### Bot stops unexpectedly

1. Check logs for errors: `./manage.sh logs`
2. Verify network connectivity
3. Check if the bot token is still valid

### Autostart not working

1. Ensure you ran the command with sudo: `sudo ./manage.sh autostart`
2. Check service status: `sudo systemctl status iprn-bot`
3. Check system logs: `sudo journalctl -u iprn-bot -n 50`

### Permission Issues

If you encounter permission errors:

```bash
# Make sure manage.sh is executable
chmod +x manage.sh

# For autostart commands, use sudo
sudo ./manage.sh autostart
```

## Security Notes

- Never commit your `.env` file or bot token to version control
- The `.env` file is already included in `.gitignore`
- Keep your bot token secure and don't share it publicly
- Regularly update dependencies: `./manage.sh install`

## Requirements

See `requirements.txt` for Python dependencies:

- `python-telegram-bot` - Telegram Bot API wrapper
- `python-dotenv` - Environment variable management

## License

This project is open source and available for use and modification.

## Support

For issues, questions, or contributions, please open an issue on the repository.

## Credits

Built with [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) library.