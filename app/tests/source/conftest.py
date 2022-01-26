import asyncio

import pytest_asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession

api_id = 'api_id'
api_hash = 'api_hash'
session_str = 'session'


@pytest_asyncio.fixture(scope="session")
async def client() -> TelegramClient:
    client = TelegramClient(
        StringSession(session_str), api_id, api_hash,
        sequential_updates=True
    )
    await client.connect()
    await client.get_me()
    await client.get_dialogs()

    yield client

    await client.disconnect()
    await client.disconnected


@pytest_asyncio.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()
