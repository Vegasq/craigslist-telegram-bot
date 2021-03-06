import re
import db
import requests
import random

from craigwatch.log import LOG
from craigwatch import exceptions

import telegram


def extract_command_value(update):
    LOG.debug("Extract value from command.")
    message = update.to_dict()["message"]["text"]
    if not message.startswith('/'):
        raise exceptions.CommandNotFound('Missed starting /')
    r = re.compile(r'/\w+(\ +)(.+)')
    try:
        keyword = r.search(message).group(2)
    except AttributeError:
        raise exceptions.CommandRequiresValue()
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


def send_message_with_keyboard(bot, update, text):
    custom_keyboard = [["/update " + telegram.emoji.Emoji.ANTENNA_WITH_BARS,
                        "/watchlist " + telegram.emoji.Emoji.WATCH,
                        "/help " + telegram.emoji.Emoji.BOOKS]]

    reply_markup = telegram.ReplyKeyboardMarkup(
        custom_keyboard, resize_keyboard=True)

    bot.sendMessage(chat_id=update.message.chat_id,
                    text=text,
                    reply_markup=reply_markup,
                    parse_mode='Markdown',
                    disable_web_page_preview=True)
