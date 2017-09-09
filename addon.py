import xbmcaddon
import xbmcgui
import xbmcplugin

import sys
from urlparse import parse_qsl
from urllib import urlencode

import requests

from resources.lib.lynda_api import LyndaApi

addon = xbmcaddon.Addon()
addonname = addon.getAddonInfo('name')

# Get the plugin url in plugin:// notation.
__url__ = sys.argv[0]
# Get the plugin handle as an integer number.
__handle__ = int(sys.argv[1])

__version__ = addon.getAddonInfo("version")

class LyndaAddon:
    def __init__(self):
        self.api = LyndaApi()

    def show_listing(self, listing):
        """Show a listing on the screen."""

        xbmcplugin.addDirectoryItems(__handle__, listing, len(listing))
        xbmcplugin.endOfDirectory(__handle__)


    def list_root_options(self, name):
        """Create the list of root options in the Kodi interface."""

        listing = []
        list_item = xbmcgui.ListItem(label="Search Courses")
        url = '{0}?action=search&type={1}'.format(__url__, "course")
        is_folder = True
        listing.append((url, list_item, is_folder))

        list_item = xbmcgui.ListItem(label="Browse Course Categories")
        url = '{0}?action=list_categories_letters'.format(__url__)
        is_folder = True
        listing.append((url, list_item, is_folder))

        if name is None:
            logged_in = "Not logged in"
        else:
            list_item = xbmcgui.ListItem(label="My Courses")
            url = '{0}?action=list_my_courses'.format(__url__)
            is_folder = True
            listing.append((url, list_item, is_folder))

            logged_in = "Logged in as " + name

        list_item = xbmcgui.ListItem(label=logged_in)
        url = ''
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
            url = '{0}?action=list_course_chapter_videos&course_id={1}&chapter_id={2}'.format(__url__, course_id, chapter.chapter_id)
            is_folder = True
            listing.append((url, list_item, is_folder))

        self.show_listing(listing)


    def search(self):
        keyboard = xbmc.Keyboard("", "Search", False)
        keyboard.doModal()
        if keyboard.isConfirmed() and keyboard.getText() != "":
            query = keyboard.getText()
            courses = self.api.course_search(query)
            self.list_courses(courses)


    def router(self, paramstring):
        """
        Router function that calls other functions depending on the provided
        paramstrings
        """

        # Parse a URL-encoded paramstring to the dictionary of
        # {<parameter>: <value>} elements
        params = dict(parse_qsl(paramstring[1:]))

        if params:
            if params['action'] == 'search':
                self.search()
            elif params['action'] == 'list_course_chapters':
                self.list_course_chapters(params['course_id'])
        else:
            name = None
            self.list_root_options(name)


if __name__ == '__main__':
    lynda_addon = LyndaAddon()

    # Call the router function and pass the plugin call parameters to it
    lynda_addon.router(sys.argv[2])
