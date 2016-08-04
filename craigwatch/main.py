#!/usr/bin/python
from telegram.ext import Updater
from telegram.ext import MessageHandler, Filters
from telegram.ext import CommandHandler

import controllers

from craigwatch.log import LOG


TG_TOKEN = "240427566:AAGl5wVArPdoGSBR4nwJks0esJzwJK4B0XQ"


class Robot(object):
    def __init__(self):
        self.updater = Updater(token=TG_TOKEN)
        self.dispatcher = self.updater.dispatcher

        # Register WatchController
        watch_handler = CommandHandler(
            "watch", controllers.WatchController.watch)
        unwatch_handler = CommandHandler(
            "unwatch", controllers.WatchController.unwatch)
        watchlist_handler = CommandHandler(
            "watchlist", controllers.WatchController.watchlist)
        updates_handler = CommandHandler(
            "update", controllers.WatchController.updates)
        up_handler = CommandHandler(
            "up", controllers.WatchController.updates)

        self.dispatcher.add_handler(watch_handler)
        self.dispatcher.add_handler(unwatch_handler)
        self.dispatcher.add_handler(watchlist_handler)
        self.dispatcher.add_handler(updates_handler)
        self.dispatcher.add_handler(up_handler)

        # Register SearchController
        search_handler = MessageHandler(
            [Filters.text], controllers.SearchController.search)
        self.dispatcher.add_handler(search_handler)

        # Register CityController
        city_handler = CommandHandler("city", controllers.CityController.city)
        citylist_handler = CommandHandler("citylist", controllers.CityController.citylist)
        self.dispatcher.add_handler(city_handler)
        self.dispatcher.add_handler(citylist_handler)

        # Register StartController
        start_handler = CommandHandler("start", controllers.StartController.start)
        self.dispatcher.add_handler(start_handler)

        restart_handler = CommandHandler("restart", controllers.StartController.restart)
        self.dispatcher.add_handler(restart_handler)

        help_handler = CommandHandler("help", controllers.StartController.help)
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
