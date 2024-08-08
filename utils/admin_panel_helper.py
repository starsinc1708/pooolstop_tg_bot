import datetime
import os
import pandas as pd
from aiogram.types import FSInputFile
from database import db
from utils import locale_parser
from utils.buttons_callbacks_finder import get_btn_tag_from_key

async def create_new_user_stat_file(period: int) -> FSInputFile:
    end_date = datetime.datetime.utcnow()
    start_date = end_date - datetime.timedelta(days=period)

    user_sources = await db.user_ad_sources.find({
        'timestamp': {'$gte': start_date, '$lte': end_date}
    }).to_list(length=None)

    user_stats = []

    for user_source in user_sources:
        user_id = user_source['user_id']
        source_timestamp = user_source['timestamp']

        # Retrieve commands and callbacks
        commands = await db.command_logs.find({
            'user_id': user_id
        }).to_list(length=None)

        callbacks = await db.callback_logs.find({
            'user_id': user_id,
        }).to_list(length=None)

        user_doc = await db.users.find_one({
            'user_id': user_id,
        })
        username = user_doc['username'] if user_doc else 'Unknown'
        first_name = user_doc['first_name'] if user_doc else ''
        last_name = user_doc['last_name'] if user_doc else ''

        for command in commands:
            user_stats.append({
                'ID пользователя': user_id,
                'Username': username,
                'Имя': first_name,
                'Фамилия': last_name,
                'Время перехода': source_timestamp,
                'Тип лога': 'Команда',
                'Детали лога': command['command'],
                'Текст кнопки': "",
                'Время': command['datetime']
            })

        for callback in callbacks:
            user_stats.append({
                'ID пользователя': user_id,
                'Username': username,
                'Имя': first_name,
                'Фамилия': last_name,
                'Время перехода': source_timestamp,
                'Тип лога': 'Нажатие кнопки',
                'Детали лога': callback['callback_data'],
                'Текст кнопки': locale_parser.get_btn_text("ru", get_btn_tag_from_key(callback['callback_data'])),
                'Время': callback['datetime']
            })

    df = pd.DataFrame(user_stats)

    directory = './new_user_stat'
    file_name = f"user_stats_{period}_days.xlsx"
    file_path = os.path.join(directory, file_name)

    os.makedirs(directory, exist_ok=True)

    with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Статистика пользователей')
        worksheet = writer.sheets['Статистика пользователей']

        # Adjust column widths based on the maximum length of the values
        for col_num, value in enumerate(df.columns.values):
            max_length = max(df[value].astype(str).apply(len).max(), len(value)) + 2
            worksheet.set_column(col_num, col_num, max_length)

    return FSInputFile(file_path, filename=file_name)
