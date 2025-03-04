import logging

from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ChatMemberUpdated
from redis.asyncio import Redis
from sqlmodel.ext.asyncio.session import AsyncSession

from bot.keyboards import inline
from bot.states import StepsForm
from db.repositories import UserRepository, EventRepository
from db.models import UsersModel
from settings import settings


logger = logging.getLogger(__name__)


async def send_message(bot: Bot, title: str, text: str, mentions: str) -> None:
    await bot.send_message(
        chat_id=settings.bots.supergroup_id,
        text=f"<i><b>{title}</b></i>\n\n{text}\n\n{mentions}",
        message_thread_id=settings.bots.theme_id,
        parse_mode="HTML",
    )


async def send_events_list(call: CallbackQuery, session: AsyncSession, redis: Redis) -> None:
    data = await EventRepository(session, redis).get_events_by_user(user_id=int(call.from_user.id))
    await call.message.edit_text(  # type: ignore
        text="<b>Уведомления</b>",
        parse_mode="HTML",
        reply_markup=inline.get_events_keyboard(data)
    )


async def send_edit_event_message(message: Message, state: FSMContext) -> None:
    await message.answer(
        text="<b>Что изменить?</b>",
        parse_mode="HTML",
        reply_markup=inline.edit_events,
    )
    await state.set_state(StepsForm.EDIT_EVENTS)


async def send_start_menu(call: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await call.message.edit_text(  # type: ignore
        text='<b>Что хотите сделать?</b>',
        reply_markup=inline.event_interactions,
        parse_mode="HTML"
    )


async def update_user(event: ChatMemberUpdated, session: AsyncSession, redis: Redis, in_group: bool) -> None:
    user_repository = UserRepository(session, redis)
    user = UsersModel(
        id=event.new_chat_member.user.id,
        username=event.new_chat_member.user.username,
        first_name=event.new_chat_member.user.first_name,
        last_name=event.new_chat_member.user.last_name,
        in_group=in_group,
    )
    if await user_repository.get(event.new_chat_member.user.id):
        await user_repository.update(user)
    else:
        await user_repository.create(user)
