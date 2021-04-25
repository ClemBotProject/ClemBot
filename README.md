<p align="center">
  <img src="ClemBot.png" width="275" height= "275">
</p>

# ClemBot 



<p align="center">
  <br>
  <a href="https://discord.gg/QNRbC6k">
    <img src="https://img.shields.io/discord/515071617815019520.svg?label=Discord&logo=Discord&colorB=7289da&style=for-the-badge" alt="Support">

  <a href="https://www.python.org/downloads/">
    <img src="https://img.shields.io/badge/Made%20With-Python%203.8-blue.svg?style=for-the-badge&logo=Python" alt="Made with Python 3.8">
  </a>
  <a href="https://github.com/ClemsonCPSC-Discord/ClemBot/blob/master/LICENSE">
    <img src="https://img.shields.io/badge/license-mit-e74c3c.svg?style=for-the-badge&logo=appveyor" alt="MIT License">
  </a>
  </br>
</p>

<p align="center">
  </a>
    <a href="https://top.gg/bot/710672266245177365">
    <img src="https://top.gg/api/widget/710672266245177365.svg" alt="ClemBot" />
  </a>
</p>
 
 
A Discord bot for server and community management with a focus on school/programming/fun related commands. 
   - <b>Moderation:</b>  Moderation and Moderation logging is made easy with ClemBot, Banning, Muting and Warning are all supported and easy to use

   - <b>Role Management:</b> Easily manage you and your users roles with designated assignable roles
   
   - <b>Starboard:</b> Allow your server to highlight the best or funniest messages by members with a starboard, simply assign the starboard channel and react with stars

   - <b>Customizable Prefix:</b> Whatever you want ClemBot to respond to, it can. Just set your servers preferred prefix with  `!prefix <prefix>`
    
   - <b>Python Repl:</b> Coding is fun, Discord is fun. Put them together and collaborative learning is easy with a built in python interpreter. Just type your python code into discord and run it with `!eval` and watch the bot evaluate your code.
    
   - <b>Message Logging:</b> Clembot offers the abillity to log message edits and deletions, just run `!channels add message_log #mychannel` to designate a channel as a log message
   
   - <b>Tags:</b> Tags allow you to create message snippets that can be invoked right in discord with a simple inline command. Just run `!tag add  <MyTagName> <MyTagsBody>` and invoke it with `$MyTagName`
   
   - <b>Channel Generation:</b>  If you are a school related server clembot offers an easy way to generate class channels and roles. Just run `!class add` and follow the onscreen prompts
   
   - <b>Welcome Messages:</b>  You can optionally set a message to be sent to new members of your server. Making it easy to make sure people understand rules and procedures.
   
   - <b>Expression Evaluator:</b>  Clembot implements the shunting yard algorithim to allow for rapid mathematical expression evaluation right in discord. just run `!calc 1+1` to get your result
   
   - <b>Meme Generator:</b>  SpongeBob text, Crab raves, wheres waldo and more. only one way to find all of them!!
   
   - <b>Weather Forecasts:</b> Clembot supports weather forecasts from anywhere in the world, simply run `!weather <location>` to get a full 7 day forecast for your area
  
   - <b>Translation:</b> Leveraging Azure translation services Clembot supports over 50 langauges world wide for instant translation!
     
   and so much more
   
   Clembot is in current active development so check back often to see whats new!!

# Bot Invite
To invite Clembot to your server click this link: [Clembot Invite](https://discord.com/api/oauth2/authorize?client_id=710672266245177365&permissions=1409412343&scope=bot)

## Community
We are a community focused on learning and acceptance; anyone is welcome. If you have an idea or a feature you would like to contribute, feel free to open an issue and we as a community can begin discussion. 

# Development
To start developing and contributing to this project, please see [CONTRIBUTING.md](CONTRIBUTING.md)

# Architecture overview

The bot is set up in a simple way. There are 3 layers, the Cog layer, the Service layer and the Data layer. Cogs and Services communicate exclusively through the messenger. This allows us to maintain total decoupling of the layers. Repos are referenced directly in both.

1. Cog layer - This is where the frontend bot command code resides. Anything that you directly use to interface with discord goes in this layer.
2. Service layer - This is where all things that are bot related but not controlled through front end commands live. Things like user tracking, event handling etc all go in here.
3. Data layer - This is the abstraction on top of the sqlite database. This layer is a collection of repositories which contain the code to query and insert from the DB.

The bot loads Cogs and Services dynamically. To create a new command simply create a class that inherits from Command.Cog and defines a setup function in module scope at the bottom. See [example_cog.py](https://github.com/ClemsonCPSC-Discord/ClemBot/blob/master/bot/cogs/example_cog.py) for an example. 

The bot does the same thing for services, to see how to define a service, see [example_service.py](https://github.com/ClemsonCPSC-Discord/ClemBot/blob/master/bot/services/example_service.py)

![ClemBot Master Deployment](https://github.com/ClemsonCPSC-Discord/ClemBot/workflows/ClemBot%20Master%20Deployment/badge.svg?branch=master)
![ClemBot Master Integration](https://github.com/ClemsonCPSC-Discord/ClemBot/workflows/ClemBot%20Master%20integration/badge.svg?branch=master)
