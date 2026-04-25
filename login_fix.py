from telethon import TelegramClient, errors
import asyncio
from config import config_p

api_id = config_p.api_id
api_hash = config_p.api_hash
phone = config_p.phone_number


async def main():
    # Створюємо клієнт з НОВОЮ назвою сесії, щоб уникнути конфліктів
    client = TelegramClient('pulse_worker_fix', api_id=api_id, api_hash=api_hash)

    await client.connect()

    if not await client.is_user_authorized():
        try:
            # Надсилаємо запит на код
            await client.send_code_request(phone)
            code = input('Enter a code from Telegram: ')

            try:
                # Намагаємось залогінитись
                await client.sign_in(phone, code)
            except errors.SessionPasswordNeededError:
                # Просимо ввести хмарний пароль (2FA)
                password = input('Enter your additional password (2FA): ')
                await client.sign_in(password=password)

            print("Success! The session has been created.")

        except errors.AuthRestartError:
            print("Restart error. Just wait 5–10 minutes and try again.")
        except Exception as e:
            print(f"An error occurred: {e}")
    else:
        print("You are already logged in!")

    client.disconnect()


if __name__ == '__main__':
    asyncio.run(main())