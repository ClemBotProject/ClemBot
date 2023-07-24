---
sidebar_position: 2
---

# Ban

## Overview

Bans remove an individual from a server permanently (until undone) and blocks their IP from rejoining. Optionally, users
can specify the number of days of messages from which to purge/delete a user's messages.

:::note
The IP ban is done on Discord's side and can be easily circumvented by using a proxy.
However, enabling phone verification in your server can make ban circumvention much more difficult.
:::

To undo a ban on a user, navigate to your server/guild settings and under the `Moderation` group, click the `Bans` tab.
From there, select the user you wish to un-ban and click the `Revoke Ban` button.

## Commands

### Ban

#### Required [Claims](.././Claims.md)

* `moderation_ban`

#### Format

```
!ban @User [DaysToPurge] <Reason>
```

:::note
If `DaysToPurge` is not specified, it defaults to `0`, with a maximum value of `7`.
:::

#### Example

```
!ban @User Spamming and trolling!
```

```
!ban @User 3 Spamming and trolling so bad we want to delete 3 days of messages!
```