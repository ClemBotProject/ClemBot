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
        NpgsqlConnection.GlobalTypeMapper.MapEnum<ConfigSettings>();
    }

    public DbSet<Channel> Channels { get; set; }
    public DbSet<ClaimsMapping> ClaimsMappings { get; set; }
    public DbSet<CustomPrefix> CustomPrefixs { get; set; }
    public DbSet<CustomTagPrefix> CustomTagPrefixs { get; set; }
    public DbSet<CommandInvocation> CommandInvocations { get; set; }
    public DbSet<DesignatedChannelMapping> DesignatedChannelMappings { get; set; }
    public DbSet<Guild> Guilds { get; set; }
    public DbSet<GuildSetting> GuildSettings { get; set; }
    public DbSet<GuildUser> GuildUser { get; set; }
    public DbSet<Infraction> Infractions { get; set; }
    public DbSet<Message> Messages { get; set; }
    public DbSet<MessageContent> MessageContents { get; set; }
    public DbSet<Reminder> Reminders { get; set; }
    public DbSet<Role> Roles { get; set; }
    public DbSet<RoleUser> RoleUser { get; set; }
    public DbSet<Tag> Tags { get; set; }
    public DbSet<TagUse> TagUses { get; set; }
    public DbSet<SlotScore> SlotScores { get; set; }
    public DbSet<User> Users { get; set; }

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<Role>()
            .Property(p => p.IsAssignable)
            .HasDefaultValue(true);

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
        modelBuilder.HasPostgresEnum<ConfigSettings>();
    }
}
