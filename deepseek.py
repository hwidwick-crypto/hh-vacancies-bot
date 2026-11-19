"""Минимальный клиент DeepSeek через OpenAI-совместимый API."""

import os

import requests


DEFAULT_BASE_URL = "https://api.deepseek.com"
DEFAULT_MODEL = "deepseek-v4.1-flash"


class DeepSeekError(RuntimeError):
    """Ошибка настройки или запроса к DeepSeek."""


def _endpoint(base_url):
    base_url = (base_url or DEFAULT_BASE_URL).rstrip("/")
    if base_url.endswith("/chat/completions"):
        return base_url
    return base_url + "/chat/completions"


def generate_cover_letter(vacancy, candidate_profile):
    """Сгенерировать короткий персональный текст отклика на вакансию."""

    api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
    if not api_key:
        raise DeepSeekError("не задан DEEPSEEK_API_KEY")

    model = os.getenv("DEEPSEEK_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL
    base_url = os.getenv("DEEPSEEK_BASE_URL", DEFAULT_BASE_URL)

    employer = vacancy.get("employer") or {}
    area = vacancy.get("area") or {}
    experience = vacancy.get("experience") or {}
    schedule = vacancy.get("schedule") or {}
    snippet = vacancy.get("snippet") or {}

    vacancy_text = "\n".join(
        [
            "Название: " + str(vacancy.get("name", "")),
            "Компания: " + str(employer.get("name", "не указана")),
            "Город: " + str(area.get("name", "не указан")),
            "Опыт: " + str(experience.get("name", "не указан")),
            "График: " + str(schedule.get("name", "не указан")),
            "Требования: " + str(snippet.get("requirement", "не указаны")),
            "Обязанности: " + str(snippet.get("responsibility", "не указаны")),
        ]
    )

    profile = candidate_profile.strip() or "Профиль кандидата не заполнен. Не выдумывай навыки и опыт."
    system_prompt = (
        "Ты карьерный помощник. Пиши отклик на русском языке от лица кандидата. "
        "Используй только факты из профиля, ничего не придумывай. "
        "Текст должен быть вежливым, конкретным и занимать не больше 900 символов. "
        "Не добавляй тему письма, приветствие допустимо. В конце задай один вопрос о следующем шаге."
    )
    user_prompt = (
        "Профиль кандидата:\n" + profile + "\n\n" +
        "Вакансия:\n" + vacancy_text + "\n\n" +
        "Составь готовый текст отклика."
    )

    try:
        response = requests.post(
            _endpoint(base_url),
            headers={
                "Authorization": "Bearer " + api_key,
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "temperature": 0.7,
                "max_tokens": 500,
            },
            timeout=60,
        )
    except requests.RequestException as exc:
        raise DeepSeekError("не удалось подключиться к DeepSeek") from exc

    if response.status_code >= 400:
        try:
            error = response.json().get("error", {})
            detail = error.get("message", "") if isinstance(error, dict) else str(error)
        except (ValueError, AttributeError, TypeError):
            detail = ""
        suffix = ": " + detail if detail else ""
        raise DeepSeekError("DeepSeek вернул HTTP " + str(response.status_code) + suffix)

    try:
        data = response.json()
        content = data["choices"][0]["message"]["content"]
    except (ValueError, KeyError, IndexError, TypeError) as exc:
        raise DeepSeekError("DeepSeek вернул неожиданный формат ответа") from exc

    content = str(content).strip()
    if not content:
        raise DeepSeekError("DeepSeek вернул пустой текст")
    return content
