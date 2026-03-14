import json
import re

from config import config_p
from openai import AsyncOpenAI, RateLimitError

client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=config_p.ai_api_key
)

SYSTEM_PROMPT = """
Ты — профессиональный медиа-аналитик. Твоя задача — анализировать посты блогеров и стримеров.
1. Игнорируй рекламные интеграции и спам.
2. Сжимай суть всех постов канала в 1-2 лаконичных предложения.
3. Используй уместные эмодзи для живости.
4. Выдавай ответ СТРОГО в формате JSON. Не добавляй никаких пояснений до или после JSON.

Формат ответа:
{
"topic": "Краткий заголовок темы",
"result": "Текст выжимки в 1-2 предложениях "
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