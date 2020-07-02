![ClemBot Master Deployment](https://github.com/ClemsonCPSC-Discord/ClemBot/workflows/ClemBot%20Master%20Deployment/badge.svg?branch=master)

# ClemBot - A Discord Bot for the Clemson CPSC Discord Server
A Discord bot for server management with a focus on school related commands. We are a community focused on learning and acceptance and anyone is welcome. If you have an idea or a feature you would like to contribute feel free to open an issue and we as a community can begin discussion. 
## Server Invite:  

<div align="center">
  <br>

  <a href="https://discord.gg/QNRbC6k">
    <img src="https://img.shields.io/discord/515071617815019520.svg?label=Discord&logo=Discord&colorB=7289da&style=for-the-badge" alt="Support">
  </a>
  
  <a href="https://www.python.org/downloads/">
    <img src="https://img.shields.io/badge/Made%20With-Python%203.7-blue.svg?style=for-the-badge&logo=Python" alt="Made with Python 3.7">
  </a>
  
  <a href="https://github.com/ClemsonCPSC-Discord/ClemBot/blob/master/LICENSE">
    <img src="https://img.shields.io/badge/license-mit-e74c3c.svg?style=for-the-badge&logo=appveyor" alt="MIT License">
  </a>
  </br>
</div>

# Development
To start developing and contributing to this project, please see [CONTRIBUTING.md](CONTRIBUTING.md)

# Architecture overview

The bot is set up in a simple way. There are 3 layers, the Cog layer, the Service layer and the Data layer.

1. Cog layer - This is where the frontend bot command code resides. Anything that you directly use to interface with discord goes in this layer.
2. Service layer - This is where all things that are bot related but not controlled through front end commands live. Things like user tracking, event handling etc all go in here.
3. Data layer - This is the abstraction on stop of the sqlite database. This layer is a collection of repositories which contain the code to query and insert from the DB

The bot loads Cogs and Services dynamically. To create a new command simply create a class that inherits from Command.Cog and defines a setup function in module scope at the bottom. See manage_classes.py for an example.
