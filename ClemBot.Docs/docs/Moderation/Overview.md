---
sidebar_position: 1
---

# Overview

ClemBot provides powerful moderation tools to help you run your server.
Every moderation action is logged and categorized and can be searched through at any time.
You have a complete history of every infraction ever committed in your server.
To view them, run the commands below.

## Logging

ClemBot will log all moderation actions into a given channel if configured.
See [Designated Channels](../DesignatedChannels.md) for more information on how to enable moderation logging.

## Commands

### Infractions

#### Required [Claims](../Claims.md)

`moderation_infraction_view`
or
`moderation_infraction_view_self`

:::info
The `moderation_infraction_view_self` only gives a user permission to view their **OWN** infractions.
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
You can find the infraction ID by running the `!infractions` command on the user you wish to remove the infraction from.
:::

#### Example

```
!infractions delete 12
```