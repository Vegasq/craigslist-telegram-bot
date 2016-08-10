from craigslist_telegram_bot import utils
from craigslist_telegram_bot import db


message = """Hello there!\n
First of all tell us where are you from. \
To do so send command like \"/city newyork\".
To get list of avaliable cities/places please call /citylist.
"""

help_message = """

Avaliable commands:

*<AnyMessage>* - to search for it.

*/city <CityName>* - set your city, deadly required!
*/citylist* - list of avaliable cities.

*/watch <KeyWord>* - add keyword to watchlist.
*/unwatch <KeyWord>* - remove keyword from watchlist.
*/watchlist* - print current watchlist.
*/up* or */update* - show updates from watchlist.

*/start* - introduce message.
*/help* - this message.
"""


@utils.context_wrapper
def start(context, bot, update):
    context.set_context({
        'function': "craigslist_telegram_bot.controllers.city_controller",
        'method': "city"})
    message = "Tell us city you are from."

    utils.send_message_with_keyboard(bot, update, message)


@utils.context_wrapper
def restart(context, bot, update):
    db.PostsModel().delete_all()
    db.WatchModel().delete_all()
    db.CityModel().delete_all()
    utils.send_message_with_keyboard(bot, update, "Total reset")


@utils.context_wrapper
def help(context, bot, update):
    utils.send_message_with_keyboard(bot, update, help_message)
