using Microsoft.EntityFrameworkCore.Migrations;
using Npgsql.EntityFrameworkCore.PostgreSQL.Metadata;

#nullable disable

namespace ClemBot.Api.Data.Migrations
{
    public partial class AddCommandRestrictions : Migration
    {
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AlterDatabase()
                .Annotation("Npgsql:Enum:bot_auth_claims", "designated_channel_view,designated_channel_modify,custom_prefix_set,welcome_message_view,welcome_message_modify,tag_add,tag_delete,assignable_roles_add,assignable_roles_delete,delete_message,emote_add,claims_view,claims_modify,manage_class_add,moderation_warn,moderation_ban,moderation_mute,moderation_purge,moderation_infraction_view,moderation_infraction_view_self,dashboard_view,dashboard_edit,guild_settings_view,guild_settings_edit,custom_tag_prefix_set,manage_commands,bypass_disabled_commands")
                .Annotation("Npgsql:Enum:config_settings", "allow_embed_links")
                .Annotation("Npgsql:Enum:designated_channels", "message_log,moderation_log,user_join_log,user_leave_log,starboard,server_join_log,bot_dm_log")
                .Annotation("Npgsql:Enum:infraction_type", "ban,mute,warn")
                .OldAnnotation("Npgsql:Enum:bot_auth_claims", "designated_channel_view,designated_channel_modify,custom_prefix_set,welcome_message_view,welcome_message_modify,tag_add,tag_delete,assignable_roles_add,assignable_roles_delete,delete_message,emote_add,claims_view,claims_modify,manage_class_add,moderation_warn,moderation_ban,moderation_mute,moderation_purge,moderation_infraction_view,moderation_infraction_view_self,dashboard_view,dashboard_edit,guild_settings_view,guild_settings_edit,custom_tag_prefix_set")
                .OldAnnotation("Npgsql:Enum:config_settings", "allow_embed_links")
                .OldAnnotation("Npgsql:Enum:designated_channels", "message_log,moderation_log,user_join_log,user_leave_log,starboard,server_join_log,bot_dm_log")
                .OldAnnotation("Npgsql:Enum:infraction_type", "ban,mute,warn");

            migrationBuilder.CreateTable(
                name: "CommandRestrictions",
                columns: table => new
                {
                    Id = table.Column<int>(type: "integer", nullable: false)
                        .Annotation("Npgsql:ValueGenerationStrategy", NpgsqlValueGenerationStrategy.IdentityByDefaultColumn),
                    CommandName = table.Column<string>(type: "text", nullable: true),
                    SilentlyFail = table.Column<bool>(type: "boolean", nullable: false),
                    GuildId = table.Column<decimal>(type: "numeric(20,0)", nullable: false),
                    ChannelId = table.Column<decimal>(type: "numeric(20,0)", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_CommandRestrictions", x => x.Id);
                    table.ForeignKey(
                        name: "FK_CommandRestrictions_Channels_ChannelId",
                        column: x => x.ChannelId,
                        principalTable: "Channels",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                    table.ForeignKey(
                        name: "FK_CommandRestrictions_Guilds_GuildId",
                        column: x => x.GuildId,
                        principalTable: "Guilds",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateIndex(
                name: "IX_CommandRestrictions_ChannelId",
                table: "CommandRestrictions",
                column: "ChannelId");

            migrationBuilder.CreateIndex(
                name: "IX_CommandRestrictions_GuildId",
                table: "CommandRestrictions",
                column: "GuildId");
        }

        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "CommandRestrictions");

            migrationBuilder.AlterDatabase()
                .Annotation("Npgsql:Enum:bot_auth_claims", "designated_channel_view,designated_channel_modify,custom_prefix_set,welcome_message_view,welcome_message_modify,tag_add,tag_delete,assignable_roles_add,assignable_roles_delete,delete_message,emote_add,claims_view,claims_modify,manage_class_add,moderation_warn,moderation_ban,moderation_mute,moderation_purge,moderation_infraction_view,moderation_infraction_view_self,dashboard_view,dashboard_edit,guild_settings_view,guild_settings_edit,custom_tag_prefix_set")
                .Annotation("Npgsql:Enum:config_settings", "allow_embed_links")
                .Annotation("Npgsql:Enum:designated_channels", "message_log,moderation_log,user_join_log,user_leave_log,starboard,server_join_log,bot_dm_log")
                .Annotation("Npgsql:Enum:infraction_type", "ban,mute,warn")
                .OldAnnotation("Npgsql:Enum:bot_auth_claims", "designated_channel_view,designated_channel_modify,custom_prefix_set,welcome_message_view,welcome_message_modify,tag_add,tag_delete,assignable_roles_add,assignable_roles_delete,delete_message,emote_add,claims_view,claims_modify,manage_class_add,moderation_warn,moderation_ban,moderation_mute,moderation_purge,moderation_infraction_view,moderation_infraction_view_self,dashboard_view,dashboard_edit,guild_settings_view,guild_settings_edit,custom_tag_prefix_set,manage_commands,bypass_disabled_commands")
                .OldAnnotation("Npgsql:Enum:config_settings", "allow_embed_links")
                .OldAnnotation("Npgsql:Enum:designated_channels", "message_log,moderation_log,user_join_log,user_leave_log,starboard,server_join_log,bot_dm_log")
                .OldAnnotation("Npgsql:Enum:infraction_type", "ban,mute,warn");
        }
    }
}
