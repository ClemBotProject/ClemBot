Contributing and Development
============================
This is a quick guide on how to develop and contribute to this project

## Dependencies
Make sure you can run these commands and install them if not present.
* Python 3.8 or higher
* pip3 (packaged as python3-pip)


## Get a Discord bot token and enable intents
* Go to https://discordapp.com/developers/applications (log in if needed)
* Create an application (name doesn't matter)
* Click "Bot" it the left sidebar
* Create a bot
  * The bot's name will be what users see in servers
  * Changing the bot's name changes the BotToken
* Make note of the token on this page (later refered to as BotToken)
* Enable Discord member intents ![Intents](https://i.postimg.cc/hhWy9N7W/Screen-Shot-2020-11-06-at-10-30-25-AM.png)


## Join the test server
[Click here to join the server](https://discord.gg/FACu8k4)
ping @Jayy#6249 for permissions to add bots


## Prepare bot for connecting to discord server
* Click "OAuth2" in the left sidebar
* In the "scopes" section, check `bot`
* In the "bot permissions" section, check the following boxes [![perms](https://i.postimg.cc/NFkdvDCY/perms.png)](https://postimg.cc/xNqvKvSF)
* Copy the link from the "scopes" section and open in a new tab/window
* Select the test server to add the bot to

## Prepare the Repo
* Fork this repo
* `git clone` your fork to wherever you want to work on this bot
* Copy `BotSecrets.json.template` and rename that copy to `BotSecrets.json`
* Copy/paste the token from the Discord page into the `BotToken` empty string
* Create a database name (Whatever you want it doesnt matter)
* Set a custom bot prefix that will invoke your commands 


## Setting up the build environment
Setup a virtual environment:  
`pip3 install virtualenv` windows: `py -m pip install --user virtualenv`

`virtualenv venv`  windows: `py -m venv venv`

Enter the virtualenv with:  
`source venv/bin/activate` windows: `source .\env\Scripts\activate`

Then allow pip to get the latest libraries:  
`pip3 install -r requirements.txt` windows: `py -m pip install -r requirements.txt`

You can then test-run the bot with the command:  
`python3 -m bot`  windows: `py -m bot`
when you are in the root directory `ClemBot/`

The bot should show up in the test server and respond to commands (test with `<your_prefix>hello`)
