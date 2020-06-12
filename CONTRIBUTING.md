Contributing and Development
============================
This is a quick guide on how to develop and contribute to this project

## Dependencies
Make sure you can run these commands and install them if not present.
* python3
* pip3 (packaged as python3-pip)


## Get a Discord bot token
* Go to https://discordapp.com/developers/applications (log in if needed)
* Create an application (name doesn't matter)
* Click "Bot" it the left sidebar
* Create a bot
  * The bot's name will be what users see in servers
  * Changing the bot's name changes the BotToken
* Make note of the token on this page (later refered to as BotToken)


## Join the test server
[Click here to join the server](https://discord.gg/4xwKBs)
ping @Jayy#6249 for permissions to add bots


## Prepare bot for connecting to discord server
* Click "OAuth2" in the left sidebar
* In the "scopes" section, check `bot`
* In the "bot permissions" section, check `Administrator`
* Copy the link from the "scopes" section and open in a new tab/window
* Select the test server to add the bot to
* Confirm you want to give the bot Administrator permissions


## Prepare the Repo
* Fork this repo
* `git clone` your fork to wherever you want to work on this bot
* Rename `BotSecrets.json.template` to `BotSecrets.json`
* Copy/paste the token from the Discord page into the `BotToken` empty string
* Create a database name (Whatever you want it doesnt matter)


## Setting up the build environment
Setup a virtual environment:  
`pip3 install virtualenv`
`virtualenv venv`

Enter the virtualenv with:  
`source venv/bin/activate`

Then allow pip to get the latest libraries:  
`pip3 install -r requirements.txt`

You can then test-run the bot with the command:  
`python3 -m bot` 
when you are in the root directory `ClemBot/`

The bot should show up in the test server and respond to commands (test with `:hello`)
