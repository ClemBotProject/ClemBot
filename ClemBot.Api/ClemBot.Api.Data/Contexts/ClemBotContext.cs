using ClemBot.Api.Data.Enums;
using ClemBot.Api.Data.Models;
using Microsoft.EntityFrameworkCore;
using Npgsql;

namespace ClemBot.Api.Data.Contexts
{
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
        }

        public DbSet<Channel> Channels { get; set; }
        public DbSet<ClaimsMapping> ClaimsMappings { get; set; }
        public DbSet<CustomPrefix> CustomPrefixs { get; set; }
        public DbSet<DesignatedChannelMapping> DesignatedChannelMappings { get; set; }
        public DbSet<Guild> Guilds { get; set; }
        public DbSet<Infraction> Infractions { get; set; }
        public DbSet<Message> Messages { get; set; }
        public DbSet<MessageContent> MessageContents { get; set; }
        public DbSet<Reminder> Reminders { get; set; }
        public DbSet<Role> Roles { get; set; }
        public DbSet<Tag> Tags { get; set; }
        public DbSet<TagUse> TagUses { get; set; }
        public DbSet<User> Users { get; set; }

        protected override void OnModelCreating(ModelBuilder modelBuilder)
        {
            modelBuilder.Entity<Role>()
                .Property(p => p.IsAssignable)
                .HasDefaultValue(true);

            modelBuilder.HasPostgresEnum<BotAuthClaims>();
            modelBuilder.HasPostgresEnum<DesignatedChannels>();
            modelBuilder.HasPostgresEnum<InfractionType>();
        }
    }
}
