using Microsoft.EntityFrameworkCore.Migrations;
using Npgsql.EntityFrameworkCore.PostgreSQL.Metadata;

#nullable disable

namespace ClemBot.Api.Data.Migrations
{
    public partial class AddInlineTagprefix : Migration
    {
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AlterDatabase()
                .Annotation("Npgsql:Enum:bot_auth_claims", "designated_channel_view,designated_channel_modify,custom_prefix_set,welcome_message_view,welcome_message_modify,tag_add,tag_delete,assignable_roles_add,assignable_roles_delete,delete_message,emote_add,claims_view,claims_modify,manage_class_add,moderation_warn,moderation_ban,moderation_mute,moderation_purge,moderation_infraction_view,moderation_infraction_view_self,dashboard_view,dashboard_edit,guild_settings_view,guild_settings_edit,custom_tag_prefix_set")
                .Annotation("Npgsql:Enum:config_settings", "allow_embed_links")
                .Annotation("Npgsql:Enum:designated_channels", "message_log,moderation_log,user_join_log,user_leave_log,starboard,server_join_log,bot_dm_log")
                .Annotation("Npgsql:Enum:infraction_type", "ban,mute,warn")
                .OldAnnotation("Npgsql:Enum:bot_auth_claims", "designated_channel_view,designated_channel_modify,custom_prefix_set,welcome_message_view,welcome_message_modify,tag_add,tag_delete,assignable_roles_add,assignable_roles_delete,delete_message,emote_add,claims_view,claims_modify,manage_class_add,moderation_warn,moderation_ban,moderation_mute,moderation_purge,moderation_infraction_view,moderation_infraction_view_self,dashboard_view,dashboard_edit,guild_settings_view,guild_settings_edit")
                .OldAnnotation("Npgsql:Enum:config_settings", "allow_embed_links")
                .OldAnnotation("Npgsql:Enum:designated_channels", "message_log,moderation_log,user_join_log,user_leave_log,starboard,server_join_log,bot_dm_log")
                .OldAnnotation("Npgsql:Enum:infraction_type", "ban,mute,warn");

            migrationBuilder.CreateTable(
                name: "CustomTagPrefixs",
                columns: table => new
                {
                    Id = table.Column<int>(type: "integer", nullable: false)
                        .Annotation("Npgsql:ValueGenerationStrategy", NpgsqlValueGenerationStrategy.IdentityByDefaultColumn),
                    TagPrefix = table.Column<string>(type: "text", nullable: true),
                    GuildId = table.Column<decimal>(type: "numeric(20,0)", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_CustomTagPrefixs", x => x.Id);
                    table.ForeignKey(
                        name: "FK_CustomTagPrefixs_Guilds_GuildId",
                        column: x => x.GuildId,
                        principalTable: "Guilds",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateIndex(
                name: "IX_CustomTagPrefixs_GuildId",
                table: "CustomTagPrefixs",
                column: "GuildId");
        }

        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "CustomTagPrefixs");

            migrationBuilder.AlterDatabase()
                .Annotation("Npgsql:Enum:bot_auth_claims", "designated_channel_view,designated_channel_modify,custom_prefix_set,welcome_message_view,welcome_message_modify,tag_add,tag_delete,assignable_roles_add,assignable_roles_delete,delete_message,emote_add,claims_view,claims_modify,manage_class_add,moderation_warn,moderation_ban,moderation_mute,moderation_purge,moderation_infraction_view,moderation_infraction_view_self,dashboard_view,dashboard_edit,guild_settings_view,guild_settings_edit")
                .Annotation("Npgsql:Enum:config_settings", "allow_embed_links")
                .Annotation("Npgsql:Enum:designated_channels", "message_log,moderation_log,user_join_log,user_leave_log,starboard,server_join_log,bot_dm_log")
                .Annotation("Npgsql:Enum:infraction_type", "ban,mute,warn")
                .OldAnnotation("Npgsql:Enum:bot_auth_claims", "designated_channel_view,designated_channel_modify,custom_prefix_set,welcome_message_view,welcome_message_modify,tag_add,tag_delete,assignable_roles_add,assignable_roles_delete,delete_message,emote_add,claims_view,claims_modify,manage_class_add,moderation_warn,moderation_ban,moderation_mute,moderation_purge,moderation_infraction_view,moderation_infraction_view_self,dashboard_view,dashboard_edit,guild_settings_view,guild_settings_edit,custom_tag_prefix_set")
                .OldAnnotation("Npgsql:Enum:config_settings", "allow_embed_links")
                .OldAnnotation("Npgsql:Enum:designated_channels", "message_log,moderation_log,user_join_log,user_leave_log,starboard,server_join_log,bot_dm_log")
                .OldAnnotation("Npgsql:Enum:infraction_type", "ban,mute,warn");
        }
    }
}
