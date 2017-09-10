import xbmcaddon
import xbmcgui
import xbmcplugin

import sys
from urlparse import parse_qsl
from urllib import urlencode

import requests

import util
from resources.lib.lynda_api import LyndaApi

addon = xbmcaddon.Addon()
addonname = addon.getAddonInfo('name')

# Get the plugin url in plugin:// notation.
__url__ = sys.argv[0]
# Get the plugin handle as an integer number.
__handle__ = int(sys.argv[1])

__version__ = addon.getAddonInfo("version")


class LyndaAddon:
    COOKIE_FILE_NAME = 'lynda_cookies'

    def show_listing(self, listing):
        """Show a listing on the screen."""

        xbmcplugin.addDirectoryItems(__handle__, listing, len(listing))
        xbmcplugin.endOfDirectory(__handle__)

    def list_root_options(self):
        """Create the list of root options in the Kodi interface."""

        listing = []

        # Add search courses list item
        list_item = xbmcgui.ListItem(label="Search Courses")
        url = '{0}?action=search&type={1}'.format(__url__, "course")
        is_folder = True
        listing.append((url, list_item, is_folder))

        # Add browse course categories list item
        # list_item = xbmcgui.ListItem(label="Browse Course Categories")
        # url = '{0}?action=list_categories_letters'.format(__url__)
        # is_folder = True
        # listing.append((url, list_item, is_folder))

        if self.api.logged_in:
            # Add my courses list item
            list_item = xbmcgui.ListItem(label="My Courses")
            url = '{0}?action=list_my_courses'.format(__url__)
            is_folder = True
            listing.append((url, list_item, is_folder))

        if self.api.logged_in:
            logged_in_text = "Logged in as " + self.api.user().name
        else:
            logged_in_text = "Not logged in"

        # Add the logged in status list item
        list_item = xbmcgui.ListItem(label=logged_in_text)
        url = ''
        is_folder = False
        listing.append((url, list_item, is_folder))

        if self.api.logged_in:
            list_item = xbmcgui.ListItem(label="Refresh login credentials")
            url = '{0}?action=refresh_login'.format(__url__)
            is_folder = False
            listing.append((url, list_item, is_folder))

        self.show_listing(listing)

    def list_courses(self, courses):
        """Show a list of courses given a list of course objects."""

        listing = []
        for course in courses:
            list_item = xbmcgui.ListItem(label=course.title, thumbnailImage=course.thumb_url)
            url = '{0}?action=list_course_chapters&course_id={1}'.format(__url__, course.course_id)
            is_folder = True
            list_item.setInfo("video", {"plot": course.description})
            listing.append((url, list_item, is_folder))

        self.show_listing(listing)

    def list_course_chapters(self, course_id):
        """Show the list of course chapters in the Kodi interface."""

        chapters = self.api.course_chapters(course_id)

        listing = []
        for chapter in chapters:
            list_item = xbmcgui.ListItem(label=chapter.title)
            url = '{0}?action=list_chapter_videos&course_id={1}&chapter_id={2}'.format(__url__, course_id, chapter.chapter_id)
            is_folder = True
            listing.append((url, list_item, is_folder))

        self.show_listing(listing)

    def list_chapter_videos(self, course_id, chapter_id):
        """Show a list of playable videos within a chapter in the Kodi interface."""

        videos = self.api.chapter_videos(course_id, chapter_id)

        listing = []
        for video in videos:
            list_item = xbmcgui.ListItem(label=video.title)
            is_folder = False
            if video.has_access:
                list_item.setProperty('IsPlayable', 'true')
                url = '{0}?action=play&course_id={1}&video_id={2}'.format(__url__, course_id, video.video_id)
            else:
                url = '{0}?action=show_access_error'.format(__url__)

            listing.append((url, list_item, is_folder))

        self.show_listing(listing)

    def show_access_error(self):
        xbmcgui.Dialog().ok(addonname, "Access error.", "You do not have access to this video. Please login to view this video.")

    def play_video(self, course_id, video_id):
        """Play a video by the provided (lynda.com) video ID."""

        path = self.api.video_url(course_id, video_id)
        play_item = xbmcgui.ListItem(path=path)
        # Play the video
        xbmcplugin.setResolvedUrl(__handle__, True, listitem=play_item)

    def search(self):
        keyboard = xbmc.Keyboard("", "Search", False)
        keyboard.doModal()
        if keyboard.isConfirmed() and keyboard.getText() != "":
            query = keyboard.getText()
            courses = self.api.course_search(query)
            self.list_courses(courses)

    def list_my_courses(self):
        courses = self.api.user_courses()
        self.list_courses(courses)

    def login(self, auth_type):
        if auth_type == "Normal Lynda.com Account":
            username = xbmcplugin.getSetting(__handle__, "username")
            password = xbmcplugin.getSetting(__handle__, "password")

            login_success = self.api.login_normal(username, password)

            if not login_success:
                xbmcgui.Dialog().ok(addonname, "Could not login.", "Please check your credentials are correct.")

    def refresh_login(self):
        """Deletes persisted cookies which forces a login attempt with current credentials"""

        s = requests.Session()
        empty_cookie_jar = s.cookies
        if util.save_data(addon, self.COOKIE_FILE_NAME, empty_cookie_jar):
            xbmcgui.Dialog().ok(addonname, "Cleared cookies. Please exit the addon and open it again.")
        else:
            xbmcgui.Dialog().ok(addonname, "Could not refresh lynda session cookies")

    def router(self, paramstring):
        """Router function that calls other functions depending on the provided paramstrings"""

        # Parse a URL-encoded paramstring to the dictionary of {<parameter>: <value>} elements
        params = dict(parse_qsl(paramstring[1:]))

        if params:
            # Cookiejar should definitely exist by now. Even if empty
            cookiejar = util.load_data(addon, self.COOKIE_FILE_NAME)
            self.api = LyndaApi(cookiejar)

            if params['action'] == 'search':
                self.search()
            elif params['action'] == 'list_course_chapters':
                self.list_course_chapters(int(params['course_id']))
            elif params['action'] == 'list_chapter_videos':
                self.list_chapter_videos(int(params['course_id']), int(params['chapter_id']))
            elif params['action'] == 'play':
                # Log the video as being played if user is logged in
                if self.api.logged_in:
                    self.api.log_video(int(params['video_id']))
                self.play_video(int(params['course_id']), int(params['video_id']))
            elif params['action'] == 'show_access_error':
                self.show_access_error()
            elif params['action'] == 'list_my_courses':
                self.list_my_courses()
            elif params['action'] == 'refresh_login':
                self.refresh_login()
        else:
            cookiejar = util.load_data(addon, self.COOKIE_FILE_NAME)
            if cookiejar:
                self.api = LyndaApi(cookiejar)
            else:
                self.api = LyndaApi()

            auth_type = xbmcplugin.getSetting(__handle__, "auth_type")

            # Try to log the user in if necessary
            if not self.api.logged_in and auth_type != 'None':
                self.login(auth_type)

            # Save cookie jar to disk so other screens in addon can resume session
            if not util.save_data(addon, self.COOKIE_FILE_NAME, self.api.get_cookies()):
                xbmcgui.Dialog().ok(addonname, "Could not save lynda session cookies")

            self.list_root_options()


if __name__ == '__main__':
    lynda_addon = LyndaAddon()

    # Call the router function and pass the plugin call parameters to it
    lynda_addon.router(sys.argv[2])
