import typing as t

import discord


def log_guild(guild: discord.Guild) -> dict[str, t.Any]:
    return {"id": guild.id, "name": guild.name}


def log_user(member: discord.Member | discord.User | discord.ClientUser) -> dict[str, t.Any]:
    return (
        {"id": member.id, "name": member.name, "guild": log_guild(member.guild)}
        if isinstance(member, discord.Member)
        else {
            "id": member.id,
            "name": member.name,
        }
    )


def log_message(message: discord.Message) -> dict[str, t.Any]:
    return {"author": log_user(message.author), "content": message.content}


def log_channel(channel: t.Any) -> dict[str, t.Any]:
    id = getattr(channel, "id", None)
    name = getattr(channel, "name", str(channel))
    guild = getattr(channel, "guild", None)

    return {"id": id, "name": name, "guild": log_guild(guild) if guild else None}


def log_role(role: discord.Role) -> dict[str, t.Any]:
    return {"id": role.id, "name": role.name, "guild": log_guild(role.guild)}
