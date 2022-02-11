---
sidebar_position: 1
slug: /
---

# Introduction

Hello there, and welcome to **ClemBot**! ClemBot is a modular and configurable Discord bot for all of your server needs. For a complete list of all ClemBot commands run the !help command in a server that ClemBot is in.

:::info
We are currently in the process of transitioning configuration and functionality to the websites dashboard, features that have a dashboard component will be annotated as such.
:::

## Getting Started

After ClemBot has been added to your server and initialized, it's time to do some basic setup. The first thing to do is decide which command prefix you would like ClemBot to respond to. By default ClemBot will respond to "!" as well as ClemBot's mention. To change this, simply run the prefix command with the new prefix you would like ClemBot to respond to. If you are fine with "!" remaining the prefix, you may skip this step. For more information on this functionality please see the [Custom Prefix](./CustomPrefix.md) section of the docs.

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
For documentation purposes the default prefix will be assumed to be enabled. If you have changed your guilds prefix then substitue your prefix for !
:::

## Permissions

The next step is to assign claims to your moderator/admin roles, Claims are ClemBot's way of granting access to different ClemBot functionality. Claims are associated with roles and can be added and removed from them arbitrarily. Please see the [claims](./Claims.md) section of the docs for more information.
