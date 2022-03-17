---
sidebar_position: 6
---

# Welcome Message

## Overview
Welcome messages are a way to define a message that ClemBot will dm to all members that join your server. You can use this to notify users of any rules or setup they may need to know, or just say hello!

## Dashboard
A guilds welcome message can be viewed and set from the guild tab on the dashboard.

## Commands

### Welcome
View the current welcome message

#### Required [Claims](./Claims.md)
* `welcome_message_view`

#### Example
```txt
!welcome
```

### Set
Sets a servers welcome message

#### Required [Claims](./Claims.md)
* `welcome_message_modify`

#### Format
```
!welcome set <WelcomeMessage>
```

#### Example
```txt
!welcome set welcome to our amazing server
```

### Delete
Deletes a servers welcome message

#### Required [Claims](./Claims.md)
* `welcome_message_modify`

#### Example
```txt
!welcome delete
```