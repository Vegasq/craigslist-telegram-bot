from craigslist_telegram_bot import utils
from craigslist_telegram_bot import db
from craigslist_telegram_bot import feed


@utils.city_required
def search(bot, update):
    user_id = utils.get_user_id(update)
    cm = db.CityModel()
    user_city = cm.get_city(user_id)

    posts = feed.get_posts(user_city, update.message.text)

    text = ""
    for p in posts:
        text += p.oneline

    if not text:
        text = "Empty search result."
    utils.send_message_with_keyboard(bot, update, text)
