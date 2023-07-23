---
sidebar_position: 6
---

# Emote Boards

## Overview

Originally, ClemBot had a single variation of an emote board, called "starboard".
Starboard was meant as a way for users to highlight important, funny, or noteworthy messages.
If a message received four ⭐ reactions, ClemBot would repost the message along with how many reactions the message had
received in a designated channel.
Emote boards build upon this concept in a more generalized and customizable way.
In essence, emote boards are designated channels (not to be confused
with [designated channels](./DesignatedChannels.md)) that
messages with enough reactions (as determined by the emote
board's [configuration](#customization-and-configuration-of-emote-boards)) get posted to by ClemBot.

:::note
Any reactions that a user puts on a message they authored are invalid and do not count towards the total.
:::

However, unlike starboard, emote boards support:

- Multiple emote boards per server/guild (no limit).
- Support for unicode and custom emotes.
- The ability for ClemBot to repost content to multiple channels per emote board.
- A leaderboard with multiple categories for server-wide and specific emote boards.
- Message persistence and automatic management of reposted content.
    - Edited messages that have been reposted to an emote board by ClemBot will be updated to reflect the new message
      content.
    - Deleted messages that have been reposted to an emote board by ClemBot will be deleted.
- The ability to customize the reaction count threshold (number of reactions needed).
- The ability to set whether messages authored by bot accounts will be reposted.

These new features are explained in further detail below.

### Customization and Configuration of Emote Boards

Although servers can create multiple emote boards per server/guild, each emote board can be configured differently.
The following table shows what can be configured per emote board and the default values.

| Title              | Details                                                                             | Command(s)                                                     | Default Value |
|--------------------|-------------------------------------------------------------------------------------|----------------------------------------------------------------|---------------|
| Allow Bot Posts    | Whether messages authored by bot accounts can be posted to the emote board.         | [Set Bots](#set-bots)                                          | `False`       |
| Emote              | The emote associated with the emote board.                                          | [Set Emote](#set-emote)                                        | N/A           |
| Channels           | The channels ClemBot will repost messages to upon a message reaching the threshold. | [Channel Add](#channel-add), [Channel Remove](#channel-remove) | N/A           |
| Reaction Threshold | The number of valid reactions required in order for ClemBot to repost the message.  | [Set Threshold](#set-threshold)                                | `4`           |

:::note
The name of an emote board cannot be changed after creation.
:::

### Reaction Multipliers

Along with these new features, emote boards, just like starboard, still support reaction multipliers.
Reaction multipliers add a title to the reposted content based on the number of reactions received and the number of
reactions needed to be posted to the emote board.

Below are the reaction multipliers and the title associated with that multiplier.

| Multiplier | Title                    |
|------------|--------------------------|
| 1x         | POPULAR                  |
| 2x         | QUALITY                  |
| 3x         | *THE PEOPLE HAVE SPOKEN* |
| 4x         | *INCREDIBLE*             |
| 5x         | **LEGENDARY**            |
| 6x         | ***GOD-TIER***           |

:::tip
The multiplier assigned to any reposted content is determined by the reaction threshold of that emote board.

If my emote board, **starboard**, has a reaction threshold of **4** and my message receives **8** valid
reactions, the reaction multiplier for that post is **2x** (`8 / 4 = 2, remainder of 0`).
A message with **7** reactions on the same emote board has a reaction multiplier of **1x
** (`7 / 4 = 1, remainder of 3`).
:::

## Commands

### EmoteBoard

Lists the emote boards in the server or the details for a specific emote board.

#### Aliases

- `eb`
- `board`
- `boards`
- `emojiboard`

#### Format

```
!emoteboard [board name | emote]
```

#### Example

```
!emoteboard
```

```
!emoteboard #starboard
```

```
!emoteboard ⭐
```

### Add

Adds an emote board to the server/guild.

#### Aliases

- `create`

#### Required [Claims](./Claims.md)

```
manage_emote_boards
```

#### Format

```
!emoteboard add <emote> <name> <channel>
```

#### Example

```
!emoteboard add ⭐ starboard #starboard
```

```
!emoteboard add :a_custom_emote: myboard #my-board-channel
```

### Remove

Remove an existing emote board from the server/guild.

:::warning
All data retained by ClemBot for the given emote board will be deleted and cannot be recovered.
:::

#### Aliases

- `delete`

#### Required [Claims](./Claims.md)

```
manage_emote_boards
```

#### Format

```
!emoteboard remove <board name | emote>
```

#### Example

```
!emoteboard remove starboard
```

```
!emoteboard remove ⭐
```

### Leaderboard

View the leaderboard for all emote boards in the server/guild or for a specific emote board.
The leaderboard has multiple categories that a post or user may be eligible for.

| Category Name       | Details                                                   |
|---------------------|-----------------------------------------------------------|
| Popular Posts       | The number of valid reactions gained for a single post.   |
| Number of Posts     | The total number of posts a user has reposted to a board. |
| Number of Reactions | The total number of reactions a user has received.        |

Up to 5 entries per category are displayed on the leaderboard.

#### Aliases

- `top`

#### Format

```
!emoteboard leaderboard [board name | emote]
```

#### Example

```
!emoteboard leaderboard
```

```
!emoteboard leaderboard ⭐
```

```
!emoteboard leaderboard starboard
```

### Set Threshold

Sets the number of valid reactions a message must receive in order for ClemBot to repost the message to an emote board.

#### Aliases

- `limit`
- `reactions`
- `emotes`
- `emojis`

#### Required [Claims](./Claims.md)

```
manage_emote_boards
```

#### Format

```
!emoteboard set threshold <board name | emote> <reaction count>
```

:::note
Although `reaction count` has no upper limit, it must be greater than `0`.
:::

#### Example

```
!emoteboard set threshold starboard 4
```

```
!emoteboard set threshold ⭐ 5
```

### Set Bots

Sets whether messages authored by bot accounts can be reposted to a given emote board.

#### Aliases

- `bot`
- `allow_bots`
- `bot_posts`

#### Required [Claims](./Claims.md)

```
manage_emote_boards
```

#### Format

```
!emoteboard set bots <board name | emote> <true | false>
```

#### Example

```
!emoteboard set bots starboard false
```

```
!emoteboard set bots ⭐ true
```

### Set Emote

Sets the emote that belongs to the given emote board.
The name of an emote board is permanent, while the emote of a board can be changed at any time.
Both unicode emojis and custom emotes uploaded to Discord are supported.

:::caution
Formatting errors may occur if the custom emote provided belongs to a server that ClemBot is not a member of.
:::

#### Aliases

- `emoji`

#### Required [Claims](./Claims.md)

```
manage_emote_boards
```

#### Format

```
!emoteboard set emote <board name> <emote>
```

#### Example

```
!emoteboard set emote starboard ⭐
```

```
!emoteboard set emote myboard :a_custom_emote:
```

### Channel Add

Adds the given Discord channel to the list of channels for the given emote board.

#### Required [Claims](./Claims.md)

```
manage_emote_boards
```

#### Format

```
!emoteboard channel add <channel> <board name | emote>
```

#### Example

```
!emoteboard channel add #starboard ⭐
```

```
!emoteboard channel add #my-channel myboard
```

### Channel Remove

Removes the given Discord channel from the list of channels for the given emote board.

:::caution
Although an emote board is allowed to have no channels, all reactions to messages with the emote board's emote will be
ignored. Reactions to prior reposted messages for the emote board will also be ignored and will not count towards the
leaderboard.
:::

#### Aliases

- `delete`

#### Required [Claims](./Claims.md)

```
manage_emote_boards
```

#### Format

```
!emoteboard channel remove <channel> <board name | emote>
```

#### Example

```
!emoteboard channel remove #starboard ⭐
```

```
!emoteboard channel remove #my-channel myboard
```
