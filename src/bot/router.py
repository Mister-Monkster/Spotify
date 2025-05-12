from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, LinkPreviewOptions

from bot.service import TelegramService

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


@router.message(Command('help'))
async def help(message: Message, bot: Bot):
    await message.delete()
    img_url = "https://m.buro247.ru/images/senina/130080433.jpg"
    text = (f'<a href="{img_url}">&#8203;</a>\n'
            f'/start - Получить ссылку на авторизацию\n'
            f'/track - Бот отправит информацию о текущем треке\n'
            f'/top_tracks - Ваш топ-10 треков за месяц\n'
            f'/top_artists - Ваш топ-10 артистов за месяц\n'
            f'/playlists - Ваши плейлисты\n'
            f'/me - Проверка авторизации(если бот отправляет ващ профиль, значит вы авторизованы)\n'
            f'/logout - Выход из вашего аккаунта Spotify\n')
    await bot.send_message(message.chat.id,
                           text,
                           parse_mode='HTML',
                           link_preview_options=LinkPreviewOptions(show_above_text=True))
    return None


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
            await bot.send_message(message.from_user.id, 'Не удалость получить ваш профиль')
            return None
        await bot.send_message(message.from_user.id,
                               res,
                               parse_mode='HTML',
                               link_preview_options=LinkPreviewOptions(show_above_text=True))
        return None
    except:
        await bot.send_message(message.from_user.id,
                               'Произошла ошибка, проверьте статус авторизации\n /start')
        return None

@router.message(Command('logout'))
async def logout(message: Message, service: TelegramService, bot: Bot):
    try:
        await message.delete()
        res = await service.logout(message.from_user.id)
        if res:
            await bot.send_message(message.chat.id,'Вы успешно вышли из аккаунта Spotify.')
            return None
        await bot.send_message(message.chat.id,'Не удалось выйти из аккаунта Spotify.')
    except:
        await bot.send_message(message.chat.id, 'Произошла ошибка. Попробуйте позже.')










