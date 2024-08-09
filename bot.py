import os
import time
from telegram import Bot, Update, ReplyKeyboardMarkup
from telegram.ext import CommandHandler, Updater

# Ваш токен бота от BotFather
TOKEN = 'ВАШ_ТОКЕН'
CHAT_ID = 'ВАШ_CHAT_ID'  # ID чата, куда будут отправляться уведомления

# Инициализация бота
bot = Bot(token=TOKEN)

# IP или домены ваших VPS серверов
SERVERS = {
    'SWE': '1.2.3.4',  # замените на IP или домены серверов
    'NYC': '5.6.7.8',
    'LON': '9.10.11.12',
    'FRA': '13.14.15.16'
}

# Статусы серверов (изначально все считаем онлайн)
server_statuses = {name: True for name in SERVERS}

def check_server_status():
    global server_statuses
    for name, ip in SERVERS.items():
        response = os.system(f"ping -c 1 {ip}")
        if response == 0:  # Сервер доступен
            if not server_statuses[name]:  # Если сервер был оффлайн, теперь он онлайн
                bot.send_message(chat_id=CHAT_ID, text=f"🟢 {name} - сервер онлайн")
                server_statuses[name] = True
        else:  # Сервер недоступен
            if server_statuses[name]:  # Если сервер был онлайн, теперь он оффлайн
                bot.send_message(chat_id=CHAT_ID, text=f"🔴 {name} - сервер оффлайн")
                server_statuses[name] = False

def get_all_servers_status():
    statuses = []
    for name, ip in SERVERS.items():
        response = os.system(f"ping -c 1 {ip}")
        if response == 0:  # Сервер доступен
            statuses.append(f"🟢 {name}")
        else:  # Сервер недоступен
            statuses.append(f"🔴 {name}")
    return "\n".join(statuses)

def status_command(update: Update, context):
    status_report = get_all_servers_status()
    update.message.reply_text(status_report)

def start_command(update: Update, context):
    # Сообщение и клавиатура с кнопкой "Проверить статус серверов"
    keyboard = [[
        "Проверить статус серверов"  # Кнопка с текстом
    ]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    # Отправляем сообщение с клавиатурой
    update.message.reply_text("Текст текст текст", reply_markup=reply_markup)

if __name__ == '__main__':
    # Настраиваем обработчики команд для Telegram
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Команда /start
    dispatcher.add_handler(CommandHandler('start', start_command))

    # Команда /status
    dispatcher.add_handler(CommandHandler('status', status_command))

    # Запуск бота
    updater.start_polling()

    # Цикл проверки статуса серверов
    while True:
        check_server_status()
        time.sleep(60)  # Проверка каждые 60 секунд