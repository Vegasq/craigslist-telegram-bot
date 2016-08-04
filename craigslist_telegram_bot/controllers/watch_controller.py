from craigslist_telegram_bot import utils
from craigslist_telegram_bot import db
from craigslist_telegram_bot import feed


def watch(bot, update):
    """Add new item to watchlist"""
    user_id = utils.get_user_id(update)
    keyword = utils.extract_command_value(update)

    wm = db.WatchModel()

    if not wm.is_watched(user_id, keyword):
        wm.watch(user_id, keyword)
        message = "You are now watching %s" % keyword
    else:
        message = "You already watching %s" % keyword

    utils.send_message_with_keyboard(bot, update, message)


def unwatch(bot, update):
    user_id = utils.get_user_id(update)
    keyword = utils.extract_command_value(update)

    wm = db.WatchModel()

    if wm.is_watched(user_id, keyword):
        wm.unwatch(user_id, keyword)
        message = "%s removed from watching list." % keyword
    else:
        message = "Keyword %s not found in you're watching list." % keyword

    utils.send_message_with_keyboard(bot, update, message)


def watchlist(bot, update):
    user_id = utils.get_user_id(update)
    wm = db.WatchModel()
    watchlist = wm.watchlist(user_id)

    if watchlist:
        message = "\n".join([item['keyword'] for item in watchlist])
    else:
        message = "empty"

    utils.send_message_with_keyboard(
        bot, update, "Your watchlist is:\n%s" % message)


@utils.city_required
def updates(bot, update):
    """Returns list of updated posts"""
    user_id = utils.get_user_id(update)
    cm = db.CityModel()
    wm = db.WatchModel()
    pm = db.PostsModel()

    user_city = cm.get_city(user_id)
    watchlist = wm.watchlist(user_id)

    posts = []
    for item in watchlist:
        for post in feed.get_posts(user_city, item['keyword']):
            if not pm.is_post_seen(user_id, post.post_id):
                posts.append(post)
                pm.mark_as_seen(user_id, post.post_id)

    if not posts:
        utils.send_message_with_keyboard(bot, update, "No updates so far.")
        return

    for ten_posts in utils.chunks(posts, 10):
        updates = ""
        for post in ten_posts:
            updates += post.oneline
        utils.send_message_with_keyboard(bot, update, updates)
