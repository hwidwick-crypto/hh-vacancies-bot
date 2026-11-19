import html
import re

import requests


def _strip_html(value):
    value = html.unescape(value)
    return re.sub(r"<[^>]+>", "", value).strip()


def _poisk_vac_web(rol, area):
    """Резервный поиск через HTML-страницу HH, если API недоступен."""
    url = "https://hh.ru/search/vacancy"
    params = {"text": rol, "area": area, "items_on_page": 50}
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, params=params, headers=headers, timeout=20)
        res.raise_for_status()
    except requests.RequestException:
        return []

    page = res.text
    starts = [match.start() for match in re.finditer(r'data-qa="vacancy-serp__vacancy"', page)]
    vacancies = []
    for index, start in enumerate(starts):
        end = starts[index + 1] if index + 1 < len(starts) else len(page)
        card = page[start:end]
        title_match = re.search(
            r'data-qa="serp-item__title-text"[^>]*>(.*?)</', card, re.DOTALL
        )
        url_match = re.search(
            r'<a[^>]+data-qa="serp-item__title"[^>]+href="([^"]+)',
            card,
            re.DOTALL,
        )
        if not title_match or not url_match:
            continue

        title = _strip_html(title_match.group(1))
        vacancy_url = html.unescape(url_match.group(1))
        vacancies.append({"name": title, "alternate_url": vacancy_url, "salary": None})

    return vacancies


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
    try:
        res = requests.get(url, params=params, headers=headers, timeout=20)
    except requests.RequestException:
        return []
    if res.status_code != 200:
        return _poisk_vac_web(rol, area)
    try:
        data = res.json()
    except ValueError:
        return []
    # print(data)
    return data.get('items', [])


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
