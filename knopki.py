from telebot import types

# id городов с hh
goroda = [
    ["Москва", "1"],
    ["Санкт-Петербург", "2"],
    ["Новосибирск", "4"],
    ["Екатеринбург", "3"],
    ["Казань", "88"],
    ["Краснодар", "53"],
    ["Вся Россия", "113"]
]


def knopki_gorod():
    knopka = types.InlineKeyboardMarkup(row_width=2)
    knopka1 = types.InlineKeyboardButton(text="Москва", callback_data="gorod_1")
    knopka2 = types.InlineKeyboardButton(text="Санкт-Петербург", callback_data="gorod_2")
    knopka.add(knopka1, knopka2)
    knopka3 = types.InlineKeyboardButton(text="Новосибирск", callback_data="gorod_4")
    knopka4 = types.InlineKeyboardButton(text="Екатеринбург", callback_data="gorod_3")
    knopka.add(knopka3, knopka4)
    knopka5 = types.InlineKeyboardButton(text="Казань", callback_data="gorod_88")
    knopka6 = types.InlineKeyboardButton(text="Краснодар", callback_data="gorod_53")
    knopka.add(knopka5, knopka6)
    knopka7 = types.InlineKeyboardButton(text="Вся Россия", callback_data="gorod_113")
    knopka.add(knopka7)
    return knopka


def knopki_posle():
    knopka = types.InlineKeyboardMarkup()
    knopka1 = types.InlineKeyboardButton(text="выбрать другой город", callback_data="zanovo")
    knopka.add(knopka1)
    return knopka
