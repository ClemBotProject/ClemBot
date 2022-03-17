---
sidebar_position: 5
---
# Assignable Roles

## Overview

Servers often have many roles that regular users can have, but might not want to give all users access to all roles; however, it can be annoying to manually give people the roles they want. ClemBot provides a way to mark roles as assignable so that normal users can add and remove them as they please with a simple command.

## Commands

### Roles
Shows all currently assignable roles roles in the server, or adds an assignable role to yourself if one is specified.

#### Aliases
* `role`

#### Format
```txt title="List all assignable roles in the server"
!roles
```

```txt title="Assign a given role to yourself"
!roles <rolename>
```
#### Example

```
!role
```

```
!role myrolename

!role @myrole
````

### Add
Mark a server role as assignable

:::note
Note: This is the admin command to **MARK** a role as assignable. If you would like to give yourself a role please see the above section on adding an assignable role to yourself
:::

#### Aliases
* `create`

#### Required [Claims](./Claims.md)
* `assignable_role_add`

#### Format

```
!role add <RoleName>
```
#### Example

```
!role add MyRole 
```

### Remove
Remove a server role as assignable

:::note
This is the admin command to **REMOVE** a role as assignable. If you would like to remove a role from yourself please see the above section on removing an assignable role from yourself
:::

#### Aliases
* `delete`

#### Required [Claims](./Claims.md)
* `assignable_role_delete`

#### Format

```
!role delete <RoleName>
```
#### Example

```
!role delete MyRole 
```