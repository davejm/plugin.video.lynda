"""
@author: David Moodie
"""

import resources.lib.requests as requests
from resources.lib.parsedom import parseDOM as pd
from resources.lib.parsedom import stripTags

from xbmc import log

import json

DEBUG = False


def dbg(*strings):
    global DEBUG
    if DEBUG:
        str = ', '.join(strings)
        print("DEBUG: " + str)


def getForm(html, formIndex=0):
    formObj = {}
    form = pd(html, "form")[formIndex]
    try:
        formObj['action'] = pd(html, "form", ret="action")[0]  # TODO: Use indexed form html
    except:
        formObj['action'] = None

    inputs_html = pd(form, "input")
    input_types = pd(form, "input", ret="type")
    input_values = pd(form, "input", ret="value")
    input_names = pd(form, "input", ret="name")

    formObj['input_types'] = input_types
    formObj['input_values'] = input_values
    formObj['input_names'] = input_names

    return formObj


def getName(html):
    # Tested on members page
    try:
        drop_menu = pd(html, "span", attrs={"data-qa": "eyebrow_account_menu"})[0]
        name = stripTags(drop_menu)[3:]
    except:
        name = "Can't get name"
    return name


def initSession():
    s = requests.Session()
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36"}
    s.headers.update(headers)

    return s


def org_login(s, username, password, orgURL, LDEBUG=False):
    global DEBUG
    DEBUG = LDEBUG

    # Set initial cookies
    init = s.get("http://www.lynda.com/signin/organization")

    # Get the lynda javascript var from page and parse out the auth key needed
    # for ajax request header
    lyndaVar = init.text.split("var lynda = ")[1].split(";")[0]
    lyndaVarJSON = json.loads(lyndaVar)
    weirdAuthKey = lyndaVarJSON['-_-']

    ShibCasLoginByOrg = "https://www.lynda.com/ajax/signin/organization"

    payload = {"org": orgURL}

    r = s.post(ShibCasLoginByOrg, data=payload, headers={"-_-": weirdAuthKey})
    # log(r.text)

    try:
        portalURL = r.json()['AuthUrl']
    except:
        portalURL = r.json()['RedirectUrl']

    # log("r portalURL")
    # log(portalURL)
    r2 = s.get(portalURL)  # GET the 'portal' (org) login page
    login_form = getForm(r2.text)
    doneUsername = False

    for i, inp in enumerate(login_form['input_names']):
        if login_form['input_types'][i] != "hidden" and login_form['input_values'][i] == "":
            # Assume username and password
            if doneUsername is False:
                login_form['input_values'][i] = username
                doneUsername = True
            else:
                login_form['input_values'][i] = password
    # print(login_form['input_values'])

    if login_form['action'][0] == "/":
        postURL = "/".join(r2.url.split("/")[:3]) + login_form['action']
    else:
        postURL = login_form['action']
    # log("r2 postURL")
    # log(postURL)

    payload = {}
    for i in range(len(login_form['input_names'])):
        payload[login_form['input_names'][i]] = login_form['input_values'][i]
    # log(str(payload))

    # Assuming login form uses post method. Account for this if time
    r3 = s.post(postURL, data=payload)  # Attempt to login to institution
    saml_html = r3.text
    saml_form = getForm(saml_html)

    if saml_form['action'][0] == "/":
        postURL = "/".join(r2.url.split("/")[:3]) + saml_form['action']
    else:
        postURL = saml_form['action']
    # log("saml postURL")
    # log(postURL)

    payload = {}
    for i in range(len(saml_form['input_names'])):
        payload[saml_form['input_names'][i]] = saml_form['input_values'][i]
    # print(payload)

    try:
        # Post the SAML form (still on institutions site). Response URL should
        # be on Lynda (possibly https://shib.lynda.com/InCommon)
        r4 = s.post(postURL, data=payload)
    except:
        return False

    # Now deal with the shib integration 'InCommon' form on Lynda to finalise
    # login
    shib_int_html = r4.text
    shib_form = getForm(shib_int_html)

    if shib_form['action'][0] == "/":
        postURL = "/".join(r2.url.split("/")[:3]) + shib_form['action']
    else:
        postURL = shib_form['action']
    # log("shib postURL")
    # log(postURL)

    payload = {}
    for i in range(len(shib_form['input_names'])):
        payload[shib_form['input_names'][i]] = shib_form['input_values'][i]

    r5 = s.post(postURL, data=payload)
    # log("r5 url")
    # log(r5.url)

    if r5.url != 'http://www.lynda.com/member' and r5.url != 'https://www.lynda.com/member' and r5.url != 'https://www.lynda.com/':
        return False
    else:
        name = getName(r5.text)
        return name


def library_login(s, libCardNum, libCardPin, orgDomain, LDEBUG=False):
    global DEBUG
    DEBUG = LDEBUG

    libraryLoginURL = "https://www.lynda.com/portal/sip"

    payload = {
        "org": orgDomain
    }

    r = s.get(libraryLoginURL, params=payload)
    # log(str(r))
    # log(r.text)
    # log("lib login url: " + r.url)

    form = pd(r.text, "form")[1]
    seasurf_sec_token = pd(form, "input", attrs={"name": "seasurf"}, ret="value")[0].encode("utf-8")
    payload = {
        "libraryCardNumber": libCardNum,
        "libraryCardPin": libCardPin,
        "libraryCardPasswordVerify": "",
        "org": orgDomain,
        "seasurf": seasurf_sec_token
    }
    # from pprint import pformat
    # log(pformat(payload))

    r2 = s.post(libraryLoginURL + '?org=' + orgDomain, data=payload)
    # log("lib login post url: " + r2.url)
    if r2.url != 'http://www.lynda.com/member' and r2.url != 'https://www.lynda.com/member' and r2.url != 'https://www.lynda.com/':
        return False
    else:
        name = getName(r2.text)
        return name
