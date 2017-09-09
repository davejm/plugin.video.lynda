import requests
import time
import hashlib
import urllib
import math

class LyndaApi:
    API_HOST = "https://api-1.lynda.com"
    APP_KEY = "DC325E0DF73140E48DE3C0406B911B04"
    USER_AGENT = "Dalvik/2.1.0 (Linux; U; Android 6.0; Android SDK built for x86 Build/MASTER)"
    HASH_KEY = "DC325E0DF73140E48DE3C0406B911B04F0CFC5A8D3BB4F82878947BD6D0BC3A1"

    def _make_hash(self, url):
        return hashlib.md5(self.HASH_KEY + url + str(int(time.time()))).hexdigest()

    def _headers(self, url):
        return {
            "appkey": self.APP_KEY,
            "timestamp": str(int(time.time())),
            "hash": self._make_hash(url),
            "Accept-Language": "en",
            "User-Agent": self.USER_AGENT
        }

    def _get(self, endpoint, params, new_headers=[]):
        url = self.API_HOST + endpoint
        urlencoded_params = urllib.urlencode(params)
        url_with_params = url + "?" + urlencoded_params

        headers = self._headers(url_with_params)
        # Override/add headers
        for h in new_headers:
            headers[h] = new_headers[h]

        resp = requests.get(url, params=params, headers=headers)
        return resp

    def _post(self, endpoint, data):
        pass

    def course_search(self, query):
        params = {
            "filter.includes": "Courses.ID,Courses.Title,Courses.DateReleasedUtc,Courses.HasAccess,Courses.PlaylistIds,Courses.DurationInSeconds,Courses.Description",
            "productType": 2,
            "order": "ByRelevancy",
            "start": 0,
            "limit": 20,
            "q": query
        }
        print("thequery")
        resp = self._get('/search', params).json()
        courses = []
        c = 0
        for course in resp['Courses']:
            # Only get the first few course images as requests are slow
            if c < 5:
                thumb_url = self.course_thumb(course['ID'])
            else:
                thumb_url = None
            courses.append(Course(
                course['Title'],
                course['ID'],
                thumb_url,
                course['Description']
            ))
            c += 1
        return courses

    def course_thumb(self, course_id):
        width = 480
        endpoint = '/course/{0}/thumb'.format(course_id)
        params = {
            "w": width,
            "h": int(math.ceil(width / 1.7777778)),
            "colorHex": "000000"
        }
        resp = self._get(endpoint, params)
        return resp.url


    def course_chapters(self, course_id):
        endpoint = '/course/{0}'.format(course_id)
        params = {
            "filter.includes": "ID,Chapters.ID,Chapters.Title"
        }
        resp = self._get(endpoint, params).json()
        chapters = []
        for chapter in resp['Chapters']:
            chapters.append(Chapter(
                chapter['ID'],
                chapter['Title']
            ))
        return chapters


class Course:
    def __init__(self, title, course_id, thumb_url, description):
        self.title = title
        self.course_id = course_id
        self.thumb_url = thumb_url
        self.description = description

class Chapter:
    def __init__(self, chapter_id, title):
        self.chapter_id = chapter_id
        self.title = title
