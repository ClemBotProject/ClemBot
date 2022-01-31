---
sidebar_position: 4
---
# Designated Channels

## Overview
ClemBot provides multiple different logging solutions for all aspects of your server, the way that ClemBot allows you to configure this is through a concept called Designated Channels. There are multiple possible designations for different events that ClemBot processes. You may add these designations to as many channels within your server as you would like. A channel can also have multiple designations at once.

## Available Designations

| Name           | Description                                                                           |
|----------------|---------------------------------------------------------------------------------------|
| message_log    | Channel for Clembot to log all message edits and deletions                            |
| moderation_log | Channel for Clembot to send a log of all moderation actions that happen in the server |
| starboard      | Channel to allow for starred messages to be immortalized for eternity                 |
| user_join_log  | Channel for Clembot to log all users that join the server                             |
| user_leave_log | Channel for Clembot to log all users that leave the server                            |

## Commands

### Channel
Shows all current designated channels in the server

#### Aliases
* `channels`

#### Required [Claims](./Claims.md)
* `designated_channel_view`

#### Example
```
!channel
```

### Add
Adds a designated channel mapping to a given channel

#### Aliases
* `set`
* `register`

#### Required [Claims](./Claims.md)
* `designated_channel_modify`

#### Format
```
!channel add <DesignatedChannel> <Channel>
```
#### Example
```
!channel add user_join_log #some-channel
```

### Delete
Removes a designated channel mapping from a given channel

#### Aliases
* `unregister`

#### Required [Claims](./Claims.md)
* `designated_channel_modify`

#### Format
```
!channel delete <DesignatedChannel> <Channel>
```
#### Example
```
!channel delete user_join_log #some-channel
```