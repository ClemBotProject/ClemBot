using ClemBot.Api.Common.Enums;
using ClemBot.Api.Data.Models;
using Microsoft.EntityFrameworkCore;
using Npgsql;

namespace ClemBot.Api.Data.Contexts;

public class ClemBotContext : DbContext
{
    public ClemBotContext(DbContextOptions<ClemBotContext> options)
        : base(options)
    {
    }

    static ClemBotContext()
    {
        NpgsqlConnection.GlobalTypeMapper.MapEnum<BotAuthClaims>();
        NpgsqlConnection.GlobalTypeMapper.MapEnum<DesignatedChannels>();
        NpgsqlConnection.GlobalTypeMapper.MapEnum<InfractionType>();
        NpgsqlConnection.GlobalTypeMapper.MapEnum<CommandRestrictionType>();
        NpgsqlConnection.GlobalTypeMapper.MapEnum<ConfigSettings>();
    }

    public DbSet<Channel> Channels => Set<Channel>();
    public DbSet<ClaimsMapping> ClaimsMappings => Set<ClaimsMapping>();
    public DbSet<CommandRestriction> CommandRestrictions => Set<CommandRestriction>();
    public DbSet<CustomPrefix> CustomPrefixs => Set<CustomPrefix>();
    public DbSet<CustomTagPrefix> CustomTagPrefixs => Set<CustomTagPrefix>();
    public DbSet<CommandInvocation> CommandInvocations => Set<CommandInvocation>();
    public DbSet<DesignatedChannelMapping> DesignatedChannelMappings => Set<DesignatedChannelMapping>();
    public DbSet<Guild> Guilds => Set<Guild>();
    public DbSet<GuildSetting> GuildSettings => Set<GuildSetting>();
    public DbSet<GuildUser> GuildUser => Set<GuildUser>();
    public DbSet<Infraction> Infractions => Set<Infraction>();
    public DbSet<Message> Messages => Set<Message>();
    public DbSet<MessageContent> MessageContents => Set<MessageContent>();
    public DbSet<Reminder> Reminders => Set<Reminder>();
    public DbSet<Role> Roles => Set<Role>();
    public DbSet<RoleUser> RoleUser => Set<RoleUser>();
    public DbSet<Tag> Tags => Set<Tag>();
    public DbSet<TagUse> TagUses => Set<TagUse>();
    public DbSet<SlotScore> SlotScores => Set<SlotScore>();
    public DbSet<User> Users => Set<User>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<Guild>()
            .HasMany(p => p.Users)
            .WithMany(p => p.Guilds)
            .UsingEntity<GuildUser>(
                j => j
                    .HasOne(pt => pt.User)
                    .WithMany(t => t.GuildUsers)
                    .HasForeignKey(pt => pt.UserId),
                j => j
                    .HasOne(pt => pt.Guild)
                    .WithMany(p => p.GuildUsers)
                    .HasForeignKey(pt => pt.GuildId));

        modelBuilder.Entity<Role>()
            .HasMany(p => p.Users)
            .WithMany(p => p.Roles)
            .UsingEntity<RoleUser>(
                j => j
                    .HasOne(pt => pt.User)
                    .WithMany(t => t.RoleUsers)
                    .HasForeignKey(pt => pt.UserId),
                j => j
                    .HasOne(pt => pt.Role)
                    .WithMany(p => p.RoleUsers)
                    .HasForeignKey(pt => pt.RoleId));

        modelBuilder.Entity<Channel>()
            .Property(e => e.IsThread)
            .HasComputedColumnSql(@"""Channels"".""ParentId"" IS NOT null", stored: true);

        modelBuilder.HasPostgresEnum<BotAuthClaims>();
        modelBuilder.HasPostgresEnum<DesignatedChannels>();
        modelBuilder.HasPostgresEnum<InfractionType>();
        modelBuilder.HasPostgresEnum<CommandRestrictionType>();
        modelBuilder.HasPostgresEnum<ConfigSettings>();
    }
}
