from aiogram.fsm.state import StatesGroup, State


class StepsForm(StatesGroup):
    START = State()
    EDIT_GET_DATE = State()
    EDIT_GET_TITLE = State()
    EDIT_GET_TEXT = State()
    EDIT_GET_MENTIONS = State()

    CREATE_EVENT = State()
    GET_TITLE = State()
    GET_DATE = State()
    GET_TEXT = State()
    GET_MENTIONS = State()
    WAITING_CONFIRM = State()

    DELETE_EVENTS = State()

    VIEW_EVENTS = State()

    EDIT_EVENTS = State()
    # GET_DATE = State()
    # GET_TITLE = State()
    # GET_TEXT = State()
    # GET_MENTION = State()