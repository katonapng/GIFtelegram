import logging

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

# Объект бота
bot = Bot('bot token')

# bot_token = getenv("BOT_TOKEN",  parse_mode=types.ParseMode.HTML)
# if not bot_token:
#     exit("Error: no token provided")
# Диспетчер для бота
dp = Dispatcher(bot, storage=MemoryStorage())
# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)


class Form(StatesGroup):
    picture = State()
    quote = State()


@dp.message_handler(commands="quote")
async def cmd_quote(message: types.Message, state: FSMContext):
    await Form.quote.set()
    nice_word = message.get_args()
    if nice_word == 'please':
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


@dp.message_handler(state=Form.picture, content_types=['photo'])
async def process_picture(message: types.Message, state: FSMContext):
    await message.reply_photo(message.photo[0].file_id)

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Good Picture", "Nope, misclick"]
    keyboard.add(*buttons)

    await message.answer("You sure this is the one?", reply_markup=keyboard)
    await state.finish()


@dp.message_handler(Text(equals="Good Picture"))
async def good_picture_button(message: types.Message):
    await message.answer("We all set, here you go.",
                         reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(Text(equals="Nope, misclick"))
async def nope_misclick_button(message: types.Message):
    await message.answer("Oh, well, mistakes happen.\nTry again.",
                         reply_markup=types.ReplyKeyboardRemove())
    await Form.picture.set()


@dp.message_handler(state=Form.quote)
async def process_text(message: types.Message, state: FSMContext):
    await message.reply(message.text)

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Nice quote", "Wrong quote"]
    keyboard.add(*buttons)
    await message.answer("Will it go well with the"
                         " picture you gave me?",
                         reply_markup=keyboard)
    await state.finish()


@dp.message_handler(Text(equals="Nice quote"))
async def nice_quote_button(message: types.Message):
    await message.answer("Well, hope you chose wisely.\n"
                         "Give me the picture now.",
                         reply_markup=types.ReplyKeyboardRemove())
    await Form.picture.set()


@dp.message_handler(Text(equals="Wrong quote"))
async def wrong_quote_button(message: types.Message):
    await message.answer("Agh, make up your mind kid!\n"
                         "Give me the right one!",
                         reply_markup=types.ReplyKeyboardRemove())
    await Form.quote.set()


@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.finish()
    await message.answer('Gotcha.')


@dp.message_handler(commands="help")
async def cmd_help(message: types.Message):
    await message.answer("Here you go, all the request you can ask of me\n"
                         "If I'm in the mood, i shall answer you:\n"
                         "/start - start interactions\n"
                         "/help - get all available requests\n"
                         "/quote - create a picture out of given"
                         " picture and text"
                         "")


@dp.message_handler(commands="start")
async def cmd_start(message: types.Message):
    await message.answer("Welcome To The 75th Annual Hunger Games!\n"
                         "Uh... I mean, wrong text, who gave me this?\n"
                         "Welcome to the QuoteCreator, of course!\n"
                         "Let me dig up some useful information... "
                         "Just a sec")
    await cmd_help(message)


@dp.message_handler()
async def echo_message(msg: types.Message):
    await bot.send_message(msg.from_user.id, msg.text)


@dp.message_handler(content_types=[types.ContentType.ANIMATION])
async def echo_document(message: types.Message):
    await message.reply_animation(message.animation.file_id)


if __name__ == "__main__":
    # Запуск бота
    executor.start_polling(dp, skip_updates=True)
