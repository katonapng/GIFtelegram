import logging
import os

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from applytext import create_image
from createGIF import create_GIF
from disk import get_all_users_GIFs, get_user_GIFs, upload_to_yadisk
from yadisk.exceptions import ParentNotFoundError

token = 'token'
bot = Bot(token)

dp = Dispatcher(bot, storage=MemoryStorage())
logging.basicConfig(level=logging.INFO)


class QuoteForm(StatesGroup):
    picture = State()
    quote = State()
    picture_button = State()
    quote_button = State()


class GifForm(StatesGroup):
    Gif = State()
    privacy_button = State()


class GetGifForm(StatesGroup):
    get_gif = State()


@dp.message_handler(commands="getgif")
async def cmd_getgif(message: types.Message):
    """Function to handle /getgif command.

    User keyboard is replaced with two buttons to
    choose what command should be executed next.
    Depending on the answer either user_gifs_button
    or all_users_gifs_button will be executed.

    Args:
        message (types.Message): message sent by the user.

    """
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Give me my gifs", "Give me all users gifs"]
    keyboard.add(*buttons)
    await message.answer("Do you want to get only your gifs \n"
                         "or you want to violate someones "
                         "privacy?\n",
                         reply_markup=keyboard)
    await GetGifForm.get_gif.set()


@dp.message_handler(Text(equals="Give me my gifs"), state=GetGifForm.get_gif)
async def user_gifs_button(message: types.Message, state: FSMContext):
    """Function called when 'Give me my gifs' button is pressed.

    All gifs created by specific user are extracted from
    storage and sent back to the user.

    Args:
        message (types.Message): message sent by the user.
        state (state: FSMContext): state of finite state machine.

    """
    gifs_path = get_user_GIFs(message.from_user.id)
    if gifs_path:
        await message.answer("No problem, here you go.",
                             reply_markup=types.ReplyKeyboardRemove())
    else:
        await message.answer("I don't think i have your "
                             "gifs in archive.\n"
                             "Create some first.",
                             reply_markup=types.ReplyKeyboardRemove())

    for path in gifs_path:
        await bot.send_document(message.chat.id, path)

    await state.finish()


@dp.message_handler(Text(equals="Give me all users gifs"),
                    state=GetGifForm.get_gif)
async def all_users_gifs_button(message: types.Message, state: FSMContext):
    """Function called when 'Give me all users gifs' button is pressed.

    All gifs created by all users are extracted from
    storage and sent back to the user.

    Args:
        message (types.Message): message sent by the user.
        state (state: FSMContext): state of finite state machine.

    """
    await message.answer("That's not nice, you know?\n"
                         "But what can I do about it, "
                         "I'm just a pawn...",
                         reply_markup=types.ReplyKeyboardRemove())
    # send users gifs
    gifs_path = get_all_users_GIFs()
    for path in gifs_path:
        await bot.send_document(message.chat.id, path)
    await state.finish()


@dp.message_handler(commands="gif")
async def cmd_gif(message: types.Message):
    """Function to handle /gif command.

    User keyboard is replaced with one button to
    signal that user have sent all desired media.

    Args:
        message (types.Message): message sent by the user.

    """
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["That's all"]
    keyboard.add(*buttons)
    await message.answer("My favorite thing to do.\n"
                         "Send me some pictures and "
                         "I'll create a gif for you.\n"
                         "Keep in mind, that all images "
                         "will be resized to fit first "
                         "image you send!\n"
                         "There is a button 'That's all' "
                         "where your keyboard is. "
                         "Press it when you're done.",
                         reply_markup=keyboard)
    await GifForm.Gif.set()


@dp.message_handler(state=GifForm.Gif, content_types=['photo', 'document'])
async def process_media_group(message: types.Message, state: FSMContext):
    """Function to collect all photos sent by user.

    All photos sent by the user are handled and stored one by one
    (because of the Telegram Bot API nature).

    Args:
        message (types.Message): message sent by the user.
        state (state: FSMContext): state of finite state machine.

    """
    if message.content_type == 'photo':
        file_id = message.photo[-1].file_id
        await message.photo[-1].download(destination_file='./photos/'
                                         f'{file_id}.jpg')
    elif message.content_type == 'document':
        file_id = message.document.file_id
        await message.document.download(destination_file='./photos/'
                                        f'{file_id}.jpg')
    async with state.proxy() as data:
        try:
            data['file_ids'].append(file_id)
        except KeyError:
            data['file_ids'] = [file_id]


@dp.message_handler(Text(equals="That's all"), state=GifForm.Gif)
async def thats_all_button(message: types.Message, state: FSMContext):
    """Function called when 'That's all' button is pressed.

    All stored photos are converted into one gif and
    sent back to the user.

    Args:
        message (types.Message): message sent by the user.
        state (state: FSMContext): state of finite state machine.

    """
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Yeah, protect it", "Nah, it's for fun"]
    keyboard.add(*buttons)
    await message.answer("Do you want this gif to be private?",
                         reply_markup=keyboard)

    await GifForm.privacy_button.set()


async def upload(message: types.Message, state: FSMContext, _type: str):
    async with state.proxy() as data:
        try:
            path_to_gif = create_GIF(data['file_ids'][0], data['file_ids'])
            if _type == 'gif_private':
                await message.answer("Nice album we have here.\n"
                                     "Let me create a private GIF "
                                     "just for you.",
                                     reply_markup=types.ReplyKeyboardRemove())
            else:
                await message.answer("Nice album we have here.\n"
                                     "Let me create a GIF for you.",
                                     reply_markup=types.ReplyKeyboardRemove())

            with open(f'{path_to_gif}', 'rb') as doc:
                await bot.send_document(chat_id=message.chat.id,
                                        document=doc)

            upload_to_yadisk(message.from_user.id, path_to_gif, f'{_type}')
            await state.finish()

        except KeyError:
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            buttons = ["That's all"]
            keyboard.add(*buttons)
            await message.answer("Stop joking around and "
                                 "give me some pictures so "
                                 "I could finish my work.",
                                 reply_markup=keyboard)
        except FileNotFoundError:
            await message.answer('Something went wrong with files.\n'
                                 'Try again.')
            await state.finish()


@dp.message_handler(Text(equals="Yeah, protect it"),
                    state=GifForm.privacy_button)
async def yeah_protect_it_button(message: types.Message, state: FSMContext):
    """Function called when 'Yeah, protect it' button is pressed.

    Created gif will be uploaded to private album.
    Gifs in private album can't be seen other users.

    Args:
        message (types.Message): message sent by the user.
        state (state: FSMContext): state of finite state machine.

    """
    await message.answer("Please wait a second.",
                         reply_markup=types.ReplyKeyboardRemove())
    await upload(message, state, 'gif_private')


@dp.message_handler(Text(equals="Nah, it's for fun"),
                    state=GifForm.privacy_button)
async def nah_fun_button(message: types.Message, state: FSMContext):
    """Function called when 'Nah, it's for fun' button is pressed.

    Created gif will be uploaded to public album.
    Gifs in public album can be seen by other users.

    Args:
        message (types.Message): message sent by the user.
        state (state: FSMContext): state of finite state machine.

    """
    await message.answer("Please wait a second.",
                         reply_markup=types.ReplyKeyboardRemove())
    await upload(message, state, 'gif')


@dp.message_handler(commands="quote")
async def cmd_quote(message: types.Message):
    """Function to handle /quote command.

    Message with a request for the quote is
    sent to user.

    Args:
        message (types.Message): message sent by the user.

    """
    await QuoteForm.quote.set()
    words = message.get_args()
    if 'please' in words:
        await message.answer("Oh, well mannered kid, how refreshing.\n"
                             "I would gladly help you create a picture.\n"
                             "Give me the quote for the picture first, "
                             "please.")
    else:
        await message.answer("OK, i can create a picture for you.\n"
                             "It would not hurt you to say please sometimes,"
                             " you know!\n"
                             "Give me the quote for the picture first,"
                             " please.")


@dp.message_handler(state=QuoteForm.quote, content_types=['text'])
async def process_text(message: types.Message, state: FSMContext):
    """Function to process quote sent by user.

    Recieved quote is stored.
    User keyboard is replaced with two buttons to
    choose what command should be executed next.
    Depending on the answer either nice_quote_button
    or wrong_quote_button will be executed.

    Args:
        message (types.Message): message sent by the user.
        state (state: FSMContext): state of finite state machine.

    """
    async with state.proxy() as data:
        data['quote'] = message.text
    await message.reply(message.text)

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Nice quote", "Wrong quote"]
    keyboard.add(*buttons)
    await message.answer("Will it go well with the"
                         " picture?",
                         reply_markup=keyboard)
    await QuoteForm.quote_button.set()


@dp.message_handler(Text(equals="Nice quote"), state=QuoteForm.quote_button)
async def nice_quote_button(message: types.Message):
    """Function called when 'Nice quote' button is pressed.

    Message with confirmation is sent and state to
    process picture is set.

    Args:
        message (types.Message): message sent by the user.

    """
    await message.answer("Well, hope you chose wisely.\n"
                         "Give me the picture now.",
                         reply_markup=types.ReplyKeyboardRemove())
    await QuoteForm.picture.set()


@dp.message_handler(Text(equals="Wrong quote"),
                    state=QuoteForm.quote_button)
async def wrong_quote_button(message: types.Message):
    """Function called when 'Wrong quote' button is pressed.

    Message to give another quote is sent and state to
    process quote is set once again.

    Args:
        message (types.Message): message sent by the user.

    """
    await message.answer("Agh, make up your mind kid!\n"
                         "Give me the right one!",
                         reply_markup=types.ReplyKeyboardRemove())
    await QuoteForm.quote.set()


@dp.message_handler(state=QuoteForm.picture,
                    content_types=['photo', 'document'])
async def process_picture(message: types.Message, state: FSMContext):
    """Function to process picture sent by user.

    Recieved picture is stored.
    User keyboard is replaced with two buttons to
    choose what command should be executed next.
    Depending on the answer either good_picture_button
    or nope_misclick_button will be executed.

    Args:
        message (types.Message): message sent by the user.
        state (state: FSMContext): state of finite state machine.

    """
    if message.content_type == 'photo':
        file_id = message.photo[-1].file_id
        async with state.proxy() as data:
            data['picture'] = file_id

        await message.photo[-1].download(destination_file='./photos/'
                                         f'{file_id}.jpg')
        await message.reply_photo(file_id)
    elif message.content_type == 'document':
        file_id = message.document.file_id
        async with state.proxy() as data:
            data['picture'] = file_id

        await message.document.download(destination_file='./photos/'
                                        f'{file_id}.jpg')
        await message.reply_document(file_id)

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Good Picture", "Nope, misclick"]
    keyboard.add(*buttons)

    await message.answer("You sure this is the one?", reply_markup=keyboard)
    await QuoteForm.picture_button.set()


@dp.message_handler(Text(equals="Good Picture"),
                    state=QuoteForm.picture_button)
async def good_picture_button(message: types.Message, state: FSMContext):
    """Function called when 'Good picture' button is pressed.

    Creates picture out of stored data, sends picture
    back to the user and stores picture in cloud storage.

    Args:
        message (types.Message): message sent by the user.
        state (state: FSMContext): state of finite state machine.

    """
    await message.answer("We all set, here you go.",
                         reply_markup=types.ReplyKeyboardRemove())

    try:
        async with state.proxy() as data:
            path_to_modified_image = create_image(data['quote'],
                                                  data['picture'])

        with open(f'{path_to_modified_image}', 'rb') as _photo:
            await bot.send_photo(chat_id=message.chat.id,
                                 photo=_photo)
        upload_to_yadisk(message.from_user.id, path_to_modified_image,
                         'jpeg')
        await state.finish()
    except (FileNotFoundError, ParentNotFoundError):
        await message.answer('Something went wrong with files.\n'
                             'Try again.')
        await state.finish()


@dp.message_handler(Text(equals="Nope, misclick"),
                    state=QuoteForm.picture_button)
async def nope_misclick_button(message: types.Message, state=FSMContext):
    """Function called when 'Nope, misclick' button is pressed.

    Message to give another picture is sent and state to
    process picture is set once again.

    Args:
        message (types.Message): message sent by the user.
        state (state: FSMContext): state of finite state machine.

    """
    await message.answer("Oh, well, mistakes happen.\nTry again.",
                         reply_markup=types.ReplyKeyboardRemove())
    async with state.proxy() as data:
        os.remove(f"./photos/{data['picture']}.jpg")
    await QuoteForm.picture.set()


@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    """Function to hadle /cancel command.

    Finish state of any running command,
    except typing quote, so /cancel can be
    displayed on the picture.

    Args:
        message (types.Message): message sent by the user.
        state (state: FSMContext): state of finite state machine.

    """
    current_state = await state.get_state()
    if current_state is None:
        return

    async with state.proxy() as data:
        try:
            for file_id in data['file_ids']:
                if os.path.isfile(f'./photos/{file_id}.jpg'):
                    os.remove(f'./photos/{file_id}.jpg')
            print('deleted')
        except KeyError:
            print('index error')
            pass
        try:
            if os.path.isfile(f'./photos/{data["picture"]}.jpg'):
                os.remove(f'./photos/{data["picture"]}.jpg')
            print('deleted')
        except KeyError:
            print('index error')
            pass

    await state.finish()
    await message.answer('Gotcha.', reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(commands="help")
async def cmd_help(message: types.Message):
    """Function to handle /help command.

    Message with all available commands is sent
    to the user.

    Args:
        message (types.Message): message sent by the user.

    """
    await message.answer("Here you go, all the requests you can ask of me\n"
                         "If I'm in the mood, i shall answer you:\n"
                         "/start - begin interaction\n"
                         "/help - get all available requests\n"
                         "/quote - create a picture out of given"
                         " image and text"
                         "/gif - create a gif out of given photo "
                         "or album of photos.\n"
                         "/getgif - get created gifs"
                         "/cancel - cancel any operation "
                         "except quote typing")


@dp.message_handler(commands="start")
async def cmd_start(message: types.Message):
    """Function to handle /start command.

    Greatings message and all available commands are sent
    to the user.

    Args:
        message (types.Message): message sent by the user.

    """
    await message.answer("Welcome To The 75th Annual Hunger Games!\n"
                         "Uh... I mean, wrong text, who gave me this?\n"
                         "Welcome to the QuoteCreator, of course!\n"
                         "Let me dig up some useful information... "
                         "Just a sec")
    await cmd_help(message)


@dp.message_handler(content_types=['text'])
async def echo_message(message: types.Message):
    """Function to handle random text messages.

    Echo message is sent back to user.

    Args:
        message (types.Message): message sent by the user.

    """
    await bot.send_message(message.from_user.id, message.text)


@dp.message_handler(content_types=[types.ContentType.ANIMATION])
async def echo_animation(message: types.Message):
    """Function to handle random media messages.

    Echo message is sent back to user.

    Args:
        message (types.Message): message sent by the user.

    """
    await message.reply_animation(message.animation.file_id)


@dp.message_handler(state='*', content_types=['photo', 'text', 'document'])
async def echo_in_state(message: types.Message):
    """Function to handle random media messages.

    Echo message is sent back to user.

    Args:
        message (types.Message): message sent by the user.

    """
    await message.answer('Wrong move, read the message above '
                         'if your are in command or type any '
                         'command to start it. Maybe try /cancel.')


if __name__ == "__main__":
    # Запуск бота
    executor.start_polling(dp, skip_updates=True)
