import util
import requests
from random import randint


class GoogleAnalytics:
    VISITOR_FILE = 'visitor'

    def __init__(self, addon, version):
        self.addon = addon
        self.version = version

    def _get_visitorid(self):
        visitor_id = util.load_data(self.addon, self.VISITOR_FILE)
        if visitor_id is None:
            visitor_id = str(randint(0, 0x7fffffff))
            util.save_data(self.addon, self.VISITOR_FILE, visitor_id)

        return visitor_id

    def track(self, page):
        url = 'https://ssl.google-analytics.com/collect'
        payload = {
            'v': 1,
            'tid': 'UA-23742434-4',
            'cid': self._get_visitorid(),
            't': 'screenview',
            'an': 'Lynda.com Kodi Addon',
            'av': self.version,
            'cd': page
        }

        headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:11.0) Gecko/20100101 Firefox/11.0'}
        r = requests.post(url, data=payload, headers=headers)
