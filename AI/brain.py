import json
import re

from config import config_p
from openai import AsyncOpenAI, RateLimitError

client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=config_p.ai_api_key
)

SYSTEM_PROMPT = """
You are a professional content analyst for Pulse Bot. Your task is to analyze a block of text from a Telegram channel and compile a brief, live digest.

IMPORTANT: The text block is separated by tags [POST ID {ID} {date}]

PROCESSING RULES:
1. CLASSIFICATION: If multiple posts describe a single event (e.g., a stream announcement and a later time change) combine them into a single entity. If the posts are about different things, create separate blocks.
2. FILTERING: Completely ignore advertisements (casinos, betting, promo codes, external links to products), spam, and meaningless messages (just stickers or greetings without context).
3. SUMMARY: Describe the essence of the event as concisely as possible (2–7 sentences).
4. STYLE: Use appropriate emojis to add liveliness, but don’t overuse them.
5. DATES: STRICTLY extract the date from the [POST ID ... {date}] tag for each event. If an event spans multiple posts, use the date of the earliest post as the event’s start date.

RESPONSE FORMAT:
You must respond STRICTLY in JSON format. No extra text before or after the JSON.
JSON structure:
{
  “events”: [
    {
      “event_date”: “YYYY-MM-DD”,
      “topic”: “Event title with emojis”,
      “result”: “Brief description of the event (2–7 sentences)”,
      “list”: “List of POST IDs included in the event”
    }
  ]
}
"""

LANGUAGE_MAP = {
    'en': 'English',
    'ukr': 'Ukrainian',
    'ru': 'Russian',
}

async def content_process(content: str) -> str:
    """
    Очищає необроблений текст постів від зайвих елементів (HTML, посилання, емодзі, стоп-слова),
    зберігаючи структуру з мітками [POST ID ...]
    """
    if not content:
        return ""

    # Видалення стоп-слів та «вводних» фраз (ігноруючи регістр)
    # \b означає «межа слова», щоб випадково не видалити частину іншого слова
    stop_words = [
        r'\bМысли богатых\b',
        r'\bбизнес блог\b',
        r'\bпривет\b',
        r'\bвсем привет\b',
        r'\bкак вы\b',
        r'\bHi everyone\b',
        r'\bHi\b',
        r'\bHello\b',
        r'\bWhats up\b',
        r'\bHow are you doing\b'
    ]
    stop_pattern = '|'.join(stop_words)
    clean_content = re.sub(stop_pattern, '', content, flags=re.IGNORECASE)

    # Видалення посилань (що починаються з http/https або www)
    clean_content = re.sub(r'https?://\S+|www\.\S+', '', clean_content)

    # Видалення HTML-тегів
    clean_content = re.sub(r'<[^>]+>', '', clean_content)

    # Видалення emojis
    clean_content = re.sub(r'[\U00010000-\U0010ffff]', '', clean_content)

    # Видаляємо символи по типу " , ", " ! ", " ? " на початку або після видалення слів
    clean_content = re.sub(r'\s+([.,!?])', r'\1', clean_content)

    # Замінюємо буль-які довгі пробіли, tab та enter на один пробіл
    clean_content = re.sub(r'\s+', ' ', clean_content)

    # Відновлення структури для ШІ
    clean_content = clean_content.replace('[POST ID', '\n[POST ID')

    return clean_content.strip()

async def make_digest(channel_title: str, raw_content: str, lang: str) -> dict:
    """Перетворює сирий контент постів у дайджест в форматі JSON"""
    # встановлюємо мову дайджесту, по дефолту англійська
    target_lang = f"\nIMPORTANT: The language of the digest MUST be {LANGUAGE_MAP.get(lang, 'English')}"

    # Оброблюємо сирий контент постів
    processed_content = await content_process(content=raw_content)

    user_prompt = f"Channel: {channel_title}. Posts content:{processed_content}"

    try:
        response = await client.chat.completions.create(
            # Обираємо модель
            model="google/gemini-2.0-flash-lite-001",
            # Відправляємо промпт для моделі й контент постів
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT + target_lang},
                {"role": "user", "content": user_prompt}
            ],
            # Повинні отримати у відповідь JSON об'єкт
            response_format={"type": "json_object"}
        )

        # Отримуємо текст від ШІ
        content = response.choices[0].message.content

        # Чистимо текст від Markdown (на випадок, якщо модель додала ```json)
        clean_content = re.sub(r'```json|```', "", content).strip()

        # Парсим в Python об'єкт
        result = json.loads(clean_content)

        # Якщо ШІ повернув список замість словника, беремо перший елемент
        if isinstance(result, list):
            result = result[0]

        return result

    except RateLimitError:
        print("Server is overload. Try again in 5 seconds.")
    except Exception as e:
        print(f"Error Brain: {e}")
        return {
            "events": None
        }