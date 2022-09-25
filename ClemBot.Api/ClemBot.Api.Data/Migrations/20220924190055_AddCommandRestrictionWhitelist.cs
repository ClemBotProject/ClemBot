using ClemBot.Api.Common.Enums;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace ClemBot.Api.Data.Migrations
{
    public partial class AddCommandRestrictionWhitelist : Migration
    {
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AlterDatabase()
                .Annotation("Npgsql:Enum:bot_auth_claims", "designated_channel_view,designated_channel_modify,custom_prefix_set,welcome_message_view,welcome_message_modify,tag_add,tag_delete,tag_transfer,assignable_roles_add,assignable_roles_delete,delete_message,emote_add,claims_view,claims_modify,manage_class_add,moderation_warn,moderation_ban,moderation_mute,moderation_purge,moderation_infraction_view,moderation_infraction_view_self,dashboard_view,dashboard_edit,guild_settings_view,guild_settings_edit,custom_tag_prefix_set,command_restrictions_edit,bypass_disabled_commands")
                .Annotation("Npgsql:Enum:command_restriction_type", "white_list,black_list")
                .Annotation("Npgsql:Enum:config_settings", "allow_embed_links")
                .Annotation("Npgsql:Enum:designated_channels", "message_log,moderation_log,user_join_log,user_leave_log,starboard,server_join_log,bot_dm_log")
                .Annotation("Npgsql:Enum:infraction_type", "ban,mute,warn")
                .OldAnnotation("Npgsql:Enum:bot_auth_claims", "designated_channel_view,designated_channel_modify,custom_prefix_set,welcome_message_view,welcome_message_modify,tag_add,tag_delete,tag_transfer,assignable_roles_add,assignable_roles_delete,delete_message,emote_add,claims_view,claims_modify,manage_class_add,moderation_warn,moderation_ban,moderation_mute,moderation_purge,moderation_infraction_view,moderation_infraction_view_self,dashboard_view,dashboard_edit,guild_settings_view,guild_settings_edit,custom_tag_prefix_set,command_restrictions_edit,bypass_disabled_commands")
                .OldAnnotation("Npgsql:Enum:config_settings", "allow_embed_links")
                .OldAnnotation("Npgsql:Enum:designated_channels", "message_log,moderation_log,user_join_log,user_leave_log,starboard,server_join_log,bot_dm_log")
                .OldAnnotation("Npgsql:Enum:infraction_type", "ban,mute,warn");

            migrationBuilder.AlterColumn<bool>(
                name: "SilentlyFail",
                table: "CommandRestrictions",
                type: "boolean",
                nullable: true,
                oldClrType: typeof(bool),
                oldType: "boolean");

            migrationBuilder.AddColumn<CommandRestrictionType>(
                name: "RestrictionType",
                table: "CommandRestrictions",
                type: "command_restriction_type",
                nullable: false,
                defaultValue: CommandRestrictionType.WhiteList);
        }

        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropColumn(
                name: "RestrictionType",
                table: "CommandRestrictions");

            migrationBuilder.AlterDatabase()
                .Annotation("Npgsql:Enum:bot_auth_claims", "designated_channel_view,designated_channel_modify,custom_prefix_set,welcome_message_view,welcome_message_modify,tag_add,tag_delete,tag_transfer,assignable_roles_add,assignable_roles_delete,delete_message,emote_add,claims_view,claims_modify,manage_class_add,moderation_warn,moderation_ban,moderation_mute,moderation_purge,moderation_infraction_view,moderation_infraction_view_self,dashboard_view,dashboard_edit,guild_settings_view,guild_settings_edit,custom_tag_prefix_set,command_restrictions_edit,bypass_disabled_commands")
                .Annotation("Npgsql:Enum:config_settings", "allow_embed_links")
                .Annotation("Npgsql:Enum:designated_channels", "message_log,moderation_log,user_join_log,user_leave_log,starboard,server_join_log,bot_dm_log")
                .Annotation("Npgsql:Enum:infraction_type", "ban,mute,warn")
                .OldAnnotation("Npgsql:Enum:bot_auth_claims", "designated_channel_view,designated_channel_modify,custom_prefix_set,welcome_message_view,welcome_message_modify,tag_add,tag_delete,tag_transfer,assignable_roles_add,assignable_roles_delete,delete_message,emote_add,claims_view,claims_modify,manage_class_add,moderation_warn,moderation_ban,moderation_mute,moderation_purge,moderation_infraction_view,moderation_infraction_view_self,dashboard_view,dashboard_edit,guild_settings_view,guild_settings_edit,custom_tag_prefix_set,command_restrictions_edit,bypass_disabled_commands")
                .OldAnnotation("Npgsql:Enum:command_restriction_type", "white_list,black_list")
                .OldAnnotation("Npgsql:Enum:config_settings", "allow_embed_links")
                .OldAnnotation("Npgsql:Enum:designated_channels", "message_log,moderation_log,user_join_log,user_leave_log,starboard,server_join_log,bot_dm_log")
                .OldAnnotation("Npgsql:Enum:infraction_type", "ban,mute,warn");

            migrationBuilder.AlterColumn<bool>(
                name: "SilentlyFail",
                table: "CommandRestrictions",
                type: "boolean",
                nullable: false,
                defaultValue: false,
                oldClrType: typeof(bool),
                oldType: "boolean",
                oldNullable: true);
        }
    }
}
