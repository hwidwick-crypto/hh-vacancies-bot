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
    vac = data['items']
    for item in vac:
        if item['salary'] != None:
            if item['salary']['from'] != None:
                print(item['name'] + " " + str(item['salary']['from']))
            elif item['salary']['to'] != None:
                print(item['name'] + " " + str(item['salary']['to']))
            else:
                print(item['name'])
        else:
            print(item['name'])
    return vac


def sred_zp(vac):
    summa = 0
    count = 0
    for item in vac:
        # тут берем зп если она вообще есть
        if item['salary'] != None:
            if item['salary']['from'] != None:
                summa = summa + item['salary']['from']
                count = count + 1
            elif item['salary']['to'] != None:
                summa = summa + item['salary']['to']
                count = count + 1
    if count == 0:
        return 0
    return summa / count
