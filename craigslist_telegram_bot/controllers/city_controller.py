from craigslist_telegram_bot import utils
from craigslist_telegram_bot import db
from craigslist_telegram_bot.log import LOG


@utils.context_wrapper
def city(context, bot, update):
    city_name = utils.extract_command_value(update)

    if not city_name:
        utils.set_next_step_to_city_request(context)
        message = "Tell us city you are from."

        utils.send_message_with_unwatch_keyboard(
            bot, update, message, [])

        return

    if city_name not in utils.get_craigslist_sites():
        bot.sendMessage(
            chat_id=update.message.chat_id,
            text="City not found. Please send /citylist "
                 "to check list of avaliable cities.")
        return

    user_id = utils.get_user_id(update)

    cm = db.CityModel()
    cm.set_city(user_id=user_id, city=city_name)

    utils.send_message_with_keyboard(bot, update, "City set to %s" % city_name)


@utils.context_wrapper
def citylist(context, bot, update):
    LOG.debug('Requesting citylist')
    cities_list = utils.get_craigslist_sites()
    cities_list = sorted(cities_list)

    for chunk in utils.chunks(cities_list, 200):
        LOG.debug('Generate citylist message')
        utils.send_message_with_keyboard(bot, update, " | ".join(chunk))
