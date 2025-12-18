# IPRN Telegram Bot

A Telegram bot with inline keyboard menu functionality and SMS fetching capabilities, built with Python and the `python-telegram-bot` library.

## Features

- 🤖 Simple and intuitive inline keyboard menu
- 📱 SMS fetching by phone number
- 📊 Status, Info, Settings, and Help menu options
- 🔄 Refresh button to re-fetch SMS data
- 🔔 Admin notifications for SMS fetches
- 🔄 Easy management with `manage.sh` script
- 🚀 Systemd integration for autostart
- 📝 Comprehensive logging
- 🔐 Environment-based configuration

## Prerequisites

- Python 3.7 or higher
- pip (Python package installer)
- A Telegram Bot Token (get it from [@BotFather](https://t.me/BotFather))
- Bearer Token for IPRN API access
- Admin Channel ID for notifications (optional)
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

# Edit the .env file and add your credentials
nano .env
# or
vim .env
```

Add the following to your `.env` file:
- `TELEGRAM_BOT_TOKEN` - Your bot token from BotFather
- `BEARER_TOKEN` - Your IPRN API bearer token
- `ADMIN_CHANNEL_ID` - Your admin channel ID for notifications (optional)

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

### SMS Fetching

Simply send a phone number (e.g., `37498316061`) to the bot, and it will:
1. Fetch SMS messages for that number from the IPRN API
2. Display the messages with details (date, status, destination, message body)
3. Provide a refresh button to fetch the latest messages
4. Send a notification to the admin channel (if configured)

### Inline Keyboard Menu

The bot provides an interactive inline keyboard with the following options:

- **📊 Status** - Check bot status and system information
- **ℹ️ Info** - View bot information and version
- **⚙️ Settings** - Access settings menu (customizable)
- **❓ Help** - Display help and available commands
- **🔄 Refresh Menu** - Refresh the main menu

### Admin Notifications

When a user fetches SMS data, the bot sends a notification to the configured admin channel with:
- User information (ID, name, username)
- Phone number queried
- SMS count and details (without message body)
- Timestamp

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
3. Check if the bot token and bearer token are still valid
4. Verify the API endpoint is accessible

### SMS not fetching

1. Verify `BEARER_TOKEN` is correctly set in `.env`
2. Check if the phone number format is correct
3. Verify API endpoint is accessible: `https://api.iprn.pro/api/public/v1/stock/edr-account`
4. Check logs for API errors: `./manage.sh logs`

### Admin notifications not working

1. Verify `ADMIN_CHANNEL_ID` is correctly set in `.env`
2. Ensure the bot is added to the admin channel as an administrator
3. Check that the channel ID format is correct (e.g., `-100XXXXXXXXXX` for channels)

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

- Never commit your `.env` file or tokens to version control
- The `.env` file is already included in `.gitignore`
- Keep your bot token, bearer token, and admin channel ID secure
- Don't share tokens or credentials publicly
- Regularly update dependencies: `./manage.sh install`
- Admin notifications don't include SMS message bodies for privacy

## Requirements

See `requirements.txt` for Python dependencies:

- `python-telegram-bot` - Telegram Bot API wrapper
- `python-dotenv` - Environment variable management
- `httpx` - HTTP client for API requests

## License

This project is open source and available for use and modification.

## Support

For issues, questions, or contributions, please open an issue on the repository.

## Credits

Built with [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) library.