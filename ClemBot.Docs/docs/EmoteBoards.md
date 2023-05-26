---
sidebar_position: 6
---
# Emote Boards

## Overview

Originally, ClemBot had a single variation of an emote board, called "starboard".
Starboard was meant as a way for users to highlight important, funny, or noteworthy messages.
If a message received four ⭐ reactions, ClemBot would repost the message along with how many reactions the message had received in a designated channel.
Emote boards build upon this concept.

Emote boards are designated channels (not to be confused with [designated channels](./DesignatedChannels.md)) that messages with enough reactions get posted to by ClemBot.
However, unlike starboard, emote boards support:
- Multiple emote boards per server/guild.
- Support for unicode and custom emotes.
- The ability for ClemBot to repost content to multiple channels per emote board.
- A leaderboard with multiple categories for general and specific emote boards.
- Message persistence and automatic management of reposted content.
- Customizable reaction count threshold.
- ...and more!

:::note
Any reactions that a user puts on a message they authored do not count.
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
!emoteboard :star:
```

### Add
