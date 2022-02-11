---
sidebar_position: 2
---
# Ban

## Overview
Bans remove an individual from a server permanently and blocks their IP from rejoining. Allows for optionally specifying the number of days of messages from which to purge a users messages. (Defaults to 0 with a maximum of 7)

:::note
The IP ban is done on Discords side, and can be easily circumvented
:::

## Commands

### Ban

#### Required [Claims](./Claims.md)
* `moderation_ban`

#### Format
```
!ban @User <DaysToPurge> <Reason>
```

#### Example
```
!ban @User Spamming and trolling!

!ban @User 3 Spamming and trolling so bad we want to delete 3 days of messages!
```