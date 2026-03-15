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

ВАЖНО: массив текста, разделен метками [POST ID]

ПРАВИЛА ОБРАБОТКИ:
1. КЛАССИФИКАЦИЯ: Если несколько постов описывают одно событие (например, анонс стрима и последующий перенос времени), объедини их в одну сущность. Если посты о разном — создай разные блоки.
2. ФИЛЬТРАЦИЯ: Полностью игнорируй рекламу (казино, ставки, промокоды, внешние ссылки на товары), спам и бессмысленные сообщения (просто стикеры или приветствия без контекста).
3. СЖАТИЕ: Описывай суть события максимально лаконично (1-3 предложения).
4. СТИЛЬ: Используй подходящие эмодзи для живости, но не переспамь ими.

ФОРМАТ ОТВЕТА:
Ты должен отвечать СТРОГО в формате JSON. Никакого лишнего текста до или после JSON.
Структура JSON:
{
  "summary_date": "MM-DD-YYYY",
  "events": [
    {
      "topic": "Заголовок события с эмодзи",
      "result": "Краткое описание сути 1-3 предложения",
      "ids": "Список POST ID которие вошли в событие"
    }
  ]
}
"""


async def make_digest(channel_title: str, post_content: str):
    user_prompt = f"Channel: {channel_title}\nPost's text:\n{post_content}"

    try:
        response = await client.chat.completions.create(
            model="google/gemini-2.0-flash-lite-001",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"}
        )

        # 1. Получаем сырой текст
        content = response.choices[0].message.content

        # 2. Чистим текст от Markdown (на случай, если модель добавила ```json)
        clean_content = re.sub(r'```json|```', "", content).strip()

        # 3. Парсим в Python объект
        result = json.loads(clean_content)

        # 4. Если ИИ вернул список вместо словаря, берем первый элемент
        if isinstance(result, list):
            result = result[0]

        return result

    except RateLimitError:
        print("Server is overload. Try again in 5 seconds.")
    except Exception as e:
        print(f"Error Brain: {e}")
        return {
            "title": channel_title,
            "topic": "Error",
            "result": f"{e}"
        }