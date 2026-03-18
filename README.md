# 🤖 Pulse Bot

Pulse Bot is an advanced asynchronous Telegram bot designed to aggregate, filter, and summarize content from various Telegram channels using AI. It provides users with personalized, noise-free daily digests, saving time and keeping them updated on their favorite content creators and news sources.

## ✨ Key Features

* **🧠 AI-Powered Summaries (via brain.py)**: Acts as the central intelligence hub that orchestrates the flow between raw channel data and AI models. It handles prompt engineering to ensure high-quality, structured, and noise-free summaries
* **⚡ Smart Caching (Cache-Aside Pattern):** To optimize API costs and response times, the bot caches generated summaries. If multiple users request a digest for the same channel on the same day, the bot serves the cached version.
* **📂 Personalized Subscriptions:** Users manage their own list of favorite channels. The database utilizes a robust Many-to-Many architecture (`user_subscriptions` junction table).
* **🕰️ Digest History:** Users can access a history of previously generated summaries for their subscribed channels.
* **📊 Data Flow:** Scraper => Filter => Brain (AI) => DB & User

## 🛠️ Tech Stack

* **Language:** Python 3.12+
* **Telegram Framework:** [aiogram 3.25.0](https://docs.aiogram.dev/)
* **Database:** SQLite
* **ORM:** [SQLAlchemy 2.0.46](https://www.sqlalchemy.org/)
* **Migrations:** [Alembic 1.18.4](https://alembic.sqlalchemy.org/)

## 🏗️ Project Structure

```text
Pulse-Bot/
├── Database/               # Database logic and connection
│   └── models/             # SQLAlchemy models (User, Channel, Posts, Summary, Summary Posts, Subscriptions)
├── Handlers/               # Aiogram routers and event handlers
├── Keyboard/               # Inline and Reply keyboard definitions
├── Middleware/             # Dependency injection and session handling
├── migrations/             # Alembic migration scripts and history
│   └── versions/           # Individual migration files
├── Pictures/               # Static assets or bot images
├── Repositories/           # Data access layer (CRUD operations)
├── .gitignore              # Files to be ignored by Git
├── alembic.ini             # Alembic configuration
├── brain.py                # Core AI logic: text processing and LLM orchestration
├── config.py               # Application configuration and environment loading
├── requirements.txt        # List of project dependencies
├── scraper.py              # Telethon 
└── main.py                 # Application entry point