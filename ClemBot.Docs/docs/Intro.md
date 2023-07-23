---
sidebar_position: 1
slug: /
---

# Introduction

Hello there, and welcome to **ClemBot**!
ClemBot is a modular and configurable Discord bot for all of your server needs.
For a complete list of all ClemBot commands run the `!help` command in a server that ClemBot is in.

:::info
We are currently in the process of transitioning configuration and functionality to the website's dashboard.
Features that have a dashboard component will be annotated as such.
:::

## Command Basics & Syntax

As you read the rest of the documentation for ClemBot, make note of the syntax used for commands, specifically
the `Format` section. Below is a table explaining what types of symbols may appear and what they mean, along with an
example.

| Symbol(s)           | Example                          | Meaning                                                           |
|---------------------|----------------------------------|-------------------------------------------------------------------|
| `<>`                | `<name>`                         | This parameter of the command is **required**.                    |
| `[]`                | `[channel]`                      | This parameter of the command is **optional**.                    |
| <code>&#124;</code> | <code>[name &#124; emoji]</code> | This **optional** parameter accepts **either** `name` or `emoji`. |
| `!`                 | `!help`                          | This is the default [prefix](./CustomPrefix.md) for ClemBot.      |

## Getting Started

After ClemBot has been added to your server and initialized, it's time to do some basic setup.
The first thing to do is decide which command prefix you would like ClemBot to respond to.
By default, ClemBot will respond to `!<command>` as well as ClemBot's mention.
To change this, simply run the prefix command with the new prefix you would like ClemBot to respond to.
If you are fine with `!` remaining as the prefix, you may skip this step.
For more information on this functionality, please see the [Custom Prefix](./CustomPrefix.md) section of the docs.

#### Example

```
!prefix ?
```

or

```
@ClemBot prefix ?
```

Congratulations, you've set up ClemBot to respond in your server!

:::info
For documentation purposes the default prefix will be assumed to be enabled.
If you have changed your guilds prefix, substitute your prefix for `!`.
:::

## Permissions

The next step is to assign claims to your moderator/admin roles.
Claims are ClemBot's way of granting access to different ClemBot functionality.
Claims are associated with roles and can be added and removed from them arbitrarily.
Please see the [Authorization Claims](./Claims.md) section of the docs for more information.
