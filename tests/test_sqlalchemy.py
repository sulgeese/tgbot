from sqlalchemy import inspect
from sqlmodel import SQLModel


def check_instance_lifecycle(instance: SQLModel) -> None:
    state = inspect(instance)
    if state.session:
        print("Объект привязан к сессии.")
    else:
        print("Объект не привязан к сессии.")
    if state.transient:
        print("Объект находится в состоянии transient.")
    elif state.persistent:
        print("Объект находится в состоянии persistent.")
    elif state.deleted:
        print("Объект находится в состоянии deleted.")
    elif state.detached:
        print("Объект находится в состоянии detached.")
    elif state.pending:
        print("Объект находится в состоянии pending.")