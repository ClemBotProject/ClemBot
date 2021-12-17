using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace ClemBot.Api.Data.Migrations
{
    public partial class AddDashboardEditClaim : Migration
    {
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AlterDatabase()
                .Annotation("Npgsql:Enum:bot_auth_claims", "designated_channel_view,designated_channel_modify,custom_prefix_set,welcome_message_view,welcome_message_modify,tag_add,tag_delete,assignable_roles_add,assignable_roles_delete,delete_message,emote_add,claims_view,claims_modify,manage_class_add,moderation_warn,moderation_ban,moderation_mute,moderation_purge,moderation_infraction_view,dashboard_edit")
                .Annotation("Npgsql:Enum:designated_channels", "message_log,moderation_log,user_join_log,user_leave_log,starboard,server_join_log,bot_dm_log")
                .Annotation("Npgsql:Enum:infraction_type", "ban,mute,warn")
                .OldAnnotation("Npgsql:Enum:bot_auth_claims", "designated_channel_view,designated_channel_modify,custom_prefix_set,welcome_message_view,welcome_message_modify,tag_add,tag_delete,assignable_roles_add,assignable_roles_delete,delete_message,emote_add,claims_view,claims_modify,manage_class_add,moderation_warn,moderation_ban,moderation_mute,moderation_purge,moderation_infraction_view")
                .OldAnnotation("Npgsql:Enum:designated_channels", "message_log,moderation_log,user_join_log,user_leave_log,starboard,server_join_log,bot_dm_log")
                .OldAnnotation("Npgsql:Enum:infraction_type", "ban,mute,warn");

            migrationBuilder.AlterColumn<DateTime>(
                name: "Time",
                table: "TagUses",
                type: "timestamp with time zone",
                nullable: false,
                oldClrType: typeof(DateTime),
                oldType: "timestamp without time zone");

            migrationBuilder.AlterColumn<DateTime>(
                name: "Time",
                table: "Reminders",
                type: "timestamp with time zone",
                nullable: false,
                oldClrType: typeof(DateTime),
                oldType: "timestamp without time zone");
        }

        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AlterDatabase()
                .Annotation("Npgsql:Enum:bot_auth_claims", "designated_channel_view,designated_channel_modify,custom_prefix_set,welcome_message_view,welcome_message_modify,tag_add,tag_delete,assignable_roles_add,assignable_roles_delete,delete_message,emote_add,claims_view,claims_modify,manage_class_add,moderation_warn,moderation_ban,moderation_mute,moderation_purge,moderation_infraction_view")
                .Annotation("Npgsql:Enum:designated_channels", "message_log,moderation_log,user_join_log,user_leave_log,starboard,server_join_log,bot_dm_log")
                .Annotation("Npgsql:Enum:infraction_type", "ban,mute,warn")
                .OldAnnotation("Npgsql:Enum:bot_auth_claims", "designated_channel_view,designated_channel_modify,custom_prefix_set,welcome_message_view,welcome_message_modify,tag_add,tag_delete,assignable_roles_add,assignable_roles_delete,delete_message,emote_add,claims_view,claims_modify,manage_class_add,moderation_warn,moderation_ban,moderation_mute,moderation_purge,moderation_infraction_view,dashboard_edit")
                .OldAnnotation("Npgsql:Enum:designated_channels", "message_log,moderation_log,user_join_log,user_leave_log,starboard,server_join_log,bot_dm_log")
                .OldAnnotation("Npgsql:Enum:infraction_type", "ban,mute,warn");

            migrationBuilder.AlterColumn<DateTime>(
                name: "Time",
                table: "TagUses",
                type: "timestamp without time zone",
                nullable: false,
                oldClrType: typeof(DateTime),
                oldType: "timestamp with time zone");

            migrationBuilder.AlterColumn<DateTime>(
                name: "Time",
                table: "Reminders",
                type: "timestamp without time zone",
                nullable: false,
                oldClrType: typeof(DateTime),
                oldType: "timestamp with time zone");
        }
    }
}
