---
sidebar_position: 2
---

# Custom Prefix

## Overview
A command prefix is the character or phrase that notifies ClemBot that you wish to invoke a command.

### Command Example
```txt title="Discord Message"
!about
```
"!" is the command prefix and about is the name of the command that you wish to invoke.

:::tip
Clembots mention serves as a universal prefix, it can always be used to invoke the bots commands

use `@ClemBot prefix` to find what prefix the bot has been set to in your server
:::

## Dashboard
Changes a servers prefix to a given value. If no value is provided the current in use prefix is shown.

## Commands

### Prefix

#### Aliases
* `prefixs`

#### Required [Claims](./Claims.md)
* `custom_prefix_set`

#### Format
```txt title="View the current prefix"
!prefix 
```

```txt title="Change the current prefix"
!prefix <NewPrefix>
```
#### Example
```
!prefix
```

```
!prefix ?
```