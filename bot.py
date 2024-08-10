import os
import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters, JobQueue

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Ваш токен бота от BotFather
TOKEN = 'your_bot_token'

# ID пользователя, который будет получать уведомления о статусе серверов
NOTIFY_USER_ID = 'your_chat_id'

# IP или домены ваших VPS серверов
SERVERS = {
    'TUR, ANR': '1.2.3.4',
    'GER, BRL': '5.6.7.8',
    'USA, NY': '9.10.11.12'
}

server_statuses = {name: True for name in SERVERS}

async def check_server_status(context: ContextTypes.DEFAULT_TYPE):
    global server_statuses
    logging.info("Проверка статуса серверов...")
    for name, ip in SERVERS.items():
        logging.info(f"Пинг сервера {name} ({ip})...")
        response = os.system(f"ping -c 1 {ip} > /dev/null 2>&1")
        is_online = (response == 0)
        
        if is_online != server_statuses[name]:
            if is_online:
                message = f"🟢 {name} - сервер онлайн"
            else:
                message = f"🔴 {name} - сервер оффлайн"
                
            server_statuses[name] = is_online
            
            try:
                logging.info(f"Статус изменен. Отправка уведомления пользователю {NOTIFY_USER_ID}: {message}")
                bot = Bot(token=TOKEN)
                await bot.send_message(chat_id=NOTIFY_USER_ID, text=message)
            except Exception as e:
                logging.error(f"Ошибка при отправке сообщения: {e}")

def get_all_servers_status():
    statuses = []
    logging.info("Получение статуса всех серверов...")
    for name, ip in SERVERS.items():
        logging.info(f"Пинг сервера {name} ({ip})...")
        response = os.system(f"ping -c 1 {ip} > /dev/null 2>&1")
        if response == 0:
            statuses.append(f"🟢 {name}")
        else:
            statuses.append(f"🔴 {name}")
    return "\n".join(statuses)

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info(f"Получена команда /status от пользователя {update.message.chat_id}")
    status_report = get_all_servers_status()
    await update.message.reply_text(status_report)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info(f"Получена команда /start от пользователя {update.message.chat_id}")
    keyboard = [[KeyboardButton("Проверить статус серверов")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Привет! 👋\n\nЯ телеграм бот сервиса @beatVPN_bot, который помогает проверить статус наших серверов, к которым вы подключаетесь.\nЕсли у вас не подключается к серверу, вы всегда можете проверить его статус.\n\nНажмите кнопку ниже, чтобы я проверил наши сервера и прислал их статусы. 🙂", reply_markup=reply_markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "Проверить статус серверов":
        logging.info(f"Получено сообщение 'Проверить статус серверов' от пользователя {update.message.chat_id}")
        await status_command(update, context)

def main():
    application = ApplicationBuilder().token(TOKEN).build()
    
    # Установка JobQueue для периодической проверки
    job_queue = application.job_queue
    job_queue.run_repeating(check_server_status, interval=15, first=0)
    
    # Добавление обработчиков команд и сообщений
    application.add_handler(CommandHandler('start', start_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CommandHandler('status', status_command))

    logging.info("Запуск бота...")
    # Запускаем бота
    application.run_polling()

if __name__ == '__main__':
    main()
