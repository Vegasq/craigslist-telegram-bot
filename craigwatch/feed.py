import feedparser
import logging
import re

CRAIGLIST_SEARCH_URL = "http://{city}.craigslist.org/search/sss?"\
                       "format=rss&query={search}"


class FieldLeakException(Exception):
    pass


class Post(object):
    # id and dc_source and link are the same
    required_fields = ['link', 'title', 'summary']

    def __init__(self, data):
        for field in self.required_fields:
            if field not in data:
                raise FieldLeakException("Field missing: %s" % field)
        self.price_regex = re.compile(r"&#x0024;(\d+)")
        self._data = data

    def __str__(self):
        return u"""{title} - {price}$\n{link}""".format(
            title=self.title,
            description=self.description,
            link=self.link,
            price=self.price)

    @property
    def price(self):
        try:
            price = int(self.price_regex.search(self._data["title"]).group(1))
        except AttributeError:
            logging.error(
                "Price not found in title '%s'" % self._data["title"])
            price = None
        except IndexError:
            logging.error(
                "Price not found in title '%s'" % self._data["title"])
            price = None
        return price

    @property
    def post_id(self):
        return self._data["link"]

    @property
    def title(self):
        return self._data["title"].replace('&#x0024;', '$')

    @property
    def link(self):
        return self._data["link"]

    @property
    def description(self):
        return self._data["summary"]

    @property
    def oneline(self):
        if self.price is None:
            price = "Unknown price"
        else:
            price = self.price
        return u"\[*{price}*$] [{title}]({link})\n\n".format(
            price=str(price), title=self.title, link=self.link)


class Posts(object):
    def __init__(self, parsed_feed):
        self._parsed_feed = parsed_feed
        self._posts = []
        if not self._parsed_feed["entries"]:
            logging.error("Empty result")
        else:
            for p in self._parsed_feed["entries"]:
                self._posts.append(Post(p))

    def __len__(self):
        return len(self._posts)

    def __iter__(self):
        self._iter_index = 0
        return self

    def next(self):
        try:
            p = self._posts[self._iter_index]
        except IndexError:
            raise StopIteration
        self._iter_index += 1
        return p

    def __next__(self):
        return self.next()


def get_posts(city, query):
    url = CRAIGLIST_SEARCH_URL.format(
        city=city,
        search=query.encode('utf-8').replace(" ", "+"))
    parsed_feed = feedparser.parse(url)
    return Posts(parsed_feed)
