# from tinydb import TinyDB, Query
from craigwatch.log import LOG
from craigwatch import exceptions
import pymongo
from pymongo import MongoClient


# db = TinyDB('db.json')


class GenericMongoModel(object):
    def __init__(self):
        self.mongo_client = pymongo.MongoClient('localhost', 32770)
        self.db = self.mongo_client.craigwatch
        self.table = "UNSET"

    def delete_all(self):
        self.table.delete_many({})


class PostsModel(GenericMongoModel):
    # query = Query()
    # table = db.table('posts')
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

    # @staticmethod
    # def mark_as_seen(user_id, post_id):
    #     if not PostsModel.is_post_seen(user_id, post_id):
    #         PostsModel.table.insert(
    #             {'user_id': user_id,
    #              'post_id': post_id,
    #              'status': PostsModel.POST_ALREADY_SEEN})
    #     else:
    #         LOG.error("Post already marked as seen")

    # @staticmethod
    # def is_post_seen(user_id, post_id):
    #     result = PostsModel.table.search(
    #         (PostsModel.query.user_id == user_id) &
    #         (PostsModel.query.post_id == post_id) &
    #         (PostsModel.query.status == PostsModel.POST_ALREADY_SEEN))

    #     if len(result) >= 2:
    #         PostsModel.table.remove(PostsModel.query.user_id == user_id)
    #         LOG.error("Multiple post statuses for one user %s" % user_id)
    #         return None
    #     if not result:
    #         return False
    #     return True


class CityModel(GenericMongoModel):

    def __init__(self):
        super(CityModel, self).__init__()
        self.table = self.db.cities

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


    # query = Query()
    # table = db.table('citydb')

    # @staticmethod
    # def set_city(user_id, city):
    #     if not city:
    #         raise exceptions.EmptyCityException()
    #     if not user_id:
    #         raise exceptions.NoUserException()

    #     CityModel.table.insert({'user_id': user_id, 'city': city})

    # @staticmethod
    # def get_city(user_id):
    #     if not user_id:
    #         raise exceptions.NoUserException()

    #     result = CityModel.table.search(CityModel.query.user_id == user_id)
    #     if len(result) >= 2:
    #         CityModel.table.remove(CityModel.query.user_id == user_id)
    #         LOG.error("Multiple cities for one user %s" % user_id)
    #         return None
    #     if not result:
    #         LOG.error('City not found, please set one.')
    #         return None
    #     return result[0]['city']

    # @staticmethod
    # def update_city(user_id, city):
    #     if not user_id:
    #         raise exceptions.NoUserException()
    #     if not city:
    #         raise exceptions.EmptyCityException()

    #     CityModel.table.update(
    #         {'city': city}, CityModel.query.user_id == user_id)

    # @staticmethod
    # def update_or_set(user_id, city):
    #     if CityModel.get_city(user_id) is None:
    #         CityModel.set_city(user_id, city)
    #     else:
    #         CityModel.update_city(user_id, city)


class WatchModel(GenericMongoModel):

    def __init__(self):
        super(WatchModel, self).__init__()
        self.table = self.db.watch

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

    def watchlist(self, user_id):
        LOG.debug("watchlist user_id:%s" % user_id)
        if not user_id:
            raise exceptions.NoUserException()
        return self.table.find({"user_id": user_id})


    # query = Query()
    # table = db.table('watchdb')

    # @staticmethod
    # def watch(user_id, keyword):
    #     if not user_id:
    #         raise exceptions.NoUserException()
    #     if not keyword:
    #         raise exceptions.EmptyKeywordException()

    #     WatchModel.table.insert({'user_id': user_id, 'keyword': keyword})

    # @staticmethod
    # def unwatch(user_id, keyword):
    #     if not user_id:
    #         raise exceptions.NoUserException()
    #     if not keyword:
    #         raise exceptions.EmptyKeywordException()

    #     WatchModel.table.remove((WatchModel.query.user_id == user_id) &
    #                             (WatchModel.query.keyword == keyword))

    # @staticmethod
    # def watchlist(user_id):
    #     if not user_id:
    #         raise exceptions.NoUserException()

    #     return WatchModel.table.search(WatchModel.query.user_id == user_id)

    # @staticmethod
    # def contains_in_watchlist(user_id, keyword):
    #     if not user_id:
    #         raise exceptions.NoUserException()
    #     if not keyword:
    #         raise exceptions.EmptyKeywordException()

    #     return WatchModel.table.search((WatchModel.query.user_id == user_id) &
    #                                    (WatchModel.query.keyword == keyword))
