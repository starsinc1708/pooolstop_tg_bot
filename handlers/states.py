from aiogram.fsm.state import StatesGroup, State


class Greeting(StatesGroup):
    settings_page = State()
    profile_page_statistics = State()
    profile_page_workers = State()
    start_msg = State()
    notifications_ratings_page = State()
    registered_no = State()
    registered_yes = State()
    main_menu = State()
    who_we_are = State()
    menu_page = State()
    profile_page = State()
    rating_page = State()
    our_social_networks = State()
    cmd_list = State()
    account_link = State()
