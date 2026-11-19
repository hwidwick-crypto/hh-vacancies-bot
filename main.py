import telebot
from telebot import apihelper
import parser
import knopki
import deepseek
import os
from pathlib import Path
from dotenv import load_dotenv

# Telegram иногда отвечает медленно через локальный прокси/VPN.
# Повторяем временные сетевые ошибки вместо немедленного падения обработчика.
apihelper.CONNECT_TIMEOUT = 30
apihelper.READ_TIMEOUT = 60
apihelper.RETRY_ON_ERROR = True
apihelper.MAX_RETRIES = 3

load_dotenv(Path(__file__).with_name(".env"))
telegram_token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
if not telegram_token or telegram_token == "ВСТАВЬ_СЮДА_ТОКЕН":
    raise RuntimeError(
        "Не задан TELEGRAM_BOT_TOKEN. Создайте файл .env на основе .env.example "
        "и вставьте токен от @BotFather. Для cmd.exe: copy .env.example .env, "
        "затем notepad .env."
    )
bot = telebot.TeleBot(telegram_token)

user_data = {}


def _new_user():
    return {
        "gorod": "",
        "area": "",
        "rol": "",
        "profile": "",
        "vacancies": [],
        "stop_requested": False,
    }


def _search_stopped(chat_id):
    return user_data.get(chat_id, {}).get("stop_requested", False)


def _send_cover_letters(chat_id, vacancies, profile):
    """Автоматически подготовить отклики для первых пяти вакансий."""
    if _search_stopped(chat_id):
        return
    if not os.getenv("DEEPSEEK_API_KEY", "").strip():
        bot.send_message(
            chat_id,
            "Чтобы я сам подготовил тексты откликов, задай DEEPSEEK_API_KEY "
            "и перезапусти бота. Базовый URL настраивается через DEEPSEEK_BASE_URL.",
        )
        return

    bot.send_message(chat_id, "готовлю персональные отклики через DeepSeek...")
    for item in vacancies[:5]:
        if _search_stopped(chat_id):
            return
        try:
            letter = deepseek.generate_cover_letter(item, profile)
            title = item.get("name", "Вакансия")
            url = item.get("alternate_url", "")
            message = "Отклик на «" + title + "»\n\n" + letter
            if url:
                message += "\n\nОткрыть вакансию и отправить отклик: " + url
            bot.send_message(chat_id, message, disable_web_page_preview=True)
        except deepseek.DeepSeekError as exc:
            bot.send_message(chat_id, "Не смог подготовить отклик на «" + item.get("name", "вакансию") + "»: " + str(exc))


@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    user_data[chat_id] = _new_user()
    # print(user_data)
    bot.send_message(
        chat_id,
        "привет, я ищу вакансии на hh.ru и готовлю тексты откликов через DeepSeek.\n"
        "Сначала выбери город. Для персональных откликов потом задай /profile.",
        reply_markup=knopki.knopki_gorod(),
    )


@bot.message_handler(commands=['profile'])
def profile_command(message):
    chat_id = message.chat.id
    if chat_id not in user_data:
        user_data[chat_id] = _new_user()
    user_data[chat_id]["awaiting_profile"] = True
    bot.send_message(
        chat_id,
        "Напиши одним сообщением свой профиль: навыки, опыт, стек, желаемую позицию и имя. "
        "Я буду использовать только эти данные и не стану придумывать факты.",
    )


@bot.message_handler(commands=['stop'])
def stop_command(message):
    chat_id = message.chat.id
    if chat_id not in user_data:
        user_data[chat_id] = _new_user()
    user_data[chat_id]["stop_requested"] = True
    bot.send_message(chat_id, "Остановил отправку вакансий и откликов.")


# хз почему но без этого не работает
@bot.callback_query_handler(func=None)
def obrabotka_knopok(call):
    chat_id = call.message.chat.id
    if call.data == "zanovo":
        user_data[chat_id] = _new_user()
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, "выбери город заново", reply_markup=knopki.knopki_gorod())
        return
    if call.data.startswith("gorod_"):
        area = call.data.split("_")[1]
        gorod = ""
        for stroka in knopki.goroda:
            if stroka[1] == area:
                gorod = stroka[0]
        current = user_data.get(chat_id, _new_user())
        current.update({"gorod": gorod, "area": area, "rol": ""})
        user_data[chat_id] = current
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, "город: " + gorod + "\nтеперь напиши кем хочешь работать, например python разработчик")


@bot.message_handler(content_types=['text'])
def poluchit_rol(message):
    chat_id = message.chat.id
    if message.text.startswith("/"):
        return
    if chat_id not in user_data:
        bot.send_message(chat_id, "нажми /start")
        return
    if user_data[chat_id].get("awaiting_profile"):
        user_data[chat_id]["profile"] = message.text.strip()
        user_data[chat_id]["awaiting_profile"] = False
        bot.send_message(chat_id, "профиль сохранён. Теперь выбери город и напиши желаемую должность.")
        return
    if user_data[chat_id]["area"] == "":
        bot.send_message(chat_id, "сначала выбери город кнопкой")
        return

    rol = message.text
    user_data[chat_id]["rol"] = rol
    user_data[chat_id]["stop_requested"] = False
    bot.send_message(chat_id, "ищу вакансии, подожди немного...")

    vac = parser.poisk_vac(rol, user_data[chat_id]["area"])
    if _search_stopped(chat_id):
        return
    if len(vac) == 0:
        bot.send_message(chat_id, "ничего не нашел, попробуй написать по другому")
        return

    sred_zp = parser.sred_zp(vac)
    mediana = parser.mediana_zp(vac)
    user_data[chat_id]["vacancies"] = vac
    otvet = "вакансий в выборке: " + str(len(vac)) + "\n"
    otvet = otvet + "средняя зп: " + str(int(sred_zp)) + " руб.\n"
    otvet = otvet + "медиана: " + str(int(mediana)) + " руб.\n\n"

    k = 0
    for item in vac:
        if k == 5:
            break
        if item['salary'] != None:
            if item['salary']['from'] != None:
                zp = item['salary']['from']
            elif item['salary']['to'] != None:
                zp = item['salary']['to']
            else:
                zp = 0
            if zp == 0:
                otvet = otvet + item['name'] + "\nзп не указана\n"
            else:
                otvet = otvet + item['name'] + "\n" + str(zp) + " " + item['salary']['currency'] + "\n"
        else:
            otvet = otvet + item['name'] + "\nзп не указана\n"
        otvet = otvet + item['alternate_url'] + "\n\n"
        k = k + 1

    if _search_stopped(chat_id):
        return
    bot.send_message(chat_id, otvet, reply_markup=knopki.knopki_posle(), disable_web_page_preview=True)
    _send_cover_letters(chat_id, vac, user_data[chat_id].get("profile", ""))


bot.polling(none_stop=True)
