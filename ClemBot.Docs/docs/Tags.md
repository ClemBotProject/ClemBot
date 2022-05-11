---
sidebar_position: 6
---

# Tags

## Overview
Tags are custom commands that allow for users to create custom responses to a given tag name. Simply add a tag, and then invoke it with either command notation or inline notation and ClemBot will respond with that tags content in a given channel.

ClemBot's tags support the idea of ownership. If a user creates a tag, that tag is owned by them until they either leave the server or transfer the tag to someone else. By owning the tag they are allowed to either edit or delete the tag. When a user leaves a server all their owned tags become unclaimed and are free to be claimed by anyone else in the server.

ClemBot also tracks what tags are popular and allows for you to access that information. You can view the total number of uses of a tag as well as its owner and creation date with the tag info command or on the dashboard.

:::caution
If you leave the server all your tags will become unowned, and be up for grabs from anyone else in the server
:::

### Inline Notation
Tags in clembot can be invoked in the middle of a message by prefixing the tag name with a `$`. This allows for more organic tag usage in the middle of a conversation.

#### Example

```txt title="Discord Message"
Hello there new person. Have you checked out $funstufftodo here yet?
```

## Dashboard
A guilds tags can be viewed from the tag tab on the dashboard. You can filter tags, create new tags or just view what tags have been created.

## Commands

### Tag
If invoked with no tag name it will show all tags in the server. If a name is provided it will attempt to invoke that tag

#### Aliases
* `tags`

#### Format
```txt title="List all tags in the server"
!tag
```

```txt title="Invoke a given tag"
!tag <tagname>
```
#### Example

```
!tag
```

```
!tag mytagname
```

### Add
Create a tag in the server

#### Aliases
* `create`
* `make`

#### Required [Claims](./Claims.md)
* `tag_add`

#### Format

```
!tag add <TagName> <TagContent>
```
#### Example

```
!tag add MyTag ClemBot is an awesome bot!
```

### Remove
Delete a tag from the server

#### Aliases
* `delete`
* `remove`

#### Required [Claims](./Claims.md)
* `tag_delete`

:::note
You do not need the `tag_delete` claim to delete a tag that you own
:::

#### Format

```
!tag delete <TagName>
```
#### Example

```
!tag delete MyTag
```

### Edit
Edit a tag in the server.

#### Format

```
!tag edit <TagName> <NewTagContent>
```
#### Example

```
!tag edit MyTag ClemBot is an super super super awesome bot!
```
### Info
Gets info about a given tag in a server

#### Aliases
* `about`

#### Format
```
!tag info <TagName>
```
#### Example

```
!tag info MyTag
```

### Claim
Claims a given unowned tag 

#### Format
```
!tag claim <TagName>
```
#### Example

```
!tag claim SomeUnownedTag
```

### Transfer
Transers a given owned tag to a new owner in the same server

#### Format
```
!tag transfer <TagName> <TagRecipient>
```
#### Example

```
!tag transfer MyTag @MyBestFriend
```

### Unclaimed
Lists all unclaimed tags in the server

#### Example

```
!tag unclaimed
```
