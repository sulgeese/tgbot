from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.filters.user import UserInGroup
from bot.keyboards import reply, inline
from .create_event import router as create_event_router
from .delete_event import router as delete_event_router
from .edit_event import router as edit_event_router
from .view_event import router as view_event_router

router = Router()

router.message.filter(F.chat.type == "private", UserInGroup())
router.chat_member.filter(F.chat.type == "private", UserInGroup())
router.callback_query.filter(F.message.chat.type == "private", UserInGroup())

router.include_router(create_event_router)
router.include_router(edit_event_router)
router.include_router(delete_event_router)
router.include_router(view_event_router)


@router.message(Command("start"))
async def start_command(message: Message) -> None:
    await message.answer(
        text="Здарова",
        reply_markup=reply.start,
    )


@router.message(F.text == "📆 События")
async def start_menu_new(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.delete()
    await message.answer(
        text='<b>Что хотите сделать?</b>',
        reply_markup=inline.event_interactions,
        parse_mode="HTML",
    )
