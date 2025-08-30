Contributing and Development
============================
This is a guide on how to develop and contribute to this project

## Dependencies

Make sure you can run these commands and install them if not present.

### ClemBot.Bot

* [Python 3.13](https://www.python.org/downloads/release/python-3130/)
* pip3 (packaged as python3-pip)
* A Python IDE
    * Anything will work, but people generally use [Visual Studio Code](https://code.visualstudio.com/)
      or [JetBrains PyCharm](https://www.jetbrains.com/pycharm/).

### ClemBot.Api

* [.Net 7 SDK](https://dotnet.microsoft.com/download/dotnet/7.0)
* A C# IDE
  * Preferably [Visual Studio Community](https://visualstudio.microsoft.com/) (Windows only)
  or [JetBrains Rider](https://www.jetbrains.com/rider/) (cross-platform, free with a student email)

### ClemBot.Site

* [nvm](https://github.com/nvm-sh/nvm#installing-and-updating)
* [yarn](https://classic.yarnpkg.com/lang/en/docs/install/#windows-stable) (Find your operating system in the
  dropdown)

### Database

* [PostgreSQL 16](https://www.postgresql.org/download/)
* [PgAdmin4](https://www.pgadmin.org/download/)

## Get a Discord bot token and enable intents

* Go to https://discordapp.com/developers/applications (log in if needed)
* Create an application (name doesn't matter)
* Click "Bot" in the left sidebar
* Create a bot
    * The bot's name will be what users see in servers
    * Changing the bot's name changes the BotToken
* Make note of the token on this page (later referred to as BotToken)
* Enable Discord member intents ![Intents](https://i.postimg.cc/hhWy9N7W/Screen-Shot-2020-11-06-at-10-30-25-AM.png)

## Join the test server

[Click here to join the server](https://discord.gg/FACu8k4)
ping @Jayy#6249 for permissions to add bots

## Prepare bot for connecting to discord server

* Click "OAuth2" in the left sidebar
* In the "scopes" section, check `bot`
* In the "bot permissions" section, check the following
  boxes [![perms](https://i.postimg.cc/NFkdvDCY/perms.png)](https://postimg.cc/xNqvKvSF)
* Copy the link from the "scopes" section and open in a new tab/window
* Select the test server to add the bot to

## Prepare the Repo

* Fork this repo
* `git clone` your fork to wherever you want to work on this bot

## Prepare your ClemBot.Api config variables

ClemBot.Api
uses `dotnet user-secrets` ([documentation](https://docs.microsoft.com/en-us/aspnet/core/security/app-secrets?view=aspnetcore-5.0))
to securely store sensitive values like database connection strings and API keys. After you have started up and
configured PostgreSQL with your desired username and password, you need to set the connection string for ClemBot.Api:

* `cd` into `ClemBot/ClemBot.Api/ClemBot.Api.Core`
* Run `dotnet user-secrets set "ClemBotConnectionString" "YourConnectionString"`
    * Example connection string: `Server=127.0.0.1;Port=5432;Database=clembotdb;User Id=XXXXX;Password=XXXXX;`
* Generate a `BotApiKey`
  with [this website](https://www.allkeysgenerator.com/Random/Security-Encryption-Key-Generator.aspx).
* Run `dotnet user-secrets set "BotApiKey" "KeyYouGeneratedAbove"`

## Prepare your ClemBot.Bot config variables

* Copy `BotSecrets.json.template` and rename that copy to `BotSecrets.json`
* Copy/paste the token from the Discord page into the `BotToken` empty string
* Make the `ApiUrl` row `https://localhost:5001/`
* Copy and paste the ClemBot.Api key value that you generated above into the `ApiKey` row
* Copy and paste the channel IDs of the channels in the test server that you want to use for Connection Status updates
  and Error Logging into the `ErrorLogChannelIds` and `StartupLogChannelIds`. If you don't want this, leave the field as
  empty brackets, like so: `[]`
* Set a custom bot prefix in the `BotPrefix` field that will invoke your commands

### All Config Variables

| Name                   | Type        | Required | Project | Description                                                                                                |
|------------------------|-------------|----------|---------|------------------------------------------------------------------------------------------------------------|
| `BotToken`             | `str`       | Yes      | Bot     | Used to log into the bot account.                                                                          |
| `ApiUrl`               | `str`       | Yes      | API     | URL of the API endpoints (defaults to `http://localhost:5001/`)                                            |
| `ApiKey`               | `str`       | Yes      | API     | Access key for the bot endpoints in the API.                                                               |
| `ClientToken`          | `str`       | No       | Site    | Used for the website.                                                                                      |
| `ClientSecret`         | `str`       | No       | Site    | Used for the website.                                                                                      |
| `BotPrefix`            | `str`       | Yes      | Bot     | The prefix your bot will respond to.                                                                       |
| `SiteUrl`              | `str`       | No       | Bot     | The URL of your local site or hosted instance for the bot to link to.                                      |
| `StartupLogChannelIds` | `list[int]` | No       | Bot     | The IDs of the channels for the bot to send start-up/shutdown events to.                                   |
| `ErrorLogChannelIds`   | `list[int]` | No       | Bot     | The IDs of the channels for the bot to send error events to.                                               |
| `ReplUrl`              | `str`       | No       | Bot     | The URL of the Snekbox container.                                                                          |
| `GitHubSourceUrl`      | `str`       | No       | Bot     | The URL that the `!source` command uses to link to source.                                                 |
| `BotOnly`              | `bool`      | No       | Bot     | If set to `true`, ClemBot.Bot operates without ClemBot.Api (with limited functionality).                   |
| `AllowBotInputIds`     | `list[int]` | No       | Bot     | The IDs of Discord bots that are allowed to run ClemBot commands.                                          |
| `MessageApiBatchSize`  | `int`       | No       | API     | The max cache size for ClemBot's internal message catch before it is flushed to the API (defaults to `5`). | 

## Setting up the ClemBot.Bot build environment

Installing uv:  
`pip3 install uv` (Windows: `py -m pip install uv`)

Installing dependencies with uv:
`uv sync`

You can then test-run the bot with the command...

`uv run python -m bot`

...when you are in the directory `ClemBot/ClemBot.Bot`.

The bot should show up in the test server and respond to commands (test with `<your_prefix>hello`)

## Setting up the ClemBot.Api build environment

* Open the `ClemBot.Api.sln` file in the `ClemBot/ClemBot.Api` folder to open the project in either Visual Studio or
  Rider
* Click the run button in your preferred IDE

## Setting up the ClemBot.Site build environment

* Navigate to the ClemBot.Site folder in your shell
* Install Node.js 16 with nvm with the command `nvm install 16` then `nvm use 16`
* Install dependencies with yarn with the command `yarn install`
* The dev server can then be run with the command `yarn run dev`

## Final Notes

ClemBot is composed of several separate components that all talk to each other over HTTP to form a complete system.
Depending on what you are developing, you might not need all of them running simultaneously to develop what you want.

Here are some common scenarios and what portions of ClemBot you need to have running:

| Developing a...                         | ClemBot.Bot | ClemBot.Api | ClemBot.Site |
|-----------------------------------------|-------------|-------------|--------------|
| Discord command (no database)           | Yes         | No          | No           |
| Discord command (with database)         | Yes         | Yes         | No           |
| Website bug fix/feature (not dashboard) | No          | No          | Yes          |
| Dashboard bug fix/feature               | Yes         | Yes         | Yes          |

In instances where **ClemBot.Bot** is not using **ClemBot.Api**, the `BotOnly` setting in the `BotSecrets.json` file can
be toggled to `true` and vice versa.
