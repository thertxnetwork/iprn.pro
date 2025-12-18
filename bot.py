#!/usr/bin/env python3
"""
Simple Telegram Bot with Inline Keyboard Menu
"""

import os
import logging
import httpx
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get bot token and API bearer token from environment variables
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
BEARER_TOKEN = os.getenv('BEARER_TOKEN')
ADMIN_CHANNEL_ID = os.getenv('ADMIN_CHANNEL_ID')

if not BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable is not set!")
if not BEARER_TOKEN:
    raise ValueError("BEARER_TOKEN environment variable is not set!")
if not ADMIN_CHANNEL_ID:
    logger.warning("ADMIN_CHANNEL_ID not set - admin notifications will be disabled")

# API endpoint for fetching SMS
API_ENDPOINT = "https://api.iprn.pro/api/public/v1/stock/edr-account"


def get_main_keyboard() -> InlineKeyboardMarkup:
    """Create and return the main inline keyboard menu."""
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
    return InlineKeyboardMarkup(keyboard)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message with inline keyboard when the /start command is issued."""
    reply_markup = get_main_keyboard()
    
    welcome_text = (
        "👋 Welcome to the IPRN Bot!\n\n"
        "Please select an option from the menu below:"
    )
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)


async def fetch_sms_data(phone_number: str) -> dict:
    """Fetch SMS data from the API for a given phone number."""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            headers = {
                "Authorization": f"Bearer {BEARER_TOKEN}"
            }
            params = {
                "type": "sms",
                "b_number": phone_number
            }
            response = await client.get(API_ENDPOINT, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"Error fetching SMS data: {e}")
        return {"error": str(e)}


def format_sms_message(sms_data: dict) -> str:
    """Format SMS data for display in the bot."""
    if "error" in sms_data:
        return f"❌ Error fetching SMS data:\n{sms_data['error']}"
    
    data = sms_data.get("data", [])
    
    if not data:
        return "📭 No SMS messages found for this number."
    
    # Format each SMS message
    messages = []
    for idx, sms in enumerate(data, 1):
        msg_text = (
            f"📨 **Message {idx}**\n"
            f"━━━━━━━━━━━━━━━━\n"
            f"📅 **Date:** {sms.get('created_at', 'N/A')}\n"
            f"📞 **From:** Service\n"
            f"🎯 **To:** {sms.get('b_number', 'N/A')}\n"
            f"📊 **Status:** {sms.get('status', 'N/A')}\n"
            f"🌍 **Destination:** {sms.get('destination', 'N/A')}\n"
            f"━━━━━━━━━━━━━━━━\n"
            f"💬 **Message:**\n{sms.get('message', 'N/A')}\n"
        )
        messages.append(msg_text)
    
    return "\n\n".join(messages)


async def send_admin_notification(context: ContextTypes.DEFAULT_TYPE, user_info: dict, sms_data: dict, phone_number: str) -> None:
    """Send notification to admin channel about SMS fetch."""
    if not ADMIN_CHANNEL_ID:
        return
    
    try:
        # Extract user information
        user_id = user_info.get('id', 'Unknown')
        username = user_info.get('username', 'No username')
        first_name = user_info.get('first_name', 'Unknown')
        last_name = user_info.get('last_name', '')
        full_name = f"{first_name} {last_name}".strip()
        
        # Build notification message
        notification = (
            f"🔔 **SMS Fetch Notification**\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 **User Info:**\n"
            f"   • ID: `{user_id}`\n"
            f"   • Name: {full_name}\n"
            f"   • Username: @{username if username != 'No username' else 'N/A'}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📱 **Phone Number:** `{phone_number}`\n"
        )
        
        # Add SMS information (without body)
        data = sms_data.get("data", [])
        if data and "error" not in sms_data:
            notification += f"📊 **SMS Count:** {len(data)}\n━━━━━━━━━━━━━━━━━━━━\n"
            for idx, sms in enumerate(data[:3], 1):  # Show first 3 SMS details
                notification += (
                    f"\n**SMS {idx}:**\n"
                    f"   • Date: {sms.get('created_at', 'N/A')}\n"
                    f"   • Status: {sms.get('status', 'N/A')}\n"
                    f"   • Destination: {sms.get('destination', 'N/A')}\n"
                )
            if len(data) > 3:
                notification += f"\n_...and {len(data) - 3} more messages_\n"
        elif "error" in sms_data:
            notification += f"❌ **Error:** {sms_data['error']}\n"
        else:
            notification += "📭 **Result:** No messages found\n"
        
        # Send to admin channel
        await context.bot.send_message(
            chat_id=ADMIN_CHANNEL_ID,
            text=notification,
            parse_mode='Markdown'
        )
        logger.info(f"Admin notification sent for user {user_id}")
    except Exception as e:
        logger.error(f"Failed to send admin notification: {e}")


def get_sms_keyboard(phone_number: str) -> InlineKeyboardMarkup:
    """Create keyboard with refresh button for SMS view."""
    keyboard = [
        [
            InlineKeyboardButton("🔄 Refresh", callback_data=f'refresh_sms:{phone_number}'),
        ],
        [
            InlineKeyboardButton("🔙 Back to Menu", callback_data='back_to_menu'),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button presses on inline keyboard."""
    query = update.callback_query
    await query.answer()
    
    # Get the callback data
    action = query.data
    
    # Handle SMS refresh
    if action.startswith('refresh_sms:'):
        phone_number = action.split(':', 1)[1]
        await query.edit_message_text(text="🔄 Fetching SMS data...")
        
        sms_data = await fetch_sms_data(phone_number)
        formatted_message = format_sms_message(sms_data)
        reply_markup = get_sms_keyboard(phone_number)
        
        await query.edit_message_text(
            text=formatted_message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        return
    
    # Handle back to menu
    if action == 'back_to_menu':
        reply_markup = get_main_keyboard()
        await query.edit_message_text(
            text="📋 Main Menu - Select an option:",
            reply_markup=reply_markup
        )
        return
    
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
            "Send a phone number to view SMS messages.\n"
            "Use the inline buttons to navigate the bot."
        ),
        'refresh': "🔄 Menu refreshed!",
    }
    
    response_text = responses.get(action, "Unknown action")
    
    # Get the main keyboard for navigation
    reply_markup = get_main_keyboard()
    
    # Edit the message with new text and same keyboard
    await query.edit_message_text(text=response_text, reply_markup=reply_markup)


async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the menu again."""
    reply_markup = get_main_keyboard()
    
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
        "📱 To view SMS messages:\n"
        "Simply send a phone number (e.g., 37498316061)\n\n"
        "Use the inline buttons to navigate the bot."
    )
    await update.message.reply_text(help_text)


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle text messages from users."""
    message_text = update.message.text.strip()
    
    # Check if the message is a number (phone number)
    if message_text.isdigit():
        # Send a loading message
        loading_msg = await update.message.reply_text("🔍 Fetching SMS data...")
        
        # Fetch SMS data
        sms_data = await fetch_sms_data(message_text)
        formatted_message = format_sms_message(sms_data)
        reply_markup = get_sms_keyboard(message_text)
        
        # Send admin notification
        user_info = {
            'id': update.effective_user.id,
            'username': update.effective_user.username,
            'first_name': update.effective_user.first_name,
            'last_name': update.effective_user.last_name,
        }
        await send_admin_notification(context, user_info, sms_data, message_text)
        
        # Update the loading message with the results
        await loading_msg.edit_text(
            text=formatted_message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    else:
        # If not a number, provide help
        await update.message.reply_text(
            "ℹ️ Please send a phone number to view SMS messages.\n"
            "Example: 37498316061\n\n"
            "Or use /start to see the main menu."
        )


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
    
    # Register message handler for text messages (phone numbers)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    # Start the bot
    logger.info("Starting bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
