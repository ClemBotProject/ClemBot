﻿// <auto-generated />
using System;
using ClemBot.Api.Common.Enums;
using ClemBot.Api.Data.Contexts;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Infrastructure;
using Microsoft.EntityFrameworkCore.Storage.ValueConversion;
using NodaTime;
using Npgsql.EntityFrameworkCore.PostgreSQL.Metadata;

#nullable disable

namespace ClemBot.Api.Data.Migrations
{
    [DbContext(typeof(ClemBotContext))]
    partial class ClemBotContextModelSnapshot : ModelSnapshot
    {
        protected override void BuildModel(ModelBuilder modelBuilder)
        {
#pragma warning disable 612, 618
            modelBuilder
                .HasAnnotation("ProductVersion", "6.0.0")
                .HasAnnotation("Relational:MaxIdentifierLength", 63);

            NpgsqlModelBuilderExtensions.HasPostgresEnum(modelBuilder, "bot_auth_claims", new[] { "designated_channel_view", "designated_channel_modify", "custom_prefix_set", "welcome_message_view", "welcome_message_modify", "tag_add", "tag_delete", "assignable_roles_add", "assignable_roles_delete", "delete_message", "emote_add", "claims_view", "claims_modify", "manage_class_add", "moderation_warn", "moderation_ban", "moderation_mute", "moderation_purge", "moderation_infraction_view", "moderation_infraction_view_self", "dashboard_view", "dashboard_edit", "guild_settings_view", "guild_settings_edit", "custom_tag_prefix_set" });
            NpgsqlModelBuilderExtensions.HasPostgresEnum(modelBuilder, "config_settings", new[] { "allow_embed_links" });
            NpgsqlModelBuilderExtensions.HasPostgresEnum(modelBuilder, "designated_channels", new[] { "message_log", "moderation_log", "user_join_log", "user_leave_log", "starboard", "server_join_log", "bot_dm_log" });
            NpgsqlModelBuilderExtensions.HasPostgresEnum(modelBuilder, "infraction_type", new[] { "ban", "mute", "warn" });
            NpgsqlModelBuilderExtensions.UseIdentityByDefaultColumns(modelBuilder);

            modelBuilder.Entity("ClemBot.Api.Data.Models.Channel", b =>
                {
                    b.Property<decimal>("Id")
                        .ValueGeneratedOnAdd()
                        .HasColumnType("numeric(20,0)");

                    b.Property<decimal>("GuildId")
                        .HasColumnType("numeric(20,0)");

                    b.Property<bool>("IsThread")
                        .ValueGeneratedOnAddOrUpdate()
                        .HasColumnType("boolean")
                        .HasComputedColumnSql("\"Channels\".\"ParentId\" IS NOT null", true);

                    b.Property<string>("Name")
                        .HasColumnType("text");

                    b.Property<decimal?>("ParentId")
                        .HasColumnType("numeric(20,0)");

                    b.HasKey("Id");

                    b.HasIndex("GuildId");

                    b.HasIndex("ParentId");

                    b.ToTable("Channels");
                });

            modelBuilder.Entity("ClemBot.Api.Data.Models.ClaimsMapping", b =>
                {
                    b.Property<int>("Id")
                        .ValueGeneratedOnAdd()
                        .HasColumnType("integer");

                    NpgsqlPropertyBuilderExtensions.UseIdentityByDefaultColumn(b.Property<int>("Id"));

                    b.Property<BotAuthClaims>("Claim")
                        .HasColumnType("bot_auth_claims");

                    b.Property<decimal>("RoleId")
                        .HasColumnType("numeric(20,0)");

                    b.HasKey("Id");

                    b.HasIndex("RoleId");

                    b.ToTable("ClaimsMappings");
                });

            modelBuilder.Entity("ClemBot.Api.Data.Models.CommandInvocation", b =>
                {
                    b.Property<int>("Id")
                        .ValueGeneratedOnAdd()
                        .HasColumnType("integer");

                    NpgsqlPropertyBuilderExtensions.UseIdentityByDefaultColumn(b.Property<int>("Id"));

                    b.Property<decimal>("ChannelId")
                        .HasColumnType("numeric(20,0)");

                    b.Property<string>("CommandName")
                        .HasColumnType("text");

                    b.Property<decimal>("GuildId")
                        .HasColumnType("numeric(20,0)");

                    b.Property<LocalDateTime>("Time")
                        .HasColumnType("timestamp without time zone");

                    b.Property<decimal>("UserId")
                        .HasColumnType("numeric(20,0)");

                    b.HasKey("Id");

                    b.ToTable("CommandInvocations");
                });

            modelBuilder.Entity("ClemBot.Api.Data.Models.CustomPrefix", b =>
                {
                    b.Property<int>("Id")
                        .ValueGeneratedOnAdd()
                        .HasColumnType("integer");

                    NpgsqlPropertyBuilderExtensions.UseIdentityByDefaultColumn(b.Property<int>("Id"));

                    b.Property<decimal>("GuildId")
                        .HasColumnType("numeric(20,0)");

                    b.Property<string>("Prefix")
                        .HasColumnType("text");

                    b.HasKey("Id");

                    b.HasIndex("GuildId");

                    b.ToTable("CustomPrefixs");
                });

            modelBuilder.Entity("ClemBot.Api.Data.Models.CustomTagPrefix", b =>
                {
                    b.Property<int>("Id")
                        .ValueGeneratedOnAdd()
                        .HasColumnType("integer");

                    NpgsqlPropertyBuilderExtensions.UseIdentityByDefaultColumn(b.Property<int>("Id"));

                    b.Property<decimal>("GuildId")
                        .HasColumnType("numeric(20,0)");

                    b.Property<string>("TagPrefix")
                        .HasColumnType("text");

                    b.HasKey("Id");

                    b.HasIndex("GuildId");

                    b.ToTable("CustomTagPrefixs");
                });

            modelBuilder.Entity("ClemBot.Api.Data.Models.DesignatedChannelMapping", b =>
                {
                    b.Property<int>("Id")
                        .ValueGeneratedOnAdd()
                        .HasColumnType("integer");

                    NpgsqlPropertyBuilderExtensions.UseIdentityByDefaultColumn(b.Property<int>("Id"));

                    b.Property<decimal>("ChannelId")
                        .HasColumnType("numeric(20,0)");

                    b.Property<DesignatedChannels>("Type")
                        .HasColumnType("designated_channels");

                    b.HasKey("Id");

                    b.HasIndex("ChannelId");

                    b.ToTable("DesignatedChannelMappings");
                });

            modelBuilder.Entity("ClemBot.Api.Data.Models.Guild", b =>
                {
                    b.Property<decimal>("Id")
                        .ValueGeneratedOnAdd()
                        .HasColumnType("numeric(20,0)");

                    b.Property<string>("Name")
                        .HasColumnType("text");

                    b.Property<decimal>("OwnerId")
                        .HasColumnType("numeric(20,0)");

                    b.Property<string>("WelcomeMessage")
                        .HasColumnType("text");

                    b.HasKey("Id");

                    b.ToTable("Guilds");
                });

            modelBuilder.Entity("ClemBot.Api.Data.Models.GuildSetting", b =>
                {
                    b.Property<int>("Id")
                        .ValueGeneratedOnAdd()
                        .HasColumnType("integer");

                    NpgsqlPropertyBuilderExtensions.UseIdentityByDefaultColumn(b.Property<int>("Id"));

                    b.Property<decimal>("GuildId")
                        .HasColumnType("numeric(20,0)");

                    b.Property<ConfigSettings>("Setting")
                        .HasColumnType("config_settings");

                    b.Property<string>("Value")
                        .HasColumnType("text");

                    b.HasKey("Id");

                    b.HasIndex("GuildId");

                    b.ToTable("GuildSettings");
                });

            modelBuilder.Entity("ClemBot.Api.Data.Models.GuildUser", b =>
                {
                    b.Property<decimal>("GuildId")
                        .HasColumnType("numeric(20,0)");

                    b.Property<decimal>("UserId")
                        .HasColumnType("numeric(20,0)");

                    b.HasKey("GuildId", "UserId");

                    b.HasIndex("UserId");

                    b.ToTable("GuildUser");
                });

            modelBuilder.Entity("ClemBot.Api.Data.Models.Infraction", b =>
                {
                    b.Property<int>("Id")
                        .ValueGeneratedOnAdd()
                        .HasColumnType("integer");

                    NpgsqlPropertyBuilderExtensions.UseIdentityByDefaultColumn(b.Property<int>("Id"));

                    b.Property<decimal>("AuthorId")
                        .HasColumnType("numeric(20,0)");

                    b.Property<LocalDateTime?>("Duration")
                        .HasColumnType("timestamp without time zone");

                    b.Property<decimal>("GuildId")
                        .HasColumnType("numeric(20,0)");

                    b.Property<bool?>("IsActive")
                        .HasColumnType("boolean");

                    b.Property<string>("Reason")
                        .HasColumnType("text");

                    b.Property<decimal>("SubjectId")
                        .HasColumnType("numeric(20,0)");

                    b.Property<LocalDateTime>("Time")
                        .HasColumnType("timestamp without time zone");

                    b.Property<InfractionType>("Type")
                        .HasColumnType("infraction_type");

                    b.HasKey("Id");

                    b.HasIndex("AuthorId");

                    b.HasIndex("GuildId");

                    b.HasIndex("SubjectId");

                    b.ToTable("Infractions");
                });

            modelBuilder.Entity("ClemBot.Api.Data.Models.Message", b =>
                {
                    b.Property<decimal>("Id")
                        .ValueGeneratedOnAdd()
                        .HasColumnType("numeric(20,0)");

                    b.Property<decimal>("ChannelId")
                        .HasColumnType("numeric(20,0)");

                    b.Property<decimal>("GuildId")
                        .HasColumnType("numeric(20,0)");

                    b.Property<decimal>("UserId")
                        .HasColumnType("numeric(20,0)");

                    b.HasKey("Id");

                    b.HasIndex("ChannelId");

                    b.HasIndex("GuildId");

                    b.HasIndex("UserId");

                    b.ToTable("Messages");
                });

            modelBuilder.Entity("ClemBot.Api.Data.Models.MessageContent", b =>
                {
                    b.Property<int>("Id")
                        .ValueGeneratedOnAdd()
                        .HasColumnType("integer");

                    NpgsqlPropertyBuilderExtensions.UseIdentityByDefaultColumn(b.Property<int>("Id"));

                    b.Property<string>("Content")
                        .HasColumnType("text");

                    b.Property<decimal>("MessageId")
                        .HasColumnType("numeric(20,0)");

                    b.Property<LocalDateTime>("Time")
                        .HasColumnType("timestamp without time zone");

                    b.HasKey("Id");

                    b.HasIndex("MessageId");

                    b.ToTable("MessageContents");
                });

            modelBuilder.Entity("ClemBot.Api.Data.Models.Reminder", b =>
                {
                    b.Property<int>("Id")
                        .ValueGeneratedOnAdd()
                        .HasColumnType("integer");

                    NpgsqlPropertyBuilderExtensions.UseIdentityByDefaultColumn(b.Property<int>("Id"));

                    b.Property<string>("Content")
                        .HasColumnType("text");

                    b.Property<bool>("Dispatched")
                        .HasColumnType("boolean");

                    b.Property<string>("Link")
                        .HasColumnType("text");

                    b.Property<LocalDateTime>("Time")
                        .HasColumnType("timestamp without time zone");

                    b.Property<decimal>("UserId")
                        .HasColumnType("numeric(20,0)");

                    b.HasKey("Id");

                    b.HasIndex("UserId");

                    b.ToTable("Reminders");
                });

            modelBuilder.Entity("ClemBot.Api.Data.Models.Role", b =>
                {
                    b.Property<decimal>("Id")
                        .ValueGeneratedOnAdd()
                        .HasColumnType("numeric(20,0)");

                    b.Property<bool>("Admin")
                        .HasColumnType("boolean");

                    b.Property<decimal>("GuildId")
                        .HasColumnType("numeric(20,0)");

                    b.Property<bool?>("IsAssignable")
                        .ValueGeneratedOnAdd()
                        .HasColumnType("boolean")
                        .HasDefaultValue(true);

                    b.Property<string>("Name")
                        .HasColumnType("text");

                    b.HasKey("Id");

                    b.HasIndex("GuildId");

                    b.ToTable("Roles");
                });

            modelBuilder.Entity("ClemBot.Api.Data.Models.RoleUser", b =>
                {
                    b.Property<decimal>("RoleId")
                        .HasColumnType("numeric(20,0)");

                    b.Property<decimal>("UserId")
                        .HasColumnType("numeric(20,0)");

                    b.HasKey("RoleId", "UserId");

                    b.HasIndex("UserId");

                    b.ToTable("RoleUser");
                });

            modelBuilder.Entity("ClemBot.Api.Data.Models.SlotScore", b =>
                {
                    b.Property<int>("Id")
                        .ValueGeneratedOnAdd()
                        .HasColumnType("integer");

                    NpgsqlPropertyBuilderExtensions.UseIdentityByDefaultColumn(b.Property<int>("Id"));

                    b.Property<decimal>("GuildId")
                        .HasColumnType("numeric(20,0)");

                    b.Property<decimal>("Score")
                        .HasColumnType("numeric(20,0)");

                    b.Property<LocalDateTime>("Time")
                        .HasColumnType("timestamp without time zone");

                    b.Property<decimal>("UserId")
                        .HasColumnType("numeric(20,0)");

                    b.HasKey("Id");

                    b.HasIndex("GuildId");

                    b.HasIndex("UserId");

                    b.ToTable("SlotScores");
                });

            modelBuilder.Entity("ClemBot.Api.Data.Models.Tag", b =>
                {
                    b.Property<int>("Id")
                        .ValueGeneratedOnAdd()
                        .HasColumnType("integer");

                    NpgsqlPropertyBuilderExtensions.UseIdentityByDefaultColumn(b.Property<int>("Id"));

                    b.Property<string>("Content")
                        .HasColumnType("text");

                    b.Property<decimal>("GuildId")
                        .HasColumnType("numeric(20,0)");

                    b.Property<string>("Name")
                        .HasColumnType("text");

                    b.Property<LocalDateTime>("Time")
                        .HasColumnType("timestamp without time zone");

                    b.Property<decimal>("UserId")
                        .HasColumnType("numeric(20,0)");

                    b.HasKey("Id");

                    b.HasIndex("GuildId");

                    b.HasIndex("UserId");

                    b.ToTable("Tags");
                });

            modelBuilder.Entity("ClemBot.Api.Data.Models.TagUse", b =>
                {
                    b.Property<int>("Id")
                        .ValueGeneratedOnAdd()
                        .HasColumnType("integer");

                    NpgsqlPropertyBuilderExtensions.UseIdentityByDefaultColumn(b.Property<int>("Id"));

                    b.Property<decimal>("ChannelId")
                        .HasColumnType("numeric(20,0)");

                    b.Property<int>("TagId")
                        .HasColumnType("integer");

                    b.Property<DateTime>("Time")
                        .HasColumnType("timestamp with time zone");

                    b.Property<decimal>("UserId")
                        .HasColumnType("numeric(20,0)");

                    b.HasKey("Id");

                    b.HasIndex("ChannelId");

                    b.HasIndex("TagId");

                    b.HasIndex("UserId");

                    b.ToTable("TagUses");
                });

            modelBuilder.Entity("ClemBot.Api.Data.Models.User", b =>
                {
                    b.Property<decimal>("Id")
                        .ValueGeneratedOnAdd()
                        .HasColumnType("numeric(20,0)");

                    b.Property<string>("Name")
                        .HasColumnType("text");

                    b.HasKey("Id");

                    b.ToTable("Users");
                });

            modelBuilder.Entity("ClemBot.Api.Data.Models.Channel", b =>
                {
                    b.HasOne("ClemBot.Api.Data.Models.Guild", "Guild")
                        .WithMany("Channels")
                        .HasForeignKey("GuildId")
                        .OnDelete(DeleteBehavior.Cascade)
                        .IsRequired();

                    b.HasOne("ClemBot.Api.Data.Models.Channel", "Parent")
                        .WithMany()
                        .HasForeignKey("ParentId");

                    b.Navigation("Guild");

                    b.Navigation("Parent");
                });

            modelBuilder.Entity("ClemBot.Api.Data.Models.ClaimsMapping", b =>
                {
                    b.HasOne("ClemBot.Api.Data.Models.Role", "Role")
                        .WithMany("Claims")
                        .HasForeignKey("RoleId")
                        .OnDelete(DeleteBehavior.Cascade)
                        .IsRequired();

                    b.Navigation("Role");
                });

            modelBuilder.Entity("ClemBot.Api.Data.Models.CustomPrefix", b =>
                {
                    b.HasOne("ClemBot.Api.Data.Models.Guild", "Guild")
                        .WithMany("CustomPrefixes")
                        .HasForeignKey("GuildId")
                        .OnDelete(DeleteBehavior.Cascade)
                        .IsRequired();

                    b.Navigation("Guild");
                });

            modelBuilder.Entity("ClemBot.Api.Data.Models.CustomTagPrefix", b =>
                {
                    b.HasOne("ClemBot.Api.Data.Models.Guild", "Guild")
                        .WithMany("CustomTagPrefixes")
                        .HasForeignKey("GuildId")
                        .OnDelete(DeleteBehavior.Cascade)
                        .IsRequired();

                    b.Navigation("Guild");
                });

            modelBuilder.Entity("ClemBot.Api.Data.Models.DesignatedChannelMapping", b =>
                {
                    b.HasOne("ClemBot.Api.Data.Models.Channel", "Channel")
                        .WithMany("DesignatedChannels")
                        .HasForeignKey("ChannelId")
                        .OnDelete(DeleteBehavior.Cascade)
                        .IsRequired();

                    b.Navigation("Channel");
                });

            modelBuilder.Entity("ClemBot.Api.Data.Models.GuildSetting", b =>
                {
                    b.HasOne("ClemBot.Api.Data.Models.Guild", "Guild")
                        .WithMany("GuildSettings")
                        .HasForeignKey("GuildId")
                        .OnDelete(DeleteBehavior.Cascade)
                        .IsRequired();

                    b.Navigation("Guild");
                });

            modelBuilder.Entity("ClemBot.Api.Data.Models.GuildUser", b =>
                {
                    b.HasOne("ClemBot.Api.Data.Models.Guild", "Guild")
                        .WithMany("GuildUsers")
                        .HasForeignKey("GuildId")
                        .OnDelete(DeleteBehavior.Cascade)
                        .IsRequired();

                    b.HasOne("ClemBot.Api.Data.Models.User", "User")
                        .WithMany("GuildUsers")
                        .HasForeignKey("UserId")
                        .OnDelete(DeleteBehavior.Cascade)
                        .IsRequired();

                    b.Navigation("Guild");

                    b.Navigation("User");
                });

            modelBuilder.Entity("ClemBot.Api.Data.Models.Infraction", b =>
                {
                    b.HasOne("ClemBot.Api.Data.Models.User", "Author")
                        .WithMany()
                        .HasForeignKey("AuthorId")
                        .OnDelete(DeleteBehavior.Cascade)
                        .IsRequired();

                    b.HasOne("ClemBot.Api.Data.Models.Guild", "Guild")
                        .WithMany("Infractions")
                        .HasForeignKey("GuildId")
                        .OnDelete(DeleteBehavior.Cascade)
                        .IsRequired();

                    b.HasOne("ClemBot.Api.Data.Models.User", "Subject")
                        .WithMany()
                        .HasForeignKey("SubjectId")
                        .OnDelete(DeleteBehavior.Cascade)
                        .IsRequired();

                    b.Navigation("Author");

                    b.Navigation("Guild");

                    b.Navigation("Subject");
                });

            modelBuilder.Entity("ClemBot.Api.Data.Models.Message", b =>
                {
                    b.HasOne("ClemBot.Api.Data.Models.Channel", "Channel")
                        .WithMany("Messages")
                        .HasForeignKey("ChannelId")
                        .OnDelete(DeleteBehavior.Cascade)
                        .IsRequired();

                    b.HasOne("ClemBot.Api.Data.Models.Guild", "Guild")
                        .WithMany("Messages")
                        .HasForeignKey("GuildId")
                        .OnDelete(DeleteBehavior.Cascade)
                        .IsRequired();

                    b.HasOne("ClemBot.Api.Data.Models.User", "User")
                        .WithMany("Messages")
                        .HasForeignKey("UserId")
                        .OnDelete(DeleteBehavior.Cascade)
                        .IsRequired();

                    b.Navigation("Channel");

                    b.Navigation("Guild");

                    b.Navigation("User");
                });

            modelBuilder.Entity("ClemBot.Api.Data.Models.MessageContent", b =>
                {
                    b.HasOne("ClemBot.Api.Data.Models.Message", "Message")
                        .WithMany("Contents")
                        .HasForeignKey("MessageId")
                        .OnDelete(DeleteBehavior.Cascade)
                        .IsRequired();

                    b.Navigation("Message");
                });

            modelBuilder.Entity("ClemBot.Api.Data.Models.Reminder", b =>
                {
                    b.HasOne("ClemBot.Api.Data.Models.User", "User")
                        .WithMany()
                        .HasForeignKey("UserId")
                        .OnDelete(DeleteBehavior.Cascade)
                        .IsRequired();

                    b.Navigation("User");
                });

            modelBuilder.Entity("ClemBot.Api.Data.Models.Role", b =>
                {
                    b.HasOne("ClemBot.Api.Data.Models.Guild", "Guild")
                        .WithMany("Roles")
                        .HasForeignKey("GuildId")
                        .OnDelete(DeleteBehavior.Cascade)
                        .IsRequired();

                    b.Navigation("Guild");
                });

            modelBuilder.Entity("ClemBot.Api.Data.Models.RoleUser", b =>
                {
                    b.HasOne("ClemBot.Api.Data.Models.Role", "Role")
                        .WithMany("RoleUsers")
                        .HasForeignKey("RoleId")
                        .OnDelete(DeleteBehavior.Cascade)
                        .IsRequired();

                    b.HasOne("ClemBot.Api.Data.Models.User", "User")
                        .WithMany("RoleUsers")
                        .HasForeignKey("UserId")
                        .OnDelete(DeleteBehavior.Cascade)
                        .IsRequired();

                    b.Navigation("Role");

                    b.Navigation("User");
                });

            modelBuilder.Entity("ClemBot.Api.Data.Models.SlotScore", b =>
                {
                    b.HasOne("ClemBot.Api.Data.Models.Guild", "Guild")
                        .WithMany()
                        .HasForeignKey("GuildId")
                        .OnDelete(DeleteBehavior.Cascade)
                        .IsRequired();

                    b.HasOne("ClemBot.Api.Data.Models.User", "User")
                        .WithMany()
                        .HasForeignKey("UserId")
                        .OnDelete(DeleteBehavior.Cascade)
                        .IsRequired();

                    b.Navigation("Guild");

                    b.Navigation("User");
                });

            modelBuilder.Entity("ClemBot.Api.Data.Models.Tag", b =>
                {
                    b.HasOne("ClemBot.Api.Data.Models.Guild", "Guild")
                        .WithMany("Tags")
                        .HasForeignKey("GuildId")
                        .OnDelete(DeleteBehavior.Cascade)
                        .IsRequired();

                    b.HasOne("ClemBot.Api.Data.Models.User", "User")
                        .WithMany("Tags")
                        .HasForeignKey("UserId")
                        .OnDelete(DeleteBehavior.Cascade)
                        .IsRequired();

                    b.Navigation("Guild");

                    b.Navigation("User");
                });

            modelBuilder.Entity("ClemBot.Api.Data.Models.TagUse", b =>
                {
                    b.HasOne("ClemBot.Api.Data.Models.Channel", "Channel")
                        .WithMany()
                        .HasForeignKey("ChannelId")
                        .OnDelete(DeleteBehavior.Cascade)
                        .IsRequired();

                    b.HasOne("ClemBot.Api.Data.Models.Tag", "Tag")
                        .WithMany("TagUses")
                        .HasForeignKey("TagId")
                        .OnDelete(DeleteBehavior.Cascade)
                        .IsRequired();

                    b.HasOne("ClemBot.Api.Data.Models.User", "User")
                        .WithMany()
                        .HasForeignKey("UserId")
                        .OnDelete(DeleteBehavior.Cascade)
                        .IsRequired();

                    b.Navigation("Channel");

                    b.Navigation("Tag");

                    b.Navigation("User");
                });

            modelBuilder.Entity("ClemBot.Api.Data.Models.Channel", b =>
                {
                    b.Navigation("DesignatedChannels");

                    b.Navigation("Messages");
                });

            modelBuilder.Entity("ClemBot.Api.Data.Models.Guild", b =>
                {
                    b.Navigation("Channels");

                    b.Navigation("CustomPrefixes");

                    b.Navigation("CustomTagPrefixes");

                    b.Navigation("GuildSettings");

                    b.Navigation("GuildUsers");

                    b.Navigation("Infractions");

                    b.Navigation("Messages");

                    b.Navigation("Roles");

                    b.Navigation("Tags");
                });

            modelBuilder.Entity("ClemBot.Api.Data.Models.Message", b =>
                {
                    b.Navigation("Contents");
                });

            modelBuilder.Entity("ClemBot.Api.Data.Models.Role", b =>
                {
                    b.Navigation("Claims");

                    b.Navigation("RoleUsers");
                });

            modelBuilder.Entity("ClemBot.Api.Data.Models.Tag", b =>
                {
                    b.Navigation("TagUses");
                });

            modelBuilder.Entity("ClemBot.Api.Data.Models.User", b =>
                {
                    b.Navigation("GuildUsers");

                    b.Navigation("Messages");

                    b.Navigation("RoleUsers");

                    b.Navigation("Tags");
                });
#pragma warning restore 612, 618
        }
    }
}
