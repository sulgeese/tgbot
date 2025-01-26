from aiogram.fsm.state import StatesGroup, State


class StepsForm(StatesGroup):
    GET_TITLE = State()
    GET_DATE = State()
    GET_TEXT = State()
    GET_MENTION = State()
    WAITING_CONFIRM = State()
    SEARCH_EVENTS = State()
    DELETE_EVENTS = State()
    EDIT_EVENTS = State()
    EDIT_EVENTS_DATE = State()
    EDIT_EVENTS_TITLE = State()
    EDIT_EVENTS_TEXT = State()
    EDIT_EVENTS_MENTIONS = State()

    CREATE_EVENT = State()
    GET_DATE = State()
    GET_TITLE = State()
    GET_TEXT = State()
    GET_MENTION = State()

    DELETE_EVENT = State()


    VIEW_EVENT = State()

    EDIT_EVENT = State()
