"""
@author David Moodie
"""

import xbmcaddon
import xbmcgui
import xbmcplugin

import sys
from urlparse import parse_qsl
from urllib import urlencode

import resources.lib.requests as requests

import scrape
import auth
import util

addon = xbmcaddon.Addon()
addonname = addon.getAddonInfo('name')

# Get the plugin url in plugin:// notation.
__url__ = sys.argv[0]
# Get the plugin handle as an integer number.
__handle__ = int(sys.argv[1])


def list_root_options(name):
    """
    Create the list of root options in the Kodi interface.
    """

    # Create a list for our items.
    listing = []

    # Create a list item with a text label and a thumbnail image.
    list_item = xbmcgui.ListItem(label="Search Courses")

    # Create a URL for the plugin recursive callback.
    # Example: plugin://plugin.video.example/?action=listing&category=Animals
    url = '{0}?action=search&type={1}'.format(__url__, "course")

    # is_folder = True means that this item opens a sub-list of lower level items.
    is_folder = True

    # Add our item to the listing as a 3-element tuple.
    listing.append((url, list_item, is_folder))

    # Create a list item with a text label and a thumbnail image.
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

    # Add our listing to Kodi.
    # Large lists and/or slower systems benefit from adding all items at once
    # via addDirectoryItems instead of adding one by ove via addDirectoryItem.
    xbmcplugin.addDirectoryItems(__handle__, listing, len(listing))
    # Add a sort method for the virtual folder items (alphabetically,
    # ignore articles)
    # xbmcplugin.addSortMethod(__handle__, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(__handle__)


def list_course_chapters(s, courseId):
    """
    Create the list of playable course chapters in the Kodi interface.
    """

    course = scrape.get_course(s, courseId)
    chapters = course['Chapters']

    listing = []
    for i, chapter in enumerate(chapters):
        list_item = xbmcgui.ListItem(label=chapter['Title'])
        url = '{0}?action=list_course_chapter_videos&courseId={1}&chapterIndex={2}'.format(__url__, courseId, i)
        is_folder = True
        listing.append((url, list_item, is_folder))

    xbmcplugin.addDirectoryItems(__handle__, listing, len(listing))
    xbmcplugin.endOfDirectory(__handle__)


def list_course_chapter_videos(s, courseId, chapterIndex):
    """
    Create the list of playable videos within a chapter in the Kodi interface.
    """

    course = scrape.get_course(s, courseId)
    chapters = course['Chapters']

    videos = []
    chapter = chapters[int(chapterIndex)]

    for video in chapter['Videos']:
        title = video['Title']
        videoId = video['ID']
        v = {"title": title, "videoId": videoId}
        videos.append(v)

    listing = []
    for video in videos:
        list_item = xbmcgui.ListItem(label=video['title'])
        list_item.setProperty('IsPlayable', 'true')
        url = '{0}?action=play&videoId={1}'.format(__url__, video['videoId'])
        is_folder = False
        listing.append((url, list_item, is_folder))

    xbmcplugin.addDirectoryItems(__handle__, listing, len(listing))
    xbmcplugin.endOfDirectory(__handle__)


def play_video(s, videoId):
    """
    Play a video by the provided (lynda.com) video ID.
    """

    path = scrape.get_video(s, videoId)

    if path == "":
        xbmcgui.Dialog().ok(addonname, "Could not find a video source. Unexpected JSON structure.", "You may need to be logged in to view this.")
    else:
        # Create a playable item with a path to play.
        play_item = xbmcgui.ListItem(path=path)
        # Pass the item to the Kodi player.
        xbmcplugin.setResolvedUrl(__handle__, True, listitem=play_item)


def list_courses(s, courses):
    """
    Create a list of courses given a list of course objects.
    """

    listing = []
    for course in courses:
        title = course['title']
        courseId = course['courseId']

        thumbURL = course['thumbURL']

        shortDesc = course['shortDesc']

        list_item = xbmcgui.ListItem(label=title, label2="Test", thumbnailImage=thumbURL)
        url = '{0}?action=list_course_chapters&courseId={1}'.format(__url__, courseId)
        is_folder = True
        list_item.setInfo("video", {"plot": shortDesc})

        listing.append((url, list_item, is_folder))

    #xbmcgui.Dialog().ok(addonname, thumbURL) # DEBGUG

    xbmcplugin.addDirectoryItems(__handle__, listing, len(listing))
    xbmcplugin.endOfDirectory(__handle__)


def list_categories_letters(s):
    """
    Create the list of video categories' first letters in the Kodi interface.
    """

    categories_letters = scrape.get_categories_letters(s)
    listing = []

    for letter in categories_letters:
        list_item = xbmcgui.ListItem(label=letter)
        url = '{0}?action=list_category_letter_contents&letter={1}'.format(__url__, letter)
        is_folder = True
        listing.append((url, list_item, is_folder))

    xbmcplugin.addDirectoryItems(__handle__, listing, len(listing))
    xbmcplugin.endOfDirectory(__handle__)


def list_category_letter_contents(s, letter):
    """
    Creates a list of the contents of a chosen letter in the Kodi interface.
    """

    softwares = scrape.get_category_letter_software(s, letter)
    listing = []

    for software in softwares:
        list_item = xbmcgui.ListItem(label=software['name'])
        url = '{0}?action=list_category_courses&{1}'.format(__url__, urlencode({"link": software['link']}))
        is_folder = True
        listing.append((url, list_item, is_folder))

    xbmcplugin.addDirectoryItems(__handle__, listing, len(listing))
    xbmcplugin.endOfDirectory(__handle__)


def router(paramstring):
    """
    Router function that calls other functions depending on the provided
    paramstrings
    """

    # Parse a URL-encoded paramstring to the dictionary of
    # {<parameter>: <value>} elements
    params = dict(parse_qsl(paramstring[1:]))

    # Check the parameters passed to the plugin
    if params:
        s = util.load_data(addon, "lynda_session")
        if s == False:
            xbmcgui.Dialog().ok(addonname, "Could not load session data")
            return

        if params['action'] == 'search':
            keyboard = xbmc.Keyboard("", "Search", False)
            keyboard.doModal()
            if keyboard.isConfirmed() and keyboard.getText() != "":
                query = keyboard.getText()
                # xbmcgui.Dialog().ok(addonname, query)
                courses = scrape.course_search(s, query)
                list_courses(s, courses)

        elif params['action'] == 'list_my_courses':
            courses = scrape.get_my_courses(s)
            list_courses(s, courses)

        elif params['action'] == 'list_categories_letters':
            list_categories_letters(s)

        elif params['action'] == 'list_category_letter_contents':
            list_category_letter_contents(s, params['letter'])

        elif params['action'] == 'list_category_courses':
            link = params['link']
            courses = scrape.courses_for_category(s, link)
            list_courses(s, courses)

        elif params['action'] == 'list_course_chapters':
            list_course_chapters(s, params['courseId'])

        elif params['action'] == 'list_course_chapter_videos':
            list_course_chapter_videos(s, params['courseId'], params['chapterIndex'])

        elif params['action'] == 'play':
            # Play a video from a provided URL.
            play_video(s, params['videoId'])
    else:
        s = auth.initSession()
        name = None

        auth_type = xbmcplugin.getSetting(__handle__, "auth_type")
        if auth_type == "Organisation":
            username = xbmcplugin.getSetting(__handle__, "username")
            password = xbmcplugin.getSetting(__handle__, "password")
            org_url = xbmcplugin.getSetting(__handle__, "org_url")
            DEBUG = xbmcplugin.getSetting(__handle__, "debug")
            if DEBUG == 'false':
                DEBUG = False
            else:
                DEBUG = True
            print("DEBUG VAR: ", DEBUG)

            ret = auth.org_login(s,
                                 username=username,
                                 password=password,
                                 orgURL=org_url,
                                 LDEBUG=DEBUG)

            if ret != False:
                name = ret
            else:
                xbmcgui.Dialog().ok(addonname,
                                    "Could not login.",
                                    "Please check your credentials are correct.")

        if not util.save_data(addon, "lynda_session", s):
            xbmcgui.Dialog().ok(addonname, "Could not save requests session")

        list_root_options(name)

if __name__ == '__main__':
    # Call the router function and pass the plugin call parameters to it.
    router(sys.argv[2])
