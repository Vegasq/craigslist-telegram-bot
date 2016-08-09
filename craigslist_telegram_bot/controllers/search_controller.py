from craigslist_telegram_bot import utils
from craigslist_telegram_bot import feed
from craigslist_telegram_bot.log import LOG


@utils.context_wrapper
def search(context, bot, update):
    # It's not actually context, but information about next steps.
    # Rename it when will have a clue how it should be named.
    if context.action_required:
        return context.next_step(bot, update)

    LOG.debug("Search actionn for user: %s, keyword: %s" %
              (context.user_id, update.message.text))
    posts = feed.get_posts(context.city, update.message.text)

    text = ""
    for p in posts:
        text += p.oneline

    if not text:
        text = "Empty search result."
    utils.send_message_with_keyboard(bot, update, text)
