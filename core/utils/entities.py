from aiogram.types.message_entity import MessageEntity
import json


def entities_to_str(entities: list) -> str:
    if entities is None:
        return json.dumps(None)
    lst = []
    for ent in entities:
        lst.append(ent.__dict__)
    return json.dumps(lst)


def str_to_entities(string: str) -> list[MessageEntity] | None:
    if string == 'null':
        return None
    entities = []
    lst = json.loads(string)
    for kwargs in lst:
        entities.append(MessageEntity(**kwargs))
    return entities


# def change_offset(entities: list, step: int) -> list[MessageEntity] | None:
#     if not entities:
#         return None
#     for ent in entities:
#         ent.offset += step
#     return entities
