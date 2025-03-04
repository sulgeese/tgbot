from aiogram import Router
from aiogram.types import Update

universal_router = Router()

@universal_router.message()
async def catch_all_messages(event: Update) -> None:
    print("Received MESSAGE event: ")
    print(event.model_dump())

@universal_router.edited_message()
async def catch_all_edited_messages(event: Update) -> None:
    print("Received EDITED MESSAGE event:")
    print(event.model_dump())

@universal_router.channel_post()
async def catch_all_channel_posts(event: Update) -> None:
    print("Received CHANNEL POST event:")
    print(event.model_dump())

@universal_router.edited_channel_post()
async def catch_all_edited_channel_posts(event: Update) -> None:
    print("Received EDITED CHANNEL POST event:")
    print(event.model_dump())

@universal_router.inline_query()
async def catch_all_inline_queries(event: Update) -> None:
    print("Received INLINE QUERY event:")
    print(event.model_dump())

@universal_router.chosen_inline_result()
async def catch_all_chosen_inline_results(event: Update) -> None:
    print("Received CHOSEN INLINE RESULT event:")
    print(event.model_dump())

@universal_router.callback_query()
async def catch_all_callback_queries(event: Update) -> None:
    print("Received CALLBACK QUERY event:")
    print(event.model_dump())

@universal_router.shipping_query()
async def catch_all_shipping_queries(event: Update) -> None:
    print("Received SHIPPING QUERY event:")
    print(event.model_dump())

@universal_router.pre_checkout_query()
async def catch_all_pre_checkout_queries(event: Update) -> None:
    print("Received PRE-CHECKOUT QUERY event:")
    print(event.model_dump())

@universal_router.poll()
async def catch_all_polls(event: Update) -> None:
    print("Received POLL event:")
    print(event.model_dump())

@universal_router.poll_answer()
async def catch_all_poll_answers(event: Update) -> None:
    print("Received POLL ANSWER event:")
    print(event.model_dump())

@universal_router.my_chat_member()
async def catch_all_my_chat_member(event: Update) -> None:
    print("Received MY CHAT MEMBER event:")
    print(event.model_dump())

@universal_router.chat_member()
async def catch_all_chat_member(event: Update) -> None:
    print("Received CHAT MEMBER event:")
    print(event.model_dump())

@universal_router.chat_join_request()
async def catch_all_chat_join_requests(event: Update) -> None:
    print("Received CHAT JOIN REQUEST event:")
    print(event.model_dump())
