#!/usr/bin/env python3
"""
Simple Telegram Bot with Inline Keyboard Menu
"""

import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get bot token from environment variable
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

if not BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable is not set!")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message with inline keyboard when the /start command is issued."""
    keyboard = [
        [
            InlineKeyboardButton("📊 Status", callback_data='status'),
            InlineKeyboardButton("ℹ️ Info", callback_data='info'),
        ],
        [
            InlineKeyboardButton("⚙️ Settings", callback_data='settings'),
            InlineKeyboardButton("❓ Help", callback_data='help'),
        ],
        [
            InlineKeyboardButton("🔄 Refresh Menu", callback_data='refresh'),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = (
        "👋 Welcome to the IPRN Bot!\n\n"
        "Please select an option from the menu below:"
    )
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button presses on inline keyboard."""
    query = update.callback_query
    await query.answer()
    
    # Get the callback data
    action = query.data
    
    # Define responses for each button
    responses = {
        'status': "✅ Bot Status: Online\n📊 All systems operational",
        'info': (
            "ℹ️ Bot Information:\n\n"
            "Name: IPRN Bot\n"
            "Version: 1.0.0\n"
            "Framework: python-telegram-bot\n"
            "Status: Active"
        ),
        'settings': (
            "⚙️ Settings Menu:\n\n"
            "Here you can configure bot settings.\n"
            "(This is a demo - add your settings here)"
        ),
        'help': (
            "❓ Help Information:\n\n"
            "Available Commands:\n"
            "/start - Show main menu\n"
            "/menu - Show menu again\n"
            "/help - Show this help message\n\n"
            "Use the inline buttons to navigate the bot."
        ),
        'refresh': "🔄 Menu refreshed!",
    }
    
    response_text = responses.get(action, "Unknown action")
    
    # Create the same keyboard for navigation
    keyboard = [
        [
            InlineKeyboardButton("📊 Status", callback_data='status'),
            InlineKeyboardButton("ℹ️ Info", callback_data='info'),
        ],
        [
            InlineKeyboardButton("⚙️ Settings", callback_data='settings'),
            InlineKeyboardButton("❓ Help", callback_data='help'),
        ],
        [
            InlineKeyboardButton("🔄 Refresh Menu", callback_data='refresh'),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Edit the message with new text and same keyboard
    await query.edit_message_text(text=response_text, reply_markup=reply_markup)


async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the menu again."""
    keyboard = [
        [
            InlineKeyboardButton("📊 Status", callback_data='status'),
            InlineKeyboardButton("ℹ️ Info", callback_data='info'),
        ],
        [
            InlineKeyboardButton("⚙️ Settings", callback_data='settings'),
            InlineKeyboardButton("❓ Help", callback_data='help'),
        ],
        [
            InlineKeyboardButton("🔄 Refresh Menu", callback_data='refresh'),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "📋 Main Menu - Select an option:",
        reply_markup=reply_markup
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send help information."""
    help_text = (
        "❓ Help Information:\n\n"
        "Available Commands:\n"
        "/start - Show main menu\n"
        "/menu - Show menu again\n"
        "/help - Show this help message\n\n"
        "Use the inline buttons to navigate the bot."
    )
    await update.message.reply_text(help_text)


def main() -> None:
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()

    # Register command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("menu", menu))
    application.add_handler(CommandHandler("help", help_command))
    
    # Register callback query handler for inline buttons
    application.add_handler(CallbackQueryHandler(button_handler))

    # Start the bot
    logger.info("Starting bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
