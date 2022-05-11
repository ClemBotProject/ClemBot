---
sidebar_position: 3
---

# Authorization Claims

## Overview
By default ClemBot allows for anyone with Admin permissions in Discord full access to ClemBot's functionality. If you want to grant people without server admin permissions access to individual parts of the Bot (a team of moderators for example) you can do that through "Claims".

:::info
Server owners and users with administrator roles are automatically granted all claims regardless of what roles they posess
:::

Claims are ClemBot's way of providing servers' incredibly granular and precise control over WHO has access to different parts of ClemBot. Claims are added to roles within your server. Anyone who has a role that has associated claims is granted access to the functionality of the Bot that the claim correlates to. A role can have multiple claims associated with it, and a claim can be associated with multiple roles. You decide how to set up your server!

## Available Claims
| Name                            | Description                                                                           |
|---------------------------------|---------------------------------------------------------------------------------------|
| assignable_roles_add            | Allows for marking a role as assignable                                               |
| assignable_roles_delete         | Allows for removing a role as assignable                                              |
| claims_modify                   | Allows for modifying the assigned claims of a role                                    |
| claims_view                     | Allows for viewing of claims that a user or role has                                  |
| custom_prefix_set               | Allows for setting the [custom prefix](./CustomPrefix.md) the Clembot responds to     |
| delete_message                  | Allows for deletion of any message that Clembot reacts with a trashcan too            |
| designated_channel_modify       | Allows for adding and removing designations from [channels](./DesignatedChannels.md) in a server              |
| designated_channel_view         | Allows for viewing of available and assigned designated [channels](./DesignatedChannels.md) in a server          |
| guild_settings_view             | Allows for viewing of the guilds settings on the dashboard                            |
| guild_settings_view             | Allows for modifying of the guilds settings on the dashboard                          |
| moderation_ban                  | Allows for usage of the ban command                                                   |
| moderation_infraction_view      | Allows for usage of the infractions command to list a given users infractions         |
| moderation_infraction_view_self | Allows for usage of the infractions command to view only the users own infractions    |
| moderation_mute                 | Allows for usage of the mute command                                                  |
| moderation_warn                 | Allows for usage of the warn command                                                  |
| tag_add                         | Allows for adding a [tag](./Tags.md) in a server                                      |
| tag_delete                      | Allows for deleting other peoples [tags](./Tags.md) in a server                       |
| welcome_message_view            | Allows for viewing the servers [welcome message](./WelcomeMessage.md)                 |
| welcome_message_modify          | Allows for setting the servers [welcome message](./WelcomeMessage.md)                 |

## Commands

### Claims
View all the claims on a given user or role. If a role is given, the command will return the aggregate of all claims from all roles the user has.

#### Required [Claims](./Claims.md)
* `claims_view`

#### Format
```
!claims @Role
```

```
!claims @User
```
#### Example

```
!claims @Jayy
```

```
!claims @MyCoolRole
```

### Add 
Adds a claim to a given role, everyone who has that role will be granted permissions to that functionality

#### Aliases
* `set`

#### Required [Claims](./Claims.md)
* `claims_modify`

#### Format

```
!claims add <ClaimName> @Role
```
#### Example

```
!claims add tag_add @MyCoolRole
```

### Remove 
Removes a claim from a given role, everyone who has that role will no longer have permissions for that functionality

#### Aliases
* `delete`

#### Required [Claims](./Claims.md)
* `claims_modify`

#### Format

```
!claims add <ClaimName> @Role
```
#### Example

```
!claims add tag_add @MyCoolRole
```
