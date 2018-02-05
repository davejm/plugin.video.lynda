# plugin.video.lynda

An XBMC / Kodi addon that allows the user to watch Lynda.com courses.

I made this plugin as there seemed to be a demand for it and it didn't exist. I use a Raspberry Pi running OpenElec (Kodi) at home and I wanted to be able to easily watch Lynda.com courses on the T.V.

# Installation

1. Download or clone this repository.
2. Copy the folder 'plugin.video.lynda' to your XBMC / Kodi addons directory (Linux is usually ~/.kodi/addons and Windows is usually somewhere in %APPDATA%\kodi\addons). If you are using Kodi on a RaspberryPi or a headless system, you should be able to SSH into the device and SCP/SFTP the folder over. There are plenty of instructions online for how to do this.
3. Configure the plugin settings (by right clicking/long pressing on the addon in Kodi) with your login credentials.

* Note that simply copying the folder to your addons will not cause Kodi to install some dependecies of this addon. You may have better luck zipping up the plugin.video.lynda folder and installing from zip on Kodi - installing from zip DOES trigger dependecy installation.

# Notes

- Supported login types: Regular Lynda.com accounts, Organisational accounts (including school accounts)*, IP Site license accounts

* See the notes below on how to login to organisational accounts.

# Logging into Organisational Accounts

Previously this addon attempted to parse the login forms of your organisation's sites. This caused a lot of problems.
To make this work properly for everyone, you now have to manually enter a valid login token.

1. Go to lynda.com and log in to your organisational account.
2. Copy the 'token' cookie value from Dev Tools. E.g. in Chrome, open Dev Tools with Ctrl+Shift+I. Go to the 'Application' tab. Select 'Cookies' in the sidebar and the lynda.com domain. Double click the value field of the 'token' cookie and copy it.
3. Create a file in this addons user data directory (you may want to have run the addon at least once to create this directory) called 'user_login_token' and paste the token value in the file. If your Kodi box is remote, you can do this via SSH. On Linux, the directory might be something like `/home/yourusername/.kodi/userdata/addon_data/plugin.video.lynda`.
4. In the Lynda.com addon settings make sure to select the 'Organisation' login type.
5. Start the addon. If it says you're not logged in, try exiting the addon and running it once again.
