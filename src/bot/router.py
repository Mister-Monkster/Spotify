from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, LinkPreviewOptions

from service import TelegramService

router = Router()

@router.message(Command('start'))
async def start(message: Message, service: TelegramService, bot: Bot):
    try:
        await message.delete()
        url = await service.start(message.from_user.id)
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Сcылка на авторизацию', url=url)]
        ])

        await bot.send_message(message.chat.id, 'Для начала работы бота Вам необходимо авторизоваться в Spotify,'
                             ' чтобы я мог получать треки, '
                             'которые Вы слушаете', reply_markup=kb)
        return None
    except:
        await bot.send_message(message.chat.id, 'Вы уже авторизованы.')


@router.message(Command('track'))
async def current_track(message: Message, service: TelegramService, bot: Bot):
    try:
        await message.delete()
        res = await service.track(message.from_user.id)
        if res == 404:
            await bot.send_message(message.chat.id,
                                   'В данный момент вы ничего не слушаете.')
            return None
        await bot.send_message(message.chat.id,
                               res,
                               parse_mode='HTML',
                               link_preview_options=LinkPreviewOptions(show_above_text=True))
        return None
    except:
        await bot.send_message(message.chat.id,
                               'Ошибка. Возможно вы не авторизованы.\n<code>/start</code>',
                               parse_mode='HTML')


@router.message(Command('top_tracks'))
async def top_tracks(message: Message, service: TelegramService, bot: Bot):
    try:
        await message.delete()
        res = await service.top_tracks(message.from_user.id)
        if res == 404:
            await bot.send_message(message.chat.id,
                                   'Топ за этот месяц недоступен. Попробуйте позже.')
            return None
        await bot.send_message(message.chat.id,
                               res,
                               parse_mode='HTML',
                               link_preview_options=LinkPreviewOptions(show_above_text=True))
        return None
    except:
        await bot.send_message(message.chat.id,
                               'Произошла ошибка, проверьте статус авторизации\n '
                               '<code>/start</code>\n'
                               '<code>/me</code>',
                               parse_mode='HTML')
        return None



@router.message(Command('top_artists'))
async def top_artists(message: Message, service: TelegramService, bot: Bot):
    try:
        await message.delete()
        res = await service.top_artists(message.from_user.id)
        if res == 404:
            await bot.send_message(message.chat.id,
                                   'Топ за этот месяц недоступен. Попробуйте позже.')
            return None
        await message.answer(res,
            parse_mode='HTML',
            link_preview_options=LinkPreviewOptions(show_above_text=True))
        return None


    except:
        await bot.send_message(message.chat.id,
                               'Произошла ошибка, проверьте статус авторизации\n'
                               '<code>/start</code>\n'
                               '<code>/me</code>',
                               parse_mode='HTML')
        return None



@router.message(Command('playlists'))
async def albums(message: Message, service: TelegramService, bot: Bot):
    try:
        await message.delete()
        res = await service.playlists(message.from_user.id)
        if res == 404:
            await bot.send_message(message.chat.id, 'У вас нет плейлистов.')
            return None

        await bot.send_message(message.chat.id,
                               res,
                               parse_mode='HTML',
                               link_preview_options=LinkPreviewOptions(show_above_text=True)
                               )
        return None

    except:
        await bot.send_message(message.chat.id, 'Ошибка получения ваших плейлистов. Возможно вы не авторизованы\n'
                                                '<code>/start</code>')
        return None




@router.message(Command('me'))
async def profile(message: Message, service: TelegramService, bot: Bot):
    try:
        await message.delete()
        res = await service.me(message.from_user.id)
        if res == 404:
            await bot.send_message(message.chat.id, 'Не удалость получить ваш профиль')
            return None
        await bot.send_message(message.chat.id,
                               res,
                               parse_mode='HTML',
                               link_preview_options=LinkPreviewOptions(show_above_text=True))
        return None
    except:
        await message.reply('Произошла ошибка, проверьте статус авторизации\n /start')
        return None










