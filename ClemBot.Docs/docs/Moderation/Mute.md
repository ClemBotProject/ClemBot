---
sidebar_position: 4
---
# Mute

## Overview
Mutes silence an individual and prevent them from sending messages or joining voice channels for a given amount of time.

## Setup
Mutes require a one time inital setup for ClemBot to create the mute role and add it to all the channels. This might take a while depending on how many channels your server has. To avoid a heavy startup load the bot will prompt you to initialize the role when you run the mute command for the first time. After the initial setup is complete it will then apply the mute as normal.

:::caution
If you have a large server with many channels this initial setup can take a minute or two due to discord rate limits, do not worry though. Once the mute role is setup the bot will mute the user as requested.
:::

## Duration String
ClemBot supports time strings to specify how long a mute should last. For example, to mute someone for 12 hours you would use the string `12h`. To mute someone for twelve days and thirty minutes you would use the string `12d30m`. And so on in any combination you would like.

**`Available Options`**
```
- years: `Y`, `y`, `year`, `years`
- months: `M`, `month`, `months`
- weeks: `w`, `W`, `week`, `weeks`
- days: `d`, `D`, `day`, `days`
- hours: `H`, `h`, `hour`, `hours`
- minutes: `m`, `min`, `minute`, `minutes`
- seconds: `S`, `sec`, `s`, `second`, `seconds`
```

:::note
The string needs to be in descending order
:::note

## Commands

### Mute

#### Required [Claims](./Claims.md)
* `moderation_mute`

#### Format
```
!mute @User <Duration> <Reason>
```

#### Example
```
!mute @User 1d1h Spamming and trolling
```
