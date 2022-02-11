---
sidebar_position: 1
---
# Overview

ClemBot provides powerful moderation tools to help you run your server. Every moderation action is logged and categorized and can be searched through at any time. With support for all the standard commands and more coming soon!!

You have a complete history of every Infraction every committed in your server, to view them run these comands.

## Logging

ClemBot will log all moderation actions into a given channel if configured. See [Designated Channels](../DesignatedChannels.md) for more information on how to enable moderation logging.

## Commands

### Infractions

#### Required [Claims](./Claims.md)
* `moderation_infraction_view`
* or 
* `moderation_infraction_view_self`

:::info
The `moderation_infraction_view_self` only gives a user permissiont to view their **OWN** infractions, and no one elses
:::

#### Format
```txt title="View your own infractions"
!infractions 
```

```txt title="View a users infractions"
!infractions <User>
```

#### Example
```
!infractions

!infractions @SomeUser
```

### Delete
Deletes a given infraction

#### Format
```
!infractions delete <InfractionId>
```

:::tip
You can find the infraction id by running the `!infractions` command on the user you wish to remove the infraction from
:::

#### Example
```
!infractions delete 12
```