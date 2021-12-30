import discord


def log_guild(guild: discord.Guild):
    return {
        'id': guild.id,
        'name': guild.name
    }


def log_member(member: discord.Member):
    return {
        'id': member.id,
        'name': member.name,
        'guild': log_guild(member.guild)
    }


def log_user(user: discord.User):
    return {
        'id': user.id,
        'name': user.name,
    }


def log_channel(channel: discord.TextChannel):
    return {
        'id': channel.id,
        'name': channel.name,
        'guild': log_guild(channel.guild)
    }


def log_role(role: discord.Role):
    return {
        'id': role.id,
        'name': role.name,
        'guild': log_guild(role.guild)
    }
