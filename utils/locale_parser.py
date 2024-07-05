import json


with open('text_data/messages.json', encoding='utf-8') as json_file:
    msg_data = json.load(json_file)


with open('text_data/btn_text.json', encoding='utf-8') as json_file:
    btn_data = json.load(json_file)


def get_message_text(locale: str, tag: str) -> str:
    """Получить текст сообщения по локали и тегу."""
    return msg_data[tag][locale]


def get_btn_text(locale: str, tag: str) -> str:
    """Получить текст кнопки по локали и тегу."""
    return btn_data[tag][locale]
