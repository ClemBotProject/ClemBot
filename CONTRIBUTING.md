Contributing and Development
============================
This is a guide on how to develop and contribute to this project

## Dependencies
Make sure you can run these commands and install them if not present.
### ClemBot.Bot
* Python 3.8 or higher [Link](https://www.python.org/downloads/release/python-380/)
* pip3 (packaged as python3-pip) 
* A python IDE/Text Editor: Anything will work but people generally use Visual Studio Code [Link](https://code.visualstudio.com/) or Jetbrains Pycharm [Link](https://www.jetbrains.com/pycharm/)

### ClemBot.Api
* .Net 5 SDK [Link](https://dotnet.microsoft.com/download/dotnet/5.0)
* A C# IDE, Preferably [Visual Studio Community](https://visualstudio.microsoft.com/) (Windows only) or [Jetbrains Rider](https://www.jetbrains.com/rider/) (Cross Platform, Free with a student email)

### Database
* PostgresSQL [Link](https://www.postgresql.org/download/)
* PgAdmin4 [Link](https://www.pgadmin.org/download/)

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

## Prepare your ClemBot.Api config variables
ClemBot.Api uses `dotnet user-secrets` [Docs](https://docs.microsoft.com/en-us/aspnet/core/security/app-secrets?view=aspnetcore-5.0) to securely store sensitive values like db connection strings and api keys

* After you have started up and configured PostgresSQL with your desired username and password you need to set the Connection string for ClemBot.Api
* `cd` into ClemBot/ClemBot.Api/ClemBot.Api.Core
* Run `dotnet user-secrets set "ClemBotConectionString" "YourConnectionSttring"` (Example:  "Server=127.0.0.1;Port=5432;Database=clembotdb;User Id=XXXXX;Password=XXXXX;")
* Generate a `BotApiKey` with this website [Link](https://www.allkeysgenerator.com/Random/Security-Encryption-Key-Generator.aspx)
* Run `dotnet user-secrets set "BotApiKey" "KeyYouGeneratedAbove"`

## Prepare your ClemBot.Bot config variables
* Copy `BotSecrets.json.template` and rename that copy to `BotSecrets.json`
* Copy/paste the token from the Discord page into the `BotToken` empty string
* Make the `ApiUrl` row `https://localhost:5001/`
* Copy and paste the ClemBot.Api key value that you generated above into the `ApiKey` row
* Copy and paste the channel Ids of the channels in the test server that you want to use for Connection Status updates and Error Logging into the `ErrorLogChannelIds` and `StartupLogChannelIds`. If you dont want this. Leave the field as an empty brackets, []
* Set a custom bot prefix in the `BotPrefix` field that will invoke your commands 

### All Config Variables

* `BotToken`:(Required) Your discord bots api access token
* `ApiUrl`:(Required) Url of the ClemBot.Api ASP.Net endpoints (defaults to http://localhost:5001)
* `ApiKey`:(Required) Access key for the bot endpoints in ClemBot.Api
* `ClientToken`:(Optional) Used for the Website Frontend, can be ignored if you are not working on that
* `ClientSecret`:(Optional) Used for the Website Frontend, can be ignored if you are not working on that
* `BotPrefix`:(Required) Your discord bots prefix that it will default to responding too
* `StartupLogChannelIds`:(Optional) The Id of the channel for the bot to send startup events too
* `ErrorLogChannelIds`:(Optional) The Id of the channel for the bot to send error events too (recommended if you are doing work with services
* `GifMeToken`:(Optional) GifMe api token
* `ReplUrl`:(Optional) The url of the Snekbox container that allows for sandboxed evals
* `GitHubSourceUrl`:(Optional) Url that the !source command uses to link source code
* `MerriamKey`:(Optional) Merriam api token
* `WeatherKey`:(Optional) Weather forecast api token
* `GeocodeKey`:(Optional) Geocode weather service api token
* `AzureTranslateKey`:(Optional) Azure translation api token
* `BotOnly`: (optional) Puts ClemBot.Bot into Bot only mode which deactivates the api and allows for limited functionality. Mainly used when a feature only requires discord and needs no persistence/database

## Setting up the ClemBot.Bot build environment
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

## Setting up the ClemBot.Api build environment

* Open the `ClemBot.Api.sln` file in the `ClemBot/ClemBot.Api` folder to open the project in either Visual Studio or Rider
* Click the run button in your preferred IDE

## Final Notes
The ClemBot.Api and the ClemBot.Bot projects talk to eachother over http, both projects need to be run simultaneasouly if you are not working in BotOnly mode.
