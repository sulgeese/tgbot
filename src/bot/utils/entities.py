import json

from aiogram.types.message_entity import MessageEntity


def entities_to_str(entities: list) -> str:
    if entities is None:
        return json.dumps(None)
    lst = []
    for ent in entities:
        lst.append(ent.__dict__)
    return json.dumps(lst)


def str_to_entities(string: str, offset: int) -> list[MessageEntity] | None:
    if string == 'null':
        return None
    entities = []
    lst = json.loads(string)
    for kwargs in lst:
        kwargs["offset"] = kwargs.get("offset", 0) + offset
        entities.append(MessageEntity(**kwargs))
    return entities
