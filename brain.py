import json
import re

from config import config_p
from openai import AsyncOpenAI, RateLimitError

client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=config_p.ai_api_key
)

SYSTEM_PROMPT = """
Ты — профессиональный контент-аналитик Pulse Bot. Твоя задача — проанализировать массив текста из Telegram-канала и составить краткий, живой дайджест.

ВАЖНО: массив текста, разделен метками [POST ID {тут ID}]

ПРАВИЛА ОБРАБОТКИ:
1. КЛАССИФИКАЦИЯ: Если несколько постов описывают одно событие (например, анонс стрима и последующий перенос времени), объедини их в одну сущность. Если посты о разном — создай разные блоки.
2. ФИЛЬТРАЦИЯ: Полностью игнорируй рекламу (казино, ставки, промокоды, внешние ссылки на товары), спам и бессмысленные сообщения (просто стикеры или приветствия без контекста).
3. СЖАТИЕ: Описывай суть события максимально лаконично(2-7 предложений).
4. СТИЛЬ: Используй подходящие эмодзи для живости, но не переспамь ими.

ФОРМАТ ОТВЕТА:
Ты должен отвечать СТРОГО в формате JSON. Никакого лишнего текста до или после JSON.
Структура JSON:
{
  "summary_date": "MM-DD-YYYY",
  "events": [
    {
      "topic": "Заголовок события с эмодзи",
      "result": "Краткое описание сути 2-7 предложений",
      "list": "Список POST ID которие вошли в событие"
    }
  ]
}
"""

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

async def make_digest(channel_title: str, raw_content: str) -> dict:
    """Перетворює сирий контент постів у дайджест в форматі JSON"""

    # Оброблюємо сирий контент постів
    processed_content = await content_process(content=raw_content)

    user_prompt = f"Channel: {channel_title}. Posts content:{processed_content}"

    try:
        response = await client.chat.completions.create(
            # Обираємо модель
            model="google/gemini-2.0-flash-lite-001",
            # Відправляємо промпт для моделі й контент постів
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
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