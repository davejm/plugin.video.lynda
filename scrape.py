"""
@author: David Moodie
"""

import requests
from resources.lib.parsedom import parseDOM as pd
from resources.lib.parsedom import stripTags

import time

from xbmc import log


def get_video(s, videoId):
    unix_milli = int(round(time.time() * 1000))
    #payload = {"videoId": test_video_id,
    #           "courseId": test_course_id,
    #           "type": "video", "_": unix_milli}
    payload = {
        "videoId": videoId,
        "type": "video",
        "_": unix_milli
    }
    r = s.get("http://www.lynda.com/ajax/player", params=payload)
    data = r.json()
    # print(data)
    video_url = ""

    try:
        video_qualities = data['PrioritizedStreams']["0"]
        if "PrioritizedStreams" in data:
            if "720" in video_qualities:
                video_url = video_qualities["720"]
            elif "540" in video_qualities:
                video_url = video_qualities["540"]
            elif "360" in video_qualities:
                video_url = video_qualities["360"]
            else:
                print("Could not find a video source")
    except:
        print("Could not find a video source. Unexpected JSON structure")

    return video_url


def get_course(s, courseId):
    # test_course_id = 86005
    unix_milli = int(round(time.time() * 1000))
    payload = {
        "courseId": courseId,
        "type": "course",
        "_": unix_milli
    }
    r = s.get("http://www.lynda.com/ajax/player", params=payload)
    # print(r.text)
    data = r.json()
    return data


def course_search(s, query):
    url = "http://www.lynda.com/search"
    payload = {"q": query,
               "f": "producttypeid:2"}
    r = s.get(url, params=payload)
    page_html = r.text

    return parse_course_lists(page_html)

def parse_course_lists(html, is_text_search=True):
    """Takes the page html with the list of courses and returns a list of course objects (dicts)"""

    if is_text_search:
        ul_id = "search-results-list"
        course_class = "card card-list-style search-result course"
        description_class = "meta-description hidden-xs"
        title_el = "h2"
    else:
        ul_id = "category-courses"
        course_class = "card card-list-style course"
        description_class = "meta-description hidden-xs dot-ellipsis dot-resize-update"
        title_el = "h3"

    courselist = pd(html, "ul", attrs={"id": ul_id})
    # log("<<<<<<<<<<<<<<<<<DEBUG>>>>>>>>>>>>>>>>>>>>")
    # log(repr(courselist))
    courses = pd(courselist, "li")
    course_list = []

    for i, course in enumerate(courses):
        search_result = pd(course, "div", attrs={"class": course_class}, ret="id")
        if len(search_result) == 0: continue

        title = stripTags(pd(course, title_el)[0])
        courseId = search_result[0]

        thumbnail_el = pd(course, "div", attrs={"class": "thumbnail"})[0]
        thumbURL = pd(thumbnail_el, "img", ret="data-lazy-src")[0]
        shortDesc = stripTags(pd(course, "div", attrs={"class": description_class})[0]).strip()

        c = {
            "title": title,
            "courseId": courseId,
            "thumbURL": thumbURL,
            "shortDesc": shortDesc
        }

        # log(str(c))

        course_list.append(c)

    return course_list


def get_categories_letters(s):
    r = s.get("http://www.lynda.com/subject/all")
    letters_html = pd(r.text, "div", attrs={"class": "letter"})
    # print(len(letters))
    letter_list = []
    for letter in letters_html:
        letter_name = pd(letter, "h3")[0]
        letter_list.append(letter_name)

    return letter_list


def get_category_letter_software(s, search_letter):
    r = s.get("http://www.lynda.com/subject/all")
    letters_html = pd(r.text, "div", attrs={"class": "letter"})

    softwares = []

    for letter in letters_html:
        letter_name = pd(letter, "h3")[0]
        if letter_name == search_letter:
            softwares_html = pd(letter, "div", attrs={"class": "software-name"})
            for software_html in softwares_html:
                software_name = pd(software_html, "a")[0]
                link = pd(software_html, "a", ret="href")[0]
                if link[0] == "/":
                    link = "http://www.lynda.com" + link
                num_courses, software_name = software_name.split("<span>")[1].split("</span>")
                softwares.append({"name": software_name + " " + num_courses,
                                 "link": link})
            break

    return softwares


def courses_for_category(s, link):
    r = s.get(link)
    page_html = r.text
    return parse_course_lists(page_html, False)


def get_my_courses(s):
    my_courses_url = "http://www.lynda.com/CourseHistory"
    r = s.get(my_courses_url)

    courses_html = pd(r.text, "div", attrs={"class": "row_course"})
    course_list = []
    for course_html in courses_html:
        col_course = pd(course_html, "div", attrs={"class": "col_course"})
        courseId = pd(col_course, "a", ret="data-course")[0]

        title = pd(col_course, "a")[1].strip()
        thumbURL = None
        shortDesc = ""

        c = {
            "title": title,
            "courseId": courseId,
            "thumbURL": thumbURL,
            "shortDesc": shortDesc
        }
        course_list.append(c)

    return course_list
