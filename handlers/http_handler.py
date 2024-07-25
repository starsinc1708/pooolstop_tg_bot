from aiohttp import web
from aiogram import Bot
from db_utils import user_sync_from_web_app, desync_from_web_app, get_user_web_app, get_user_by_chat_id
import database as db
from dotenv import load_dotenv
import os
from keyboards.Inline_keyboards import get_inline_keyboard, ratings_keyboard
from pooolstop_api.rating_service import parse_pool, parse_pool_with_watcher
from utils.notification_sender import configure_message_head, format_pool_row, \
    configure_message_footer

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')


async def sync_telegram_user(request):
    try:
        user_info = await request.json()
        await user_sync_from_web_app(user_info)
        response = {"code": 200, "message": "", "status": "success", "data": ""}
        return web.json_response(response, status=200)
    except Exception as e:
        response = {"code": 500, "message": str(e), "status": "error", "data": ""}
        return web.json_response(response, status=400)


async def delete_telegram_user(request):
    try:
        user_info = await request.json()
        await desync_from_web_app(user_info)
        response = {"code": 200, "message": "", "status": "success", "data": user_info.get('tg_id')}
        return web.json_response(response, status=200)
    except Exception as e:
        response = {"code": 500, "message": str(e), "status": "error", "data": ""}
        return web.json_response(response, status=400)


async def check_telegram_user_synced(request):
    try:
        user_info = await request.json()
        data = await get_user_web_app(user_info)
        if data:
            response = {"code": 200, "message": "", "status": "success", "data": data}
            return web.json_response(response, status=200)
        else:
            response = {"code": 400, "message": "no such user in db", "status": "not found", "data": ""}
            return web.json_response(response, status=200)
    except Exception as e:
        response = {"code": 500, "message": str(e), "status": "error", "data": ""}
        return web.json_response(response, status=400)


async def send_custom_message(request):
    try:
        request_data = await request.json()
        chat_id = request_data.get('chat_id')
        message_text = request_data.get('message')
        message_type = request_data.get('message_type')

        if chat_id and message_text and message_type:
            bot = Bot(token=BOT_TOKEN)
            results = await configure_and_send_message(bot, [chat_id], message_text, message_type)
            if results and len(results) == 1:
                result = results[0]
                await db.log_custom_message(
                    chat_id=chat_id,
                    message_text=message_text,
                    message_type=message_type,
                    status=result["status"],
                    error_message=result.get("error_message")
                )
            response = {"code": 200, "message": f"Message {message_type} sent successfully", "status": "success"}
            return web.json_response(response, status=200)
        else:
            raise ValueError("chat_id, message, and message_type are required fields")
    except ValueError as ve:
        response = {"code": 500, "message": str(ve), "status": "error", "data": ""}
        return web.json_response(response, status=400)
    except Exception as e:
        response = {"code": 500, "message": str(e), "status": "error", "data": ""}
        return web.json_response(response, status=400)



async def send_custom_message_bulk(request):
    try:
        request_body = await request.text()
        if not request_body.strip():
            raise ValueError("Request body is empty")

        request_data = await request.json()
        receivers = request_data.get('receivers')
        message_text = request_data.get('message')
        message_type = request_data.get('message_type')

        if not receivers or not message_text or not message_type:
            raise ValueError("receivers, message, and message_type are required fields")

        bot = Bot(token=BOT_TOKEN)

        chat_ids = [receiver.get('chat_id') for receiver in receivers if receiver.get('chat_id')]
        potential_sends = len(chat_ids)

        # Запуск рассылки и получение результатов
        results = await configure_and_send_message(bot, chat_ids, message_text, message_type)
        successful_sends = sum(1 for result in results if result["status"] == "success")

        # Логирование массовой рассылки с деталями
        await db.log_bulk_send(potential_sends, successful_sends, message_text, message_type, results)

        response = {"code": 200, "message": f"Message {message_type} sent successfully to {successful_sends}/{potential_sends} receivers",
                    "status": "success"}
        return web.json_response(response, status=200)

    except ValueError as ve:
        response = {"code": 500, "message": str(ve), "status": "error", "data": ""}
        return web.json_response(response, status=400)

    except Exception as e:
        response = {"code": 500, "message": str(e), "status": "error", "data": ""}
        return web.json_response(response, status=400)



async def configure_and_send_message(bot, chat_ids, message_text, message_type):
    results = []
    # Обработаем случай, когда chat_ids — это одиночное значение
    if isinstance(chat_ids, int):
        chat_ids = [chat_ids]

    for chat_id in chat_ids:
        try:
            user = await get_user_by_chat_id(chat_id)
            if user:
                keyboard = get_inline_keyboard(message_type, user['locale'])
            else:
                keyboard = get_inline_keyboard(message_type)

            await bot.send_message(chat_id=chat_id, text=message_text, reply_markup=keyboard, parse_mode='HTML', disable_web_page_preview=True)
            results.append({"chat_id": chat_id, "status": "success", "error_message": None})

        except Exception as e:
            results.append({"chat_id": chat_id, "status": "failure", "error_message": str(e)})

    return results




async def send_ratings(request):
    try:
        request_data = await request.json()
        ratings = request_data.get('ratings')
        chat_id = request_data.get('chat_id')
        locale = db.get_user_locale_by_id(chat_id)
        if not locale:
            raise Exception("The user did not use the bot")

        if chat_id and ratings:
            data = []
            index = 1
            user_rate = 0
            for pool in ratings:
                if pool['is_user']:
                    user_rate = float(pool['avr_pay_rate'])

            if user_rate == 0:
                for pool in ratings:
                    data.append(parse_pool(pool, index))
                    index = index + 1
                head_key = "ratings_msg_head"
                footer_key = "ratings_msg_footer"
                msg = configure_message_head(locale, head_key, 7)
                for pool in data:
                    msg += format_pool_row(pool, with_user=False)
                msg += configure_message_footer(locale, footer_key)
            else:
                for pool in ratings:
                    data.append(parse_pool_with_watcher(pool, index, user_rate))
                    index = index + 1
                head_key = "ratings_msg_head_watcher"
                footer_key = "ratings_msg_footer_watcher"
                msg = configure_message_head(locale, head_key, 7)
                for pool in data:
                    msg += format_pool_row(pool, with_user=True)
                msg += configure_message_footer(locale, footer_key)

            bot = Bot(token=BOT_TOKEN)
            await bot.send_message(chat_id=chat_id,
                                   text=msg,
                                   parse_mode="MARKDOWN",
                                   reply_markup=ratings_keyboard(locale),
                                   disable_web_page_preview=True)
            response = {"code": 200, "message": "Ratings sent successfully", "status": "success"}
            return web.json_response(response, status=200)
        else:
            raise ValueError("chat_id and ratings are required fields")
    except Exception as e:
        response = {"code": 500, "message": str(e), "status": "error", "data": ""}
        return web.json_response(response, status=400)


def setup_routes(app):
    app.router.add_post('/api/create/tgsync', sync_telegram_user)
    app.router.add_post('/api/delete/tgsync', delete_telegram_user)
    app.router.add_post('/api/tgsync', check_telegram_user_synced)
    app.router.add_post('/api/message/send-to-one', send_custom_message)
    app.router.add_post('/api/message/send-to-many', send_custom_message_bulk)
    app.router.add_post('/api/message/send-ratings', send_ratings)

    return app.router
