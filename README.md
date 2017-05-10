# plugin.video.lynda
An XBMC / Kodi addon that allows the user to watch Lynda.com courses.

I made this plugin as there seemed to be a demand for it and it didn't exist. I use a Raspberry Pi running OpenElec (Kodi) at home and I wanted to be able to easily watch Lynda.com courses on the T.V.

# Installation

1. Download or clone this repository.
2. Copy the folder 'plugin.video.lynda' to your XBMC / Kodi addons directory (Linux is usually ~/.kodi/addons and Windows is usually somewhere in %APPDATA%\kodi\addons). If you are using Kodi on a RaspberryPi or a headless system, you should be able to SSH into the device and SCP/SFTP the folder over. There are plenty of instructions online for how to do this.
3. Configure the plugin settings (by right clicking/long pressing on the addon in Kodi) with your login credentials.

# Notes

- Supported login types: Regular Lynda.com accounts, Library Accounts, Organisational Accounts

- Currently, some of the lists of items returned by the parser are quite long as I haven't implemented any form of pagination yet. I may do this in the future.
