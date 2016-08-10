import re
import requests
import time

from craigslist_telegram_bot import db
from craigslist_telegram_bot import utils
from craigslist_telegram_bot.log import LOG
from craigslist_telegram_bot import exceptions

import telegram


def set_next_step_to_city_request(context):
    context.set_context({
        'function': "craigslist_telegram_bot.controllers.city_controller",
        'method': "city"})


def context_wrapper(fn):
    def internal_context_wrapper(bot, update):
        user_id = get_user_id(update)
        cm = db.CityModel(user_id=user_id)

        ctx = db.ContextModel(
            user_id=user_id,
            city=cm.city
        )

        if not cm.city and is_update_contain_citylist_command(update):
            # do staff
            pass
        elif (not cm.city and is_update_contain_command(update)) or\
                (not cm.city and not ctx.is_next_step_city_set()):
            set_next_step_to_city_request(ctx)
            message = "Tell us city you are from:"
            utils.send_message_with_keyboard(bot, update, message)
            return

        return fn(ctx, bot, update)
    return internal_context_wrapper


def is_update_contain_command(update):
    if update.to_dict()["message"]["text"].startswith('/'):
        return True
    return False


def is_update_contain_citylist_command(update):
    if update.to_dict()["message"]["text"].startswith('/citylist'):
        return True
    return False


def extract_command_value(update, value_required=False):
    LOG.debug("Extract value from command.")
    message = update.to_dict()["message"]["text"]
    if not message.startswith('/'):
        LOG.debug("Command not found")
        return message
    r = re.compile(r'/\w+(\ +)(.+)')
    try:
        keyword = r.search(message).group(2)
    except AttributeError:
        if value_required:
            raise exceptions.CommandRequiresValue()
        else:
            return None
    if not keyword:
        raise Exception('Keyword is empty')
    return keyword


def get_user_id(update):
    LOG.debug('Unpack user_id from update')
    return update.to_dict()["message"]["from"]["id"]


def city_required(fn):
    def check_city(bot, update):
        cm = db.CityModel()
        user_id = get_user_id(update)
        user_city = cm.get_city(user_id)
        if not user_city:
            bot.sendMessage(chat_id=update.message.chat_id,
                            text="Please set city by sending /city CITYNAME.")
        else:
            return fn(bot, update)
    return check_city


def get_craigslist_sites():
    r = re.compile('href="//(\w+).craigslist')
    result = r.findall(
        requests.get("http://www.craigslist.org/about/sites").text)

    result = list(set(result))
    result.remove('www')
    result.remove('mobile')
    return result


def chunks(l, n):
    """Yield successive n-sized chunks from l.
    http://stackoverflow.com/posts/312464/revisions
    """
    for i in range(0, len(l), n):
        yield l[i:i+n]


def send_message_with_unwatch_keyboard(bot, update, text, watchlist):
    reply_markup = telegram.ReplyKeyboardMarkup(
        watchlist, resize_keyboard=True)

    bot.sendMessage(chat_id=update.message.chat_id,
                    text=text,
                    reply_markup=reply_markup,
                    parse_mode='Markdown',
                    disable_web_page_preview=True)


def send_message_with_keyboard(bot, update, text):
    custom_keyboard = [["/watch", "/unwatch"],
                       ["/update " + telegram.emoji.Emoji.ANTENNA_WITH_BARS,
                        "/watchlist " + telegram.emoji.Emoji.WATCH,
                        "/help " + telegram.emoji.Emoji.BOOKS]]

    reply_markup = telegram.ReplyKeyboardMarkup(
        custom_keyboard, resize_keyboard=True)

    bot.sendMessage(chat_id=update.message.chat_id,
                    text=text,
                    reply_markup=reply_markup,
                    parse_mode='Markdown',
                    disable_web_page_preview=True)


def timing(f):
    def wrap(*args, **kwargs):
        LOG.error(args)
        LOG.error(kwargs)
        time1 = time.time()
        ret = f(*args, **kwargs)
        time2 = time.time()
        LOG.error('function took %s ms' % (time2-time1))
        return ret
    return wrap
