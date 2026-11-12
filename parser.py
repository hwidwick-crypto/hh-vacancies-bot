import requests


def poisk_vac(rol, area):
    url = "https://api.hh.ru/vacancies"
    params = {
        "text": rol,
        "area": area,
        "per_page": 50,
        "page": 0
    }
    headers = {
        "User-Agent": "hh-student-bot/1.0 (contact: your_email@yandex.ru)"
    }
    res = requests.get(url, params=params, headers=headers)
    # костыль чтобы не вылетало
    if res.status_code != 200:
        return []
    data = res.json()
    # print(data)
    vac = data['items']
    return vac


def sred_zp(vac):
    summa = 0
    count = 0
    for item in vac:
        # тут берем зп если она вообще есть
        if item['salary'] != None:
            if item['salary']['currency'] == 'RUR':
                if item['salary']['from'] != None:
                    summa = summa + item['salary']['from']
                    count = count + 1
                elif item['salary']['to'] != None:
                    summa = summa + item['salary']['to']
                    count = count + 1
    if count == 0:
        return 0
    sred_zp = summa / count
    return sred_zp


def mediana_zp(vac):
    spisok_zp = []
    for item in vac:
        if item['salary'] != None:
            if item['salary']['currency'] == 'RUR':
                if item['salary']['from'] != None:
                    spisok_zp.append(item['salary']['from'])
                elif item['salary']['to'] != None:
                    spisok_zp.append(item['salary']['to'])
    # print("зашло в цикл")
    if len(spisok_zp) == 0:
        return 0
    # сортируем массив для медианы
    spisok_zp.sort()
    i = int(len(spisok_zp) / 2)
    if len(spisok_zp) % 2 == 0:
        mediana = (spisok_zp[i - 1] + spisok_zp[i]) / 2
    else:
        mediana = spisok_zp[i]
    return mediana
