#!/usr/bin/python
from telegram.ext import Updater
from telegram.ext import MessageHandler, Filters
from telegram.ext import CommandHandler

from craigslist_telegram_bot.controllers import watch_controller
from craigslist_telegram_bot.controllers import city_controller
from craigslist_telegram_bot.controllers import start_controller
from craigslist_telegram_bot.controllers import search_controller
from craigslist_telegram_bot.log import LOG
from craigslist_telegram_bot import settings


class Robot(object):
    def __init__(self):
        self.updater = Updater(token=settings.TELEGRAM_TOKEN)
        self.dispatcher = self.updater.dispatcher

        # Register WatchController
        up_handler = CommandHandler("up", watch_controller.updates)
        watch_handler = CommandHandler("watch", watch_controller.watch)
        update_handler = CommandHandler("update", watch_controller.updates)
        unwatch_handler = CommandHandler("unwatch", watch_controller.unwatch)
        watchls_handler = CommandHandler("watchlist",
                                         watch_controller.watchlist)

        self.dispatcher.add_handler(watch_handler)
        self.dispatcher.add_handler(unwatch_handler)
        self.dispatcher.add_handler(watchls_handler)
        self.dispatcher.add_handler(update_handler)
        self.dispatcher.add_handler(up_handler)

        # Register search_controller
        search_handler = MessageHandler([Filters.text],
                                        search_controller.search)
        self.dispatcher.add_handler(search_handler)

        # Register city_controller
        city_handler = CommandHandler("city", city_controller.city)
        cityls_handler = CommandHandler("citylist", city_controller.citylist)
        self.dispatcher.add_handler(city_handler)
        self.dispatcher.add_handler(cityls_handler)

        # Register StartController
        start_handler = CommandHandler("start", start_controller.start)
        self.dispatcher.add_handler(start_handler)

        restart_handler = CommandHandler("restart",
                                         start_controller.restart)
        self.dispatcher.add_handler(restart_handler)

        help_handler = CommandHandler("help", start_controller.help)
        self.dispatcher.add_handler(help_handler)

        self.updater.start_polling()

    def stop(self):
        self.updater.stop()


def main():
    try:
        r = Robot()
        while True:
            pass
    except KeyboardInterrupt:
        LOG.error("KeyboardInterrupt")
        r.stop()
        exit()


if __name__ == "__main__":
    main()
