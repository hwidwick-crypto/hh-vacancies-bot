import telebot
import parser
import knopki

bot = telebot.TeleBot("ВСТАВЬ_СЮДА_ТОКЕН")

user_data = {}


@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    user_data[chat_id] = {"gorod": "", "area": "", "rol": ""}
    # print(user_data)
    bot.send_message(chat_id, "привет, я ищу вакансии на hh.ru\nсначала выбери город", reply_markup=knopki.knopki_gorod())


# хз почему но без этого не работает
@bot.callback_query_handler(func=None)
def obrabotka_knopok(call):
    chat_id = call.message.chat.id
    if call.data == "zanovo":
        user_data[chat_id] = {"gorod": "", "area": "", "rol": ""}
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, "выбери город заново", reply_markup=knopki.knopki_gorod())
        return
    if call.data.startswith("gorod_"):
        area = call.data.split("_")[1]
        gorod = ""
        for stroka in knopki.goroda:
            if stroka[1] == area:
                gorod = stroka[0]
        user_data[chat_id] = {"gorod": gorod, "area": area, "rol": ""}
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
    if user_data[chat_id]["area"] == "":
        bot.send_message(chat_id, "сначала выбери город кнопкой")
        return

    rol = message.text
    user_data[chat_id]["rol"] = rol
    bot.send_message(chat_id, "ищу вакансии, подожди немного...")

    vac = parser.poisk_vac(rol, user_data[chat_id]["area"])
    if len(vac) == 0:
        bot.send_message(chat_id, "ничего не нашел, попробуй написать по другому")
        return

    sred_zp = parser.sred_zp(vac)
    mediana = parser.mediana_zp(vac)
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

    bot.send_message(chat_id, otvet, reply_markup=knopki.knopki_posle(), disable_web_page_preview=True)


bot.polling(none_stop=True)
