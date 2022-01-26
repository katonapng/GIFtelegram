from async_timeout import asyncio
from pytest import mark
from telethon import TelegramClient
from telethon.tl.custom.message import Message

api_id = 'api_id'
api_hash = 'api_hash'


@mark.asyncio
async def test_start(client: TelegramClient):
    """Test response to start command.

    Two responses are expected: greatings message and message
    displayed when help command is called.

    """
    async with client.conversation("@QuoteCreatorBot", timeout=5) as conv:
        await conv.send_message("/start")

        resp: Message = await conv.get_response()
        assert 'Welcome To The 75th Annual Hunger Games!' in resp.raw_text
        resp: Message = await conv.get_response()
        assert 'Here you go, all the requests' in resp.raw_text


@mark.asyncio
async def test_help(client: TelegramClient):
    """Test response to help command."""
    async with client.conversation("@QuoteCreatorBot", timeout=5) as conv:
        await conv.send_message("/help")

        resp: Message = await conv.get_response()
        assert 'Here you go, all the requests' in resp.raw_text


@mark.asyncio
async def test_user_sent_quote(client: TelegramClient):
    """Test response to quote sent by user
    while executing quote command."""
    async with client.conversation("@QuoteCreatorBot", timeout=5) as conv:
        await conv.send_message("/quote")

        resp: Message = await conv.get_response()
        assert 'OK, i can create a picture for you.' in resp.raw_text

        await conv.send_message('some quote')
        resp: Message = await conv.get_response()
        assert 'some quote' in resp.raw_text
        resp: Message = await conv.get_response()
        assert 'Will it go well with the picture?' in resp.raw_text


@mark.asyncio
async def test_wrong_quote_button(client: TelegramClient):
    """Test response to pressing 'Wrong quote' button in quote command."""
    async with client.conversation("@QuoteCreatorBot", timeout=5) as conv:
        await conv.send_message('Wrong quote')
        resp: Message = await conv.get_response()
        assert 'Agh, make up your mind kid!' in resp.raw_text


@mark.asyncio
async def test_nice_quote_button(client: TelegramClient):
    """Test response to pressing 'Nice quote' button in quote command."""
    async with client.conversation("@QuoteCreatorBot", timeout=5) as conv:
        await conv.send_message('some good quote')
        resp: Message = await conv.get_response()
        assert 'some good quote' in resp.raw_text
        resp: Message = await conv.get_response()
        assert 'Will it go well with the picture?' in resp.raw_text

        await conv.send_message('Nice quote')
        resp: Message = await conv.get_response()
        assert 'Well, hope you chose wisely.' in resp.raw_text


@mark.asyncio
async def test_user_sent_picture(client: TelegramClient):
    """Test response to sending picture in quote command."""
    async with client.conversation("@QuoteCreatorBot", timeout=5) as conv:
        await conv.send_file('./app/photos/arcane.jpg')
        resp: Message = await conv.get_response()
        resp: Message = await conv.get_response()
        assert 'You sure this is the one?' in resp.raw_text


@mark.asyncio
async def test_nope_misclick_button(client: TelegramClient):
    """Test response to pressing 'Nope, misclick' button in quote command."""
    async with client.conversation("@QuoteCreatorBot", timeout=5) as conv:
        await conv.send_message('Nope, misclick')
        resp: Message = await conv.get_response()
        assert 'Oh, well, mistakes happen.' in resp.raw_text


@mark.asyncio
async def test_good_picture_button(client: TelegramClient):
    """Test response to pressing 'Good Picture' button in quote command."""
    async with client.conversation("@QuoteCreatorBot", timeout=5) as conv:
        await conv.send_file('./app/photos/arcane.jpg')
        resp: Message = await conv.get_response()
        resp: Message = await conv.get_response()
        assert 'You sure this is the one?' in resp.raw_text
        await conv.send_message('Good Picture')
        resp: Message = await conv.get_response()
        assert 'We all set, here you go.' in resp.raw_text
        resp: Message = await conv.get_response()


@mark.asyncio
async def test_gif(client: TelegramClient):
    """Test response to gif command."""
    async with client.conversation("@QuoteCreatorBot", timeout=5) as conv:
        await conv.send_message("/gif")

        resp: Message = await conv.get_response()
        assert 'My favorite thing to do.' in resp.raw_text

        await conv.send_message('/cancel')
        resp: Message = await conv.get_response()


@mark.asyncio
async def test_gif_button(client: TelegramClient):
    """Test response to pressing 'That's all' button in gif command."""
    async with client.conversation("@QuoteCreatorBot", timeout=10) as conv:
        await conv.send_message("/gif")

        resp: Message = await conv.get_response()
        assert 'My favorite thing to do.' in resp.raw_text

        await conv.send_message("That's all")
        resp: Message = await conv.get_response()
        assert 'Do you want this gif to be private?' in resp.raw_text

        await conv.send_message("/cancel")
        resp: Message = await conv.get_response()


@mark.asyncio
async def test_gif_private_button(client: TelegramClient):
    """Test response to pressing 'Yeah, protect it' in gif command."""
    async with client.conversation("@QuoteCreatorBot", timeout=10) as conv:
        await conv.send_message("/gif")

        resp: Message = await conv.get_response()
        assert 'My favorite thing to do.' in resp.raw_text

        await conv.send_file('./app/photos/arcane.jpg')
        await conv.send_file('./app/photos/jinx x ekko.jpg')
        await asyncio.sleep(1)
        await conv.send_message("That's all")

        resp: Message = await conv.get_response()
        assert 'Do you want this gif to be private?' in resp.raw_text

        await conv.send_message("Yeah, protect it")
        resp: Message = await conv.get_response()
        assert 'Please wait a second.' in resp.raw_text
        resp: Message = await conv.get_response()
        assert 'Let me create a private GIF' in resp.raw_text
        await asyncio.sleep(5)


@mark.asyncio
async def test_gif_public_button(client: TelegramClient):
    """Test response to pressing 'Nah, it's for fun' in gif command."""
    async with client.conversation("@QuoteCreatorBot", timeout=10) as conv:
        await conv.send_message("/gif")

        resp: Message = await conv.get_response()
        assert 'My favorite thing to do.' in resp.raw_text

        await conv.send_file('./app/photos/arcane.jpg')
        await conv.send_file('./app/photos/jinx x ekko.jpg')
        await asyncio.sleep(1)
        await conv.send_message("That's all")

        resp: Message = await conv.get_response()
        assert 'Do you want this gif to be private?' in resp.raw_text

        await conv.send_message("Nah, it's for fun")
        resp: Message = await conv.get_response()
        assert 'Please wait a second.' in resp.raw_text
        resp: Message = await conv.get_response()
        assert 'Let me create a GIF' in resp.raw_text
        await asyncio.sleep(5)


@mark.asyncio
async def test_getgif(client: TelegramClient):
    """Test response to getgif command."""
    async with client.conversation("@QuoteCreatorBot", timeout=5) as conv:
        await conv.send_message("/getgif")

        resp: Message = await conv.get_response()
        assert 'Do you want to get only your gifs' in resp.raw_text

        await conv.send_message('/cancel')
        resp: Message = await conv.get_response()


@mark.asyncio
async def test_getgif_user_button(client: TelegramClient):
    """Test response to 'Give me my gifs' button in getgif command."""
    async with client.conversation("@QuoteCreatorBot") as conv:
        await conv.send_message("/getgif")

        resp: Message = await conv.get_response()
        assert 'Do you want to get only your gifs' in resp.raw_text

        await conv.send_message('Give me my gifs')
        resp: Message = await conv.get_response()
        assert 'No problem, here you go.' in resp.raw_text

        try:
            while await conv.get_response():
                pass
        except asyncio.exceptions.TimeoutError:
            # there is no option to ignore timeout
            pass


@mark.asyncio
async def test_getgif_all_users_button(client: TelegramClient):
    """Test response to 'Give me all users gifs' button in getgif command."""
    async with client.conversation("@QuoteCreatorBot") as conv:
        await conv.send_message("/getgif")

        resp: Message = await conv.get_response()
        assert 'Do you want to get only your gifs' in resp.raw_text

        await conv.send_message('Give me all users gifs')
        resp: Message = await conv.get_response()
        assert "That's not nice, you know?" in resp.raw_text

        try:
            while await conv.get_response():
                pass
        except asyncio.exceptions.TimeoutError:
            # there is no option to ignore timeout
            pass
