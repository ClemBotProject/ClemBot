---
sidebar_position: 4
---

# Command Restrictions

## Overview

Command restrictions give the ability to block certain ClemBot commands either in a specific channel or server-wide.
When attempting to run a disabled command, ClemBot can either respond to the user that the command is disabled or will
silently ignore the command.
This is a useful feature for letting admins and mods block certain commands they don't think are useful to that specific
channel or do not want a certain command to be used anywhere.

## Whitelisting

If you want to block a command in all places except a few channels, you can whitelist channels by first globally
disabling them, then enabling them in a specified channel.

:::tip
Both top-level commands (such as `claims`) and sub-commands (such as `claims add`) can be disabled.
:::

## Commands

### Command

View the status of a command.

The following table explains what properties are included in the status of a command.

| Title                               | Description                                                                                                  |
|-------------------------------------|--------------------------------------------------------------------------------------------------------------|
| Name                                | The name of the command.                                                                                     |
| Allows Disabling                    | Whether the command can be disabled. See [Disable](#disable) for a list of commands that cannot be disabled. |
| Disabled / Disabled In / Enabled In | Whether the command is disabled. If disabled or enabled in specific channels, those channels will be listed. |

#### Aliases

- `cmd`

#### Format

```
!command <command name>
```

:::tip
The `command name` parameter also supports aliases of commands.
:::

#### Example

```
!command tags
```

```
!command tag add
```

### Enable

Enables the given command either server-wide or in the specified channel.
If enabling a command in a specific channel, and the command has a server-wide restriction applied to it, the command
will be whitelisted for that specific channel while blacklisted everywhere else.
It can be disabled again with the [disable command](#disable).

#### Required [Claims](./Claims.md)

- `command_restrictions_edit`

#### Aliases

- `on`

#### Format

```
!command enable <command name> [channel]
```

#### Example

```txt title="Enable a command server-wide"
!command enable slots
```

```txt title="Enable a command in a specific channel"
!command enable tags #my-channel
```

### Disable

Disables the given command either server-wide or in the specified channel, with the option to ignore the command
silently.

:::caution
Any user or role that has the `bypass_disabled_commands` [claim](./Claims.md) can run disabled commands.
:::

:::note
The following command(s) are currently not allowed to be disabled:

- `help`
- `command`
- `command enable`

This is to ensure that users cannot soft-lock integral parts of ClemBot.
:::

#### Required [Claims](./Claims.md)

- `command_restrictions_edit`

#### Aliases

- `off`

#### Format

```
!command disable <command name> [channel] [silent]
```

:::note
By default, when disabling a command, it will respond to the user that the command is disabled if `silent` is not set
to `true`.
:::

#### Example

```txt title="Disable a command server-wide"
!command disable tags
```

```txt title="Disable a command in a specific channel"
!command disable tags #my-channel
```

```txt title="Disable a command server-wide, silently"
!command disable tags true
```

```txt title="Disable a command in a specific channel, silently"
!command disable tags #my-channel true
```

```txt title="Disable a sub-command in a specific channel, silently"
!command disable tag add #my-channel true
```
