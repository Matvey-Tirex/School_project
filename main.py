#Импорт нужных библиотек
import telebot
import schedule
import time
from threading import Thread
from telebot import types
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
import datetime

#Создание токена и списка
bot = telebot.TeleBot()
memoris = []

#Приветствие
@bot.message_handler(commands=["start"])
def welcome(message):
    print("Code works")
    bot.send_message(message.chat.id, "Добро пожаловать это бот напоминалка 3000\nСпомощью него ты можешь ставить напоминания\nА также он может отсылать погоду на день =)\n\nНадеюсь вам поравится новый бот.")
    keyboard = InlineKeyboardMarkup()
    button1 = InlineKeyboardButton(text="Настройки событий", callback_data="settings")

    print(message)
    keyboard.add(button1)

    bot.send_message(message.chat.id, "Нажмите кнопку ниже, чтобы создать новое напоминание:", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data == "settings")
def change_events(call):
    keyboard1 = InlineKeyboardMarkup()
    button1 = InlineKeyboardButton(text="Добавить событие", callback_data="add_memoris")
    button2 = InlineKeyboardButton(text="Удалить событие", callback_data="del_memoris")
    keyboard1.add(button1, button2)

    #Проверка есть ли события в списке
    bot.send_message(call.message.chat.id, f"На данный момент у вас есть такие события как:", reply_markup=keyboard1)


#_________2__________
def get_time(message):
    time_event = message.text
    new_message = bot.send_message(message.chat.id, "Напишите ниже текст для напоминания")
    bot.register_next_step_handler(new_message, lambda message: get_text(time_event, message))

#________________3________________
def get_text(time_event, message):
    name_event = message.text
    chat_id = message.chat.id
    add_event(time_event,name_event,chat_id)


#_______________Основное действие_______________________
#Создаём функцию которая добавляет новое событие в список
def add_event(time_event, name_event, chat_id):
    memoris.append({
        "time_event" : time_event,
        "name_event" : name_event,
        "chat_id" : chat_id
    })
    bot.send_message(chat_id, f"Напоминание установлено на {time_event}")
@bot.callback_query_handler(func=lambda call: call.data == "add_memoris")

def chk_press(call):
    new_message = bot.send_message(call.message.chat.id, "Напишите ниже время напоминания(ЧЧ:ММ)")
    bot.register_next_step_handler(new_message, get_time)

# Функция для отправки напоминаний
def send_reminders():
    now = datetime.datetime.now().strftime("%H:%M")
    for reminder in list(memoris):  # Итерируемся по копии списка
        if reminder["time_event"] == now:
            bot.send_message(reminder["chat_id"], f"Напоминание: {reminder['name_event']}")
            memoris.remove(reminder)  # Удаляем напоминание после отправки

# Запуск планировщика
def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)


# Функция для удаления напоминания
@bot.callback_query_handler(func=lambda call: call.data == "del_memoris")
def delete_reminder_menu(call):
    keyboard = InlineKeyboardMarkup()
    for i, reminder in enumerate(memoris):
        text = f"{reminder['time_event']} - {reminder['name_event']}"
        callback_data = f"delete_reminder_{i}"
        button = InlineKeyboardButton(text=text, callback_data=callback_data)
        keyboard.add(button)

    if not memoris:
        bot.send_message(call.message.chat.id, "У вас нет активных напоминаний.")
        return

    bot.send_message(call.message.chat.id, "Выберите напоминание для удаления:", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data.startswith("delete_reminder_"))
def delete_reminder(call):
    index_str = call.data.split("_")[2]
    try:
        index = int(index_str)
        if 0 <= index < len(memoris):
            del memoris[index]
            bot.send_message(call.message.chat.id, "Напоминание удалено!")
            delete_reminder_menu(call)  # Обновляем список после удаления
        else:
            bot.send_message(call.message.chat.id, "Неверный индекс напоминания.")
    except ValueError:
        bot.send_message(call.message.chat.id, "Ошибка при удалении напоминания.")


if __name__ == '__main__':
    # Создаем и запускаем планировщик в отдельном потоке
    schedule.every(1).minutes.do(send_reminders)  # Проверяем каждую минуту
    scheduler_thread = Thread(target=run_scheduler)
    scheduler_thread.daemon = True  # Позволяет завершить поток, когда основная программа завершается
    scheduler_thread.start()

    # Запускаем бота
    bot.infinity_polling()