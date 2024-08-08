# button_callbacks.py

# Dictionary with keys and values swapped
button_callbacks_reversed = {
    'main_info_ratings': 'btn_ratings',
    'main_info_profile': 'btn_profile',
    'main_info_service': 'btn_service',
    'main_info_settings': 'btn_settings',
    'main_info_open_admin_panel': 'btn_admin',

    'admin_new_users_stat': 'btn_new_user_stat',
    'admin_back': 'btn_back_admin',

    'main_info_back': 'btn_back',

    'registration_proposal_register_in_webapp': 'btn_register_in_webapp',

    'main_info_call_manager': 'btn_call_manager',
    'main_info_question': 'btn_question',

    'main_info_language': 'btn_language',

    'main_info_learn_more': 'btn_learn_more',
    'main_info_how_to_earn_more': 'btn_how_to_earn_more',

    'new_user_stat_1': 'btn_period_1',
    'new_user_stat_7': 'btn_period_7',
    'new_user_stat_30': 'btn_period_30',
    'back_to_admin': 'btn_back_to_admin',

    'main_info_ratings_7': 'btn_period_7',
    'main_info_ratings_30': 'btn_period_30',
    'main_info_ratings_90': 'btn_period_90',
    'main_info_ratings_180': 'btn_period_180',
    'main_info_ratings_365': 'btn_period_365',
    'main_info_notifications': 'btn_notifications',

    'subscribe_ratings_notify_period_1': 'btn_period_1',
    'subscribe_ratings_notify_period_7': 'btn_period_7',
    'subscribe_ratings_notify_period_30': 'btn_period_30',
    'unsubscribe_ratings': 'btn_unsubscribe',

    'profile_webapp_open': 'btn_webapp_open',
    'profile_statistics': 'btn_statistics',
    'profile_workers': 'btn_workers',
    'profile_wallet': 'btn_wallet',

    'language_en': 'btn_en',
    'language_ru': 'btn_ru'
}


def get_btn_tag_from_key(key: str) -> str:
    return button_callbacks_reversed.get(key, 'Not found')
