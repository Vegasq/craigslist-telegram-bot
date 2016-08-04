from craigwatch import utils
from craigwatch import db
from craigwatch import feed

from craigwatch.log import LOG


class SearchController(object):
    @staticmethod
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
