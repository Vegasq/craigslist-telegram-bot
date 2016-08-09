import pymongo
import json
import importlib

from craigslist_telegram_bot.log import LOG
from craigslist_telegram_bot import exceptions
from craigslist_telegram_bot import settings


class GenericMongoModel(object):
    def __init__(self):
        self.mongo_client = pymongo.MongoClient(settings.MONGO_HOST,
                                                settings.MONGO_PORT)
        self.db = self.mongo_client.craigwatch
        self.table = "UNSET"

    def delete_all(self):
        self.table.delete_many({})


class ContextModel(GenericMongoModel):
    city = None
    data = None

    @property
    def action_required(self):
        return True if self.data else False

    def __init__(self, user_id=None, city=None):
        super(ContextModel, self).__init__()
        self.table = self.db.context
        if city:
            self.city = city

        if user_id:
            self.user_id = user_id
            self.data = self._get_context(user_id)
            LOG.debug("Context set to: %s" % self.data)

    def set_context(self, context):
        self.delete_context()
        return self.table.insert_one({
            "user_id": self.user_id,
            "context": json.dumps(context)})

    def _get_context(self, user_id):
        result = self.table.find_one({"user_id": user_id})
        if not result:
            return None
        return json.loads(result['context'])

    def delete_context(self, user_id=None):
        if not user_id and not self.user_id:
            raise Exception("No user_id provided")
        if user_id and self.user_id:
            raise Exception("Do not remove context from another context")

        if not user_id:
            user_id = self.user_id
        self.table.delete_one({"user_id": user_id})

    def next_step(self, bot, update):
        # Execute
        if self.data and 'function' in self.data and 'method' in self.data:
            mdl = importlib.import_module(self.data['function'])
            LOG.debug("Execute method from context:")
            val = getattr(mdl, self.data['method'])(bot, update)

            self.delete_context()
            return val


class PostsModel(GenericMongoModel):
    POST_ALREADY_SEEN = 1

    def __init__(self):
        super(PostsModel, self).__init__()
        self.table = self.db.posts

    def is_post_seen(self, user_id, post_id):
        LOG.debug("is_post_seen user_id:%s post_id:%s" % (user_id, post_id))
        return self.table.find_one({
            "user_id": user_id,
            "post_id": post_id,
            "status": self.POST_ALREADY_SEEN})

    def mark_as_seen(self, user_id, post_id):
        LOG.debug("mark_as_seen user_id:%s post_id:%s" % (user_id, post_id))
        if not self.is_post_seen(user_id, post_id):
            self.table.insert_one({
                "user_id": user_id,
                "post_id": post_id,
                "status": PostsModel.POST_ALREADY_SEEN})


class CityModel(GenericMongoModel):
    city = None

    def __init__(self, user_id=None):
        super(CityModel, self).__init__()
        self.table = self.db.cities
        if user_id:
            self.user_id = user_id
            self.city = self.get_city(user_id)
            LOG.debug("Loading city %s for user_id %s" % (self.city, user_id))

    def is_city_set(self, user_id):
        LOG.debug("is_city_set user_id:%s" % user_id)
        if self.table.find_one({"user_id": user_id}):
            return True
        return False

    def set_city(self, user_id, city):
        LOG.debug("set_city user_id:%s city:%s" % (user_id, city))
        if not city:
            raise exceptions.EmptyCityException()
        if not user_id:
            raise exceptions.NoUserException()

        city = city.lower()

        if not self.is_city_set(user_id):
            self.table.insert_one({
                "user_id": user_id,
                "city": city})
        else:
            self.table.update_one(
                {"user_id": user_id},
                {"$set": {"city": city}})

    def get_city(self, user_id):
        LOG.debug("get_city user_id:%s" % user_id)
        if not user_id:
            raise exceptions.NoUserException()

        result = self.table.find_one({"user_id": user_id})
        LOG.error(result)
        if result is None:
            return None
        return result['city']

    def update_city(self, user_id, city):
        LOG.info("Replace update_city with set_city")
        return self.set_city(user_id, city)

    def update_or_set(self, user_id, city):
        LOG.info("Replace update_or_set with set_city")
        return self.set_city(user_id, city)


class WatchModel(GenericMongoModel):
    user_id = None

    def __init__(self, user_id=None):
        super(WatchModel, self).__init__()
        self.table = self.db.watch
        if user_id:
            self.user_id = user_id

    def is_watched(self, user_id, keyword):
        LOG.debug("is_watched user_id:%s keyword:%s" % (user_id, keyword))
        if not user_id:
            raise exceptions.NoUserException()
        if not keyword:
            raise exceptions.EmptyKeywordException()

        keyword = keyword.lower()

        if self.table.find_one({"user_id": user_id,
                                "keyword": keyword}):
            return True
        return False

    def contains_in_watchlist(self, user_id, keyword):
        LOG.info("Replace contains_in_watchlist with is_watched")
        return self.is_watched(user_id, keyword)

    def watch(self, user_id, keyword):
        LOG.debug("watch user_id:%s keyword:%s" % (user_id, keyword))
        if not user_id:
            raise exceptions.NoUserException()
        if not keyword:
            raise exceptions.EmptyKeywordException()

        keyword = keyword.lower()

        if not self.is_watched(user_id, keyword):
            self.table.insert_one({
                "user_id": user_id,
                "keyword": keyword})

    def unwatch(self, user_id, keyword):
        LOG.debug("unwatch user_id:%s keyword:%s" % (user_id, keyword))
        if not user_id:
            raise exceptions.NoUserException()
        if not keyword:
            raise exceptions.EmptyKeywordException()

        keyword = keyword.lower()

        if self.is_watched(user_id, keyword):
            self.table.delete_one({
                "user_id": user_id,
                "keyword": keyword})

    def watchlist(self, user_id=None):
        LOG.debug("watchlist user_id:%s" % user_id)
        if not user_id and not self.user_id:
            raise exceptions.NoUserException()
        user_id = user_id if user_id else self.user_id
        return self.table.find({"user_id": user_id})
