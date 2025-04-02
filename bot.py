from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests
import os
from dotenv import load_dotenv
import logging
import re

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
BACKEND_URL = 'https://ischatbot.onrender.com/chat'

def format_for_telegram(text: str) -> str:
    """Format text for Telegram with proper Markdown V2 formatting"""
    # First, escape special characters for Markdown V2
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    
    # Format links - replace escaped characters inside link syntax
    link_pattern = r'\\\[(.*?)\\\]\\\((.*?)\\\)'
    text = re.sub(link_pattern, r'[\1](\2)', text)
    
    # Format bold text
    text = text.replace('\\*\\*', '*').replace('\\*\\*', '*')
    
    # Format italic text
    text = text.replace('\\_\\_', '_').replace('\\_\\_', '_')
    
    # Format emojis (don't escape emojis)
    emoji_pattern = r'([\U0001F300-\U0001F999🎓📚📧🏢])'
    text = re.sub(emoji_pattern, r'\1', text)
    
    return text

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    welcome_message = "Hello! 👋 I'm your Information Systems Department assistant at AAU\\. How can I help you today? 🎓"
    await update.message.reply_text(welcome_message, parse_mode='MarkdownV2')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /help is issued."""
    help_text = """
🎓 *IS Department Bot Help*

Available commands:
/start \- Start the conversation
/help \- Show this help message

You can ask me about:
• IS Department information
• Course details
• Faculty contacts
• Events and activities
• And more\!

Just type your question naturally and I'll help you out\! 😊
    """
    await update.message.reply_text(help_text, parse_mode='MarkdownV2')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming messages."""
    try:
        # Send typing action
        await update.message.chat.send_action('typing')
        
        # Make request to backend
        response = requests.post(
            BACKEND_URL,
            headers={'Content-Type': 'application/json'},
            json={'message': update.message.text},
            timeout=30
        )
        
        if response.status_code == 200:
            bot_response = response.json().get('response', 'Sorry, I encountered an error.')
            formatted_response = format_for_telegram(bot_response)
            await update.message.reply_text(
                formatted_response,
                parse_mode='MarkdownV2',
                disable_web_page_preview=True
            )
        else:
            await update.message.reply_text(
                "Sorry, I'm having trouble processing your request\\. Please try again later\\.",
                parse_mode='MarkdownV2'
            )
            
    except Exception as e:
        logger.error(f"Error in handle_message: {str(e)}")
        await update.message.reply_text(
            "Sorry, I encountered an error\\. Please try again later\\.",
            parse_mode='MarkdownV2'
        )

def main():
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Run the bot until the user presses Ctrl-C
    logger.info("Starting bot...")
    application.run_polling()

if __name__ == '__main__':
    main() 