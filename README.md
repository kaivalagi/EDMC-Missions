# ED Market Connector - Missions Plugin
This is a plugin for [Elite Dangerous Market Connector](https://github.com/EDCD/EDMarketConnector).

Its purpose is to help you keep track of accepted missions in the game "Elite Dangerous", currently supporting (and still testing) collect, courier, massacre and mining missions.

It has heavily "borrowed" from the EDMC-Massacres plugin and it's excellent mission repository / store backend to support loading past journal data for complete mission details.

The Massacre plugin can be found here: https://github.com/CMDR-WDX/EDMC-Massacres

## Usage

- Extract the plugin zip contents into %USERPROFILE%\AppData\Local\EDMarketConnector\plugins
- Start EDMC and then Elite Dangerous to establish the mission data successfully, if not done this way Elite Dangerous will need reloading back through main menu.
- Once correctly initialised any mission events will be captured and your mission stack reflected through EDMC via one of 4 tabs on display

### Version Checks
On startup the plugin gets the latest version numbe from github and compares it to your install. If there is a newer version details will be displayed with an option to go to the release page to download or to dismiss the information.
The plugin settings has an option "Check for Updates on Start"where this can be turned on/off.

### Journal Files
Because EDMC does not keep track of Missions the plugin will by default read through the last 2 weeks of logs on startup
and collect all Mission-Events. There is a setting called "Journal Weeks" where the number of weeks to ue can be changed if needed.


