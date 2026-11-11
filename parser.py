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
    data = res.json()
    # print(data)
    vac = data['items']
    for item in vac:
        print(item['name'])
        print(item['salary']['from'])
    return vac
