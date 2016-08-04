import pytest
import feedparser

from craigwatch import feed


class TestPost(object):

    def test_price_parser(self):
        p = feed.Post({'title': 'Fake message',
                       'link': 'fake',
                       'summary': 'summary'})
        assert p.price is None

        p = feed.Post({'title': 'Fake message &#x0024;777',
                       'link': 'fake',
                       'summary': 'summary'})
        assert p.price == 777

        p = feed.Post({'title': 'Fake message &#x0024;777more trash',
                       'link': 'fake',
                       'summary': 'summary'})
        assert p.price == 777

        p = feed.Post({'title': '',
                       'link': 'fake',
                       'summary': 'summary'})
        assert p.price is None

        with pytest.raises(feed.FieldLeakException):
            p = feed.Post({'link': 'fake',
                           'summary': 'summary'})

    def test_post_id(self):
        p = feed.Post({'title': 'Fake message',
                       'link': 'fake_id',
                       'summary': 'summary'})
        assert p.post_id == 'fake_id'

    def test_description(self):
        p = feed.Post({'title': 'Fake message',
                       'link': 'fake',
                       'summary': 'fake_desc'})
        assert p.description == 'fake_desc'

    def test_link(self):
        p = feed.Post({'title': 'Fake message',
                       'link': 'fake_link',
                       'summary': 'summary'})
        assert p.link == 'fake_link'

    def test_title(self):
        p = feed.Post({'title': 'Fake message &#x0024;123',
                       'link': 'fake',
                       'summary': 'summary'})
        assert p.title == 'Fake message $123'

        p = feed.Post({'title': 'Fake message',
                       'link': 'fake',
                       'summary': 'summary'})
        assert p.title == 'Fake message'

    def test_oneline(self):
        p = feed.Post({'title': 'Item title &#x0024;777',
                       'id': 'internal_id',
                       'link': 'http://example.com',
                       'summary': 'My wonderfull item'})
        assert p.oneline == '777$ \t Item title $777\nhttp://example.com\n\n'

        p = feed.Post({'title': 'Item title',
                       'id': 'internal_id',
                       'link': 'http://example.com',
                       'summary': 'My wonderfull item'})
        assert p.oneline == "Unknown price$ \t Item title\n"\
                            "http://example.com\n\n"


fake_craig_responce = {
    'entries': [
        {
            'title': 'Item 1 &#x0024;100',
            'link': 'http://example.com/1',
            'summary': 'Item 1 desc',
        },
        {
            'title': 'Item 2 &#x0024;100',
            'link': 'http://example.com/2',
            'summary': 'Item 2 desc',
        },
        {
            'title': 'Item 3 &#x0024;100',
            'link': 'http://example.com/3',
            'summary': 'Item 3 desc',
        },
    ]
}


class TestPosts(object):
    def test_posts(self):
        assert len(feed.Posts(fake_craig_responce)) == 3


class TestGetPosts(object):
    def test_get_posts(self, monkeypatch):
        def parse(url):
            return fake_craig_responce
        monkeypatch.setattr(feedparser, 'parse', parse)
        posts = feed.get_posts('austin', 'cake')
        assert type(posts) == feed.Posts
        assert len(posts) == 3
