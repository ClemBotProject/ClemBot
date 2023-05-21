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

    public DbSet<Channel> Channels { get; set; } = null!;
    public DbSet<ClaimsMapping> ClaimsMappings { get; set; } = null!;
    public DbSet<CommandRestriction> CommandRestrictions { get; set; } = null!;
    public DbSet<CustomPrefix> CustomPrefixs { get; set; } = null!;
    public DbSet<CustomTagPrefix> CustomTagPrefixs { get; set; } = null!;
    public DbSet<CommandInvocation> CommandInvocations { get; set; } = null!;
    public DbSet<DesignatedChannelMapping> DesignatedChannelMappings { get; set; } = null!;
    public DbSet<EmoteBoard> EmoteBoards { get; set; } = null!;
    public DbSet<EmoteBoardChannelMapping> EmoteBoardChannelMappings { get; set; } = null!;
    public DbSet<EmoteBoardMessage> EmoteBoardMessages { get; set; } = null!;
    public DbSet<EmoteBoardPost> EmoteBoardPosts { get; set; } = null!;
    public DbSet<EmoteBoardReaction> EmoteBoardReactions { get; set; } = null!;
    public DbSet<Guild> Guilds { get; set; } = null!;
    public DbSet<GuildSetting> GuildSettings { get; set; } = null!;
    public DbSet<GuildUser> GuildUser { get; set; } = null!;
    public DbSet<Infraction> Infractions { get; set; } = null!;
    public DbSet<Message> Messages { get; set; } = null!;
    public DbSet<MessageContent> MessageContents { get; set; } = null!;
    public DbSet<Reminder> Reminders { get; set; } = null!;
    public DbSet<Role> Roles { get; set; } = null!;
    public DbSet<RoleUser> RoleUser { get; set; } = null!;
    public DbSet<Tag> Tags { get; set; } = null!;
    public DbSet<TagUse> TagUses { get; set; } = null!;
    public DbSet<SlotScore> SlotScores { get; set; } = null!;
    public DbSet<User> Users { get; set; } = null!;

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

        modelBuilder.Entity<EmoteBoardReaction>().HasKey(r => new
        {
            r.UserId, r.EmoteBoardPostId
        });

        modelBuilder.Entity<EmoteBoardChannelMapping>().HasKey(cm => new
        {
            cm.ChannelId, cm.EmoteBoardId
        });

        modelBuilder.HasPostgresEnum<BotAuthClaims>();
        modelBuilder.HasPostgresEnum<DesignatedChannels>();
        modelBuilder.HasPostgresEnum<InfractionType>();
        modelBuilder.HasPostgresEnum<CommandRestrictionType>();
        modelBuilder.HasPostgresEnum<ConfigSettings>();
    }
}
