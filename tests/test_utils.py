from craigslist_telegram_bot import utils


class Update(object):
    def __init__(self, command):
        self.command = command

    def to_dict(self):
        return {'message': {'text': self.command}}


def test_extract_command_value():
    update = Update('/city austin')
    assert 'austin' == utils.extract_command_value(update)
