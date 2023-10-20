---
sidebar_position: 6
---

# Auto Assigned Roles

## Overview

Server admins may want users to be auto-assigned roles on join. This functionality is exposed through the roles auto
sub-command group.

## Commands

### Roles Auto

Shows all current auto-assignable roles in a server.

#### Format

```txt title="List all auto assigned roles in the server"
!roles auto
```

#### Example

```
!role auto
```

### Auto add

Mark a server role as assignable

:::note
This is the admin command to **MARK** a role as auto assigned on join.
If you would like to give yourself a role, please see the [user assignable roles](./UserAssignableRoles.md) section on
adding an assignable role to yourself.
:::

#### Aliases

* `create`

#### Required [Claims](../Claims.md)

* `assignable_role_add`

#### Format

```
!role auto add <RoleName>
```

#### Example

```
!role auto add MyRole 
```

### Auto remove

Remove a server role as auto-assignable.

:::note
This is the admin command to **REMOVE** a role as auto assigned on join.
If you would like to give yourself a role please see the [user assignable roles](./UserAssignableRoles.md) section on
adding an assignable role to yourself.
:::

#### Aliases

* `delete`

#### Required [Claims](../Claims.md)

* `assignable_role_delete`

#### Format

```
!role auto delete <RoleName>
```

#### Example

```
!role auto delete MyRole 
```