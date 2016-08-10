import pytest
from craigslist_telegram_bot import db
from craigslist_telegram_bot import exceptions


class TestPostsModel(object):
    def test_mark_as_seen(self, mocker):
        FAKE_POST_ID = 'postid'
        FAKE_USER_ID = 'userid'

        pm = db.PostsModel()
        insert_one = mocker.patch.object(pm.table, 'insert_one')
        mocker.patch.object(pm, 'is_post_seen', return_value=False)

        pm.mark_as_seen(FAKE_USER_ID, FAKE_POST_ID)
        insert_one.assert_called_once_with({
            'post_id': FAKE_POST_ID,
            'user_id': FAKE_USER_ID,
            'status': db.PostsModel.POST_ALREADY_SEEN})

    def test_mark_as_seen_for_already_seen(self, mocker):
        FAKE_POST_ID = 'postid'
        FAKE_USER_ID = 'userid'
        pm = db.PostsModel()
        insert_one = mocker.patch.object(pm.table, 'insert_one')
        mocker.patch.object(pm, 'is_post_seen', return_value=True)

        pm.mark_as_seen(FAKE_USER_ID, FAKE_POST_ID)
        assert insert_one.call_count == 0

    def test_is_post_seen(self, mocker):
        FAKE_POST_ID = 'postid'
        FAKE_USER_ID = 'userid'

        pm = db.PostsModel()
        mocker.patch.object(pm.table, 'find_one')
        pm.is_post_seen(FAKE_USER_ID, FAKE_POST_ID)


class TestCityModel(object):
    def test_set_city(self, mocker):
        FAKE_CITY = 'city'
        FAKE_USER_ID = 'userid'

        cm = db.CityModel()
        mocker.patch.object(cm, 'is_city_set', return_value=False)
        insert_one = mocker.patch.object(cm.table, 'insert_one')
        cm.set_city(FAKE_USER_ID, FAKE_CITY)
        insert_one.assert_called_once_with({
            'city': FAKE_CITY,
            'user_id': FAKE_USER_ID})

    def test_set_city_with_empty_city(self, mocker):
        FAKE_CITY = ''
        FAKE_USER_ID = 'userid'

        cm = db.CityModel()
        mocker.patch.object(cm.table, 'insert_one')
        with pytest.raises(exceptions.EmptyCityException):
            cm.set_city(FAKE_USER_ID, FAKE_CITY)

    def test_set_city_with_empty_user(self, mocker):
        FAKE_CITY = 'city'
        FAKE_USER_ID = ''

        cm = db.CityModel()
        mocker.patch.object(cm.table, 'insert_one')
        with pytest.raises(exceptions.NoUserException):
            cm.set_city(FAKE_USER_ID, FAKE_CITY)

    def test_get_city(self, mocker):
        cm = db.CityModel()
        find_one = mocker.patch.object(cm.table, 'find_one')
        cm.get_city('user_id')
        find_one.assert_called_once_with({'user_id': 'user_id'})

    def test_get_city_without_user(self):
        cm = db.CityModel()
        with pytest.raises(exceptions.NoUserException):
            cm.get_city('')

    def test_update_city(self, mocker):
        FAKE_USER_ID = 'userid'
        FAKE_CITY_NAME = 'austin'

        cm = db.CityModel()
        update_one = mocker.patch.object(cm.table, 'update_one')
        mocker.patch.object(cm.table, 'is_city_set', return_value=True)
        cm.update_city(FAKE_USER_ID, FAKE_CITY_NAME)
        update_one.assert_called_once_with(
            {'user_id': FAKE_USER_ID}, {'$set': {'city': FAKE_CITY_NAME}})

    def test_update_city_empty_user_id(self, mocker):
        FAKE_USER_ID = ''
        FAKE_CITY_NAME = 'austin'

        cm = db.CityModel()
        mocker.patch.object(cm.table, 'update')
        with pytest.raises(exceptions.NoUserException):
            cm.update_city(FAKE_USER_ID, FAKE_CITY_NAME)

    def test_update_city_empty_city(self, mocker):
        FAKE_USER_ID = 'userid'
        FAKE_CITY_NAME = ''

        cm = db.CityModel()
        mocker.patch.object(cm.table, 'update')
        with pytest.raises(exceptions.EmptyCityException):
            cm.update_city(FAKE_USER_ID, FAKE_CITY_NAME)


class TestCityWatch(object):
    def test_watch(self, mocker):
        FAKE_USER_ID = 'userid'
        FAKE_KEYWORD = 'phone'

        wm = db.WatchModel()
        insert_one = mocker.patch.object(wm.table, 'insert_one')
        mocker.patch.object(wm, 'is_watched', return_value=False)
        wm.watch(FAKE_USER_ID, FAKE_KEYWORD)
        insert_one.assert_called_once_with({'keyword': FAKE_KEYWORD,
                                            'user_id': FAKE_USER_ID})

    def test_watch_empty_user_id(self, mocker):
        FAKE_USER_ID = ''
        FAKE_KEYWORD = 'phone'

        wm = db.WatchModel()
        with pytest.raises(exceptions.NoUserException):
            wm.watch(FAKE_USER_ID, FAKE_KEYWORD)

    def test_watch_empty_keyword(self, mocker):
        FAKE_USER_ID = 'userid'
        FAKE_KEYWORD = ''

        wm = db.WatchModel()
        with pytest.raises(exceptions.EmptyKeywordException):
            wm.watch(FAKE_USER_ID, FAKE_KEYWORD)

    def test_unwatch(self, mocker):
        FAKE_USER_ID = 'userid'
        FAKE_KEYWORD = 'phone'

        wm = db.WatchModel()
        mocker.patch.object(wm, 'is_watched', return_value=True)
        delete_one = mocker.patch.object(wm.table, 'delete_one')
        wm.unwatch(FAKE_USER_ID, FAKE_KEYWORD)
        delete_one.assert_called_once_with(
            {'keyword': FAKE_KEYWORD, 'user_id': FAKE_USER_ID})

    def test_unwatch_no_user_id(self, mocker):
        FAKE_USER_ID = ''
        FAKE_KEYWORD = 'phone'

        wm = db.WatchModel()
        with pytest.raises(exceptions.NoUserException):
            wm.unwatch(FAKE_USER_ID, FAKE_KEYWORD)

    def test_unwatch_no_keyword(self, mocker):
        FAKE_USER_ID = 'userid'
        FAKE_KEYWORD = ''

        wm = db.WatchModel()
        with pytest.raises(exceptions.EmptyKeywordException):
            wm.unwatch(FAKE_USER_ID, FAKE_KEYWORD)

    def test_watchlist(self, mocker):
        FAKE_USER_ID = 'userid'

        wm = db.WatchModel()
        find = mocker.patch.object(wm.table, 'find')
        wm.watchlist(FAKE_USER_ID)
        find.assert_called_once_with({'user_id': FAKE_USER_ID})

    def test_watchlist_empty_user_id(self):
        FAKE_USER_ID = ''

        wm = db.WatchModel()
        with pytest.raises(exceptions.NoUserException):
            wm.watchlist(FAKE_USER_ID)

    def test_contains_in_watchlist(self, mocker):
        FAKE_USER_ID = 'userid'
        FAKE_KEYWORD = 'phone'

        wm = db.WatchModel()
        find_one = mocker.patch.object(wm.table, 'find_one')
        wm.contains_in_watchlist(FAKE_USER_ID, FAKE_KEYWORD)

        find_one.assert_called_once_with(
            {'keyword': FAKE_KEYWORD, 'user_id': FAKE_USER_ID})

    def test_contains_in_watchlist_empty_user_id(self):
        FAKE_USER_ID = ''
        FAKE_KEYWORD = 'phone'

        wm = db.WatchModel()
        with pytest.raises(exceptions.NoUserException):
            wm.contains_in_watchlist(FAKE_USER_ID, FAKE_KEYWORD)

    def test_contains_in_watchlist_empty_keyword(self):
        FAKE_USER_ID = 'userid'
        FAKE_KEYWORD = ''

        wm = db.WatchModel()
        with pytest.raises(exceptions.EmptyKeywordException):
            wm.is_watched(FAKE_USER_ID, FAKE_KEYWORD)
