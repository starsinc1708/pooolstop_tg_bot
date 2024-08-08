import json


with open('text_data/messages.json', encoding='utf-8') as json_file:
    msg_data = json.load(json_file)


with open('text_data/btn_text.json', encoding='utf-8') as json_file:
    btn_data = json.load(json_file)


def get_message_text(locale: str, tag: str) -> str:
    """Получить текст сообщения по локали и тегу."""
    if locale == "ru" or locale == "en":
        return msg_data[tag][locale]
    else:
        return msg_data[tag]["en"]


def get_btn_text(locale: str, tag: str) -> str:
    """Получить текст кнопки по локали и тегу."""
    if locale == "ru" or locale == "en":
        try:
            return btn_data[tag][locale]
        except KeyError:
            return 'Не найдено'
    else:
        return btn_data[tag]["en"]
