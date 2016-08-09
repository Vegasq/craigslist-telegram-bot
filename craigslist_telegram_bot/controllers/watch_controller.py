from craigslist_telegram_bot import utils
from craigslist_telegram_bot import db
from craigslist_telegram_bot import feed


def _ask_for_keyword(context, bot, update):
    context.set_context({
        'function': "craigslist_telegram_bot.controllers.watch_controller",
        'method': "watch"})

    message = "Message us what you want to watch"
    utils.send_message_with_keyboard(bot, update, message)

    return


@utils.context_wrapper
def watch(context, bot, update):
    """Add new item to watchlist"""
    keyword = utils.extract_command_value(update)

    if not keyword:
        return _ask_for_keyword(context, bot, update)
    else:
        wm = db.WatchModel()

        if not wm.is_watched(context.user_id, keyword):
            wm.watch(context.user_id, keyword)
            message = "You are now watching %s" % keyword
        else:
            message = "You already watching %s" % keyword

        utils.send_message_with_keyboard(bot, update, message)


def _ask_for_unwatch_keyword(context, bot, update):
    wm = db.WatchModel(user_id=context.user_id)

    context.set_context({
        'function': "craigslist_telegram_bot.controllers.watch_controller",
        'method': "unwatch"})

    keywords = [[i['keyword']] for i in wm.watchlist()]

    message = "Message us what you want to unwatch"
    utils.send_message_with_unwatch_keyboard(
        bot, update, message, keywords)

    return


@utils.context_wrapper
def unwatch(context, bot, update):
    keyword = utils.extract_command_value(update)

    if not keyword:
        return _ask_for_unwatch_keyword(context, bot, update)
    else:
        wm = db.WatchModel(user_id=context.user_id)

        if wm.is_watched(context.user_id, keyword):
            message = "%s removed from watching list." % keyword
            wm.unwatch(context.user_id, keyword)
        else:
            message = "Keyword %s not found in you're watching list." % keyword

        utils.send_message_with_keyboard(bot, update, message)


@utils.context_wrapper
def watchlist(context, bot, update):
    wm = db.WatchModel()

    if watchlist:
        message = "\n".join([item['keyword']
                             for item in wm.watchlist(context.user_id)])
    else:
        message = "empty"

    utils.send_message_with_keyboard(
        bot, update, "Your watchlist is:\n%s" % message)


def _get_new_posts(context):
    wm = db.WatchModel(context.user_id)
    pm = db.PostsModel()

    posts = []
    for item in wm.watchlist():
        for post in feed.get_posts(context.city, item['keyword']):
            if not pm.is_post_seen(context.user_id, post.post_id):
                posts.append(post)
                pm.mark_as_seen(context.user_id, post.post_id)
    return posts


@utils.context_wrapper
def updates(context, bot, update):
    """Returns list of updated posts"""
    posts = _get_new_posts(context)

    if not posts:
        utils.send_message_with_keyboard(bot, update, "No updates so far.")
        return

    for ten_posts in utils.chunks(posts, 10):
        updates = ""
        for post in ten_posts:
            updates += post.oneline
        utils.send_message_with_keyboard(bot, update, updates)
