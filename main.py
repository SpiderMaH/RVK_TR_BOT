from dotenv import load_dotenv
from trello import TrelloClient
import os
import time
from telegram.ext import *
from telegram import Bot
from queue import Queue
import asyncio

load_dotenv()

TRELLO_API_KEY = os.getenv('TRELLO_API_KEY')
TRELLO_API_SECRET = os.getenv('TRELLO_API_SECRET')
TRELLO_TOKEN = os.getenv('TRELLO_TOKEN')
TRELLO_TOKEN_SECRET = os.getenv('TRELLO_TOKEN_SECRET')
BOARD_ID = os.getenv('BOARD_ID')
LIST_ID = os.getenv('LIST_ID')

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
AUTHORIZATION_KEY = os.getenv('AUTHORIZATION_KEY')

bot = Bot(token=TELEGRAM_BOT_TOKEN)

authorized_users = set()

async def start(update, context):
    user_key = context.args[0] if context.args else ''
    chat_id = update.message.chat_id
    print(chat_id)

    if user_key == AUTHORIZATION_KEY:
        authorized_users.add(chat_id)
        await update.message.reply_text('Authorization successful. You are now subscribed to notifications.')
    else:
        await update.message.reply_text('Authorization failed. Please provide a valid key.')

client = TrelloClient(
    api_key=TRELLO_API_KEY,
    api_secret=TRELLO_API_SECRET,
    token=TRELLO_TOKEN,
    #token_secret=TRELLO_TOKEN_SECRET
)


def get_latest_action():
    board = client.get_board(BOARD_ID)
    print(board)
    list_to_monitor = [lst for lst in board.list_lists() if lst.id == LIST_ID][0]
    print(list_to_monitor)
    actions = list_to_monitor.fetch_actions(action_filter="createCard")
    return actions[0] if actions else None


application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

application.add_handler(CommandHandler('start', start))

# Run bot
#application.run_polling(1.0)


async def run():
    latest_action = get_latest_action()
    while True:
        new_action = get_latest_action()
        print(new_action)
        if new_action and new_action['id'] != latest_action['id']:
            await application.bot.send_message(chat_id=-998959777, text=f"Добавлен новый кандидат: {new_action['data']['card']['name']}")
            latest_action = new_action
        time.sleep(30)

if __name__ == "__main__":
    asyncio.run(run())
