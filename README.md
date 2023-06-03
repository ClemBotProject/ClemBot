<p align="center">
    <img src="Branding/ClemBot.png" width="275" height= "275" alt="ClemBot Logo">
</p>

# ClemBot

<p align="center">
    <br/>
    <a href="https://discord.gg/QNRbC6k">
        <img src="https://img.shields.io/discord/515071617815019520.svg?label=Discord&logo=Discord&colorB=7289da&style=for-the-badge" alt="Support">
    </a>
    <a href="https://www.python.org/downloads/">
        <img src="https://img.shields.io/badge/Made%20With-Python%203.10-blue.svg?style=for-the-badge&logo=Python" alt="Made with Python 3.10">
    </a>
    <a href="https://github.com/ClemsonCPSC-Discord/ClemBot/blob/master/LICENSE">
        <img src="https://img.shields.io/badge/license-mit-e74c3c.svg?style=for-the-badge&logo=appveyor" alt="MIT License">
    </a>
</p>

<p align="center">
    <a href="https://top.gg/bot/710672266245177365">
        <img src="https://top.gg/api/widget/710672266245177365.svg" alt="ClemBot" />
    </a>
</p>

## Website, Documentation and Configuration Dashboard

https://clembot.io

## Intro

A Discord bot for server and community management with a focus on school/programming/fun related commands.

- <b>Moderation:</b> Moderation and Moderation logging is made easy with ClemBot, Banning, Muting and Warning are all
  supported and easy to use

- <b>Role Management:</b> Easily manage you and your users roles with designated assignable roles

- <b>Starboard:</b> Allow your server to highlight the best or funniest messages by members with a starboard, simply
  assign the starboard channel and react with stars

- <b>Customizable Prefix:</b> Whatever you want ClemBot to respond to, it can. Just set your servers preferred prefix
  with `!prefix <prefix>`.

- <b>Python Repl:</b> Coding is fun, Discord is fun. Put them together and collaborative learning is easy with a
  built-in python interpreter. Just type your python code into discord and run it with `!eval` and watch the bot
  evaluate your code.

- <b>Message Logging:</b> ClemBot offers the ability to log message edits and deletions, just
  run `!channels add message_log #mychannel` to designate a channel as a log message

- <b>Tags:</b> Tags allow you to create message snippets that can be invoked right in discord with a simple inline
  command. Just run `!tag add  <MyTagName> <MyTagsBody>` and invoke it with `$MyTagName`

- <b>Welcome Messages:</b>  You can optionally set a message to be sent to new members of your server. Making it easy to
  make sure people understand rules and procedures.

- <b>Expression Evaluator:</b>  ClemBot implements the shunting yard algorithm to allow for rapid mathematical
  expression evaluation right in discord. just run `!calc 1+1` to get your result

- ...and so much more!

ClemBot is in current active development so check back often to see what's new!!

# Bot Invite

To invite ClemBot to your server,
click [here](https://discord.com/api/oauth2/authorize?client_id=710672266245177365&permissions=398828104950&scope=bot).

## Community

We are a community focused on learning and acceptance; anyone is welcome. If you have an idea or a feature you would
like to contribute, feel free to open an issue and we as a community can begin discussion.

# Development

To start developing and contributing to this project, please see [CONTRIBUTING.md](CONTRIBUTING.md)

# Architecture overview

ClemBot utilizes a standard three tier architecture. 
The **ClemBot.Bot** project makes requests to the **ClemBot.Api** project, which then subsequently queries the PostgreSQL database.

## ClemBot.Bot

The bot is set up in a simple way. There are 3 layers, the Cog Layer, the Service Layer and the Route Layer. Cogs and
Services communicate exclusively through the messenger. This allows us to maintain total decoupling of the layers.

1. **Cog Layer:** This is where the frontend bot command code resides. Anything that you directly use to interface with
   discord goes in this layer.
2. **Service Layer:** This is where all things that are bot related but not controlled through front end commands live.
   Things like user tracking, event handling, etc., all go in here.
3. **Route Layer:** This is the route abstraction on top of the ApiClient. This layer defines methods that correspond to
   routes that are sent back to the ClemBot.Api project

The bot loads Cogs and Services dynamically. To create a new command, simply create a class that inherits from
[commands.Cog](https://discordpy.readthedocs.io/en/stable/ext/commands/api.html?highlight=cog#discord.ext.commands.Cog)
and define a setup function in module scope at the bottom.
See [example_cog.py](https://github.com/ClemsonCPSC-Discord/ClemBot/blob/master/bot/cogs/example_cog.py) for an example.

The bot does the same thing for services, to see how to define a service,
see [example_service.py](https://github.com/ClemsonCPSC-Discord/ClemBot/blob/master/bot/services/example_service.py).

## ClemBot.Api

The API utilizes the following technologies...

* [Asp.Net](https://dotnet.microsoft.com/apps/aspnet)
* [Entity Framework](https://docs.microsoft.com/en-us/ef/)
* [MediatR](https://github.com/jbogard/MediatR)
* [Serilog](https://serilog.net/)

...and is split up into several different projects under one solution:

- **ClemBot.Api.Data** contains the Entity Framework code-first database models and contexts.
- **ClemBot.Api.Core** contains the startup project and Asp.Net endpoints located in the `Features` folder.
- **ClemBot.Api.Services** contains the caching and authorization services that perform more complex tasks.

## ClemBot.Site

The site is a server-side Nuxt.js and Vue.js app that integrates with Discord OAuth.

* [Vue.js](https://vuejs.org/)
* [Nuxt.js](https://nuxtjs.org/)

## ClemBot Pipeline Status

| Service | Pipeline                        | Status                                                                                                                                                   |
|---------|---------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------|
| Api     | ClemBot.Api Master Integration  | ![ClemBot.Api Master Integration](https://github.com/ClemBotProject/ClemBot/actions/workflows/ClemBot.Api-Integration.yml/badge.svg?branch=master)       |
| Api     | ClemBot.Api Master Deployment   | ![ClemBot.Api Master Deployment](https://github.com/ClemBotProject/ClemBot/actions/workflows/ClemBot.Api-Deployment.yml/badge.svg?branch=master)         |
| Bot     | ClemBot.Bot Master Integration  | ![ClemBot.Bot Master Integration](https://github.com/ClemBotProject/ClemBot/actions/workflows/ClemBot.Bot-Integration.yml/badge.svg?branch=master)       |
| Bot     | ClemBot.Bot Master Deployment   | ![ClemBot.Bot Master Deployment](https://github.com/ClemBotProject/ClemBot/actions/workflows/ClemBot.Bot-Deployment.yml/badge.svg?branch=master)         |
| Site    | ClemBot.Site Master Integration | ![ClemBot.Site Master Integration](https://github.com/ClemBotProject/ClemBot/actions/workflows/ClemBot.Site-Integration.yml.yml/badge.svg?branch=master) |
| Site    | ClemBot.Site Master Deployment  | ![ClemBot.Site Master Deployment](https://github.com/ClemBotProject/ClemBot/actions/workflows/ClemBot.Site-Deployment.yml/badge.svg?branch=master)       |

