using Microsoft.EntityFrameworkCore.Migrations;
using Npgsql.EntityFrameworkCore.PostgreSQL.Metadata;

#nullable disable

namespace ClemBot.Api.Data.Migrations
{
    /// <inheritdoc />
    public partial class AddEmoteBoards : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AlterDatabase()
                .Annotation("Npgsql:Enum:bot_auth_claims", "designated_channel_view,designated_channel_modify,custom_prefix_set,welcome_message_view,welcome_message_modify,tag_add,tag_delete,tag_transfer,assignable_roles_add,assignable_roles_delete,delete_message,emote_add,claims_view,claims_modify,manage_class_add,moderation_warn,moderation_ban,moderation_mute,moderation_purge,moderation_infraction_view,moderation_infraction_view_self,dashboard_view,dashboard_edit,guild_settings_view,guild_settings_edit,custom_tag_prefix_set,command_restrictions_edit,bypass_disabled_commands,manage_emote_boards")
                .Annotation("Npgsql:Enum:command_restriction_type", "white_list,black_list")
                .Annotation("Npgsql:Enum:config_settings", "allow_embed_links")
                .Annotation("Npgsql:Enum:designated_channels", "message_log,moderation_log,user_join_log,user_leave_log,starboard,server_join_log,bot_dm_log")
                .Annotation("Npgsql:Enum:infraction_type", "ban,mute,warn")
                .OldAnnotation("Npgsql:Enum:bot_auth_claims", "designated_channel_view,designated_channel_modify,custom_prefix_set,welcome_message_view,welcome_message_modify,tag_add,tag_delete,tag_transfer,assignable_roles_add,assignable_roles_delete,delete_message,emote_add,claims_view,claims_modify,manage_class_add,moderation_warn,moderation_ban,moderation_mute,moderation_purge,moderation_infraction_view,moderation_infraction_view_self,dashboard_view,dashboard_edit,guild_settings_view,guild_settings_edit,custom_tag_prefix_set,command_restrictions_edit,bypass_disabled_commands")
                .OldAnnotation("Npgsql:Enum:command_restriction_type", "white_list,black_list")
                .OldAnnotation("Npgsql:Enum:config_settings", "allow_embed_links")
                .OldAnnotation("Npgsql:Enum:designated_channels", "message_log,moderation_log,user_join_log,user_leave_log,starboard,server_join_log,bot_dm_log")
                .OldAnnotation("Npgsql:Enum:infraction_type", "ban,mute,warn");

            migrationBuilder.CreateTable(
                name: "EmoteBoards",
                columns: table => new
                {
                    Id = table.Column<int>(type: "integer", nullable: false)
                        .Annotation("Npgsql:ValueGenerationStrategy", NpgsqlValueGenerationStrategy.IdentityByDefaultColumn),
                    GuildId = table.Column<decimal>(type: "numeric(20,0)", nullable: false),
                    Name = table.Column<string>(type: "text", nullable: false),
                    Emote = table.Column<string>(type: "text", nullable: false),
                    ReactionThreshold = table.Column<long>(type: "bigint", nullable: false),
                    AllowBotPosts = table.Column<bool>(type: "boolean", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_EmoteBoards", x => x.Id);
                    table.ForeignKey(
                        name: "FK_EmoteBoards_Guilds_GuildId",
                        column: x => x.GuildId,
                        principalTable: "Guilds",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "ChannelEmoteBoard",
                columns: table => new
                {
                    ChannelsId = table.Column<decimal>(type: "numeric(20,0)", nullable: false),
                    EmoteBoardsId = table.Column<int>(type: "integer", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_ChannelEmoteBoard", x => new { x.ChannelsId, x.EmoteBoardsId });
                    table.ForeignKey(
                        name: "FK_ChannelEmoteBoard_Channels_ChannelsId",
                        column: x => x.ChannelsId,
                        principalTable: "Channels",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                    table.ForeignKey(
                        name: "FK_ChannelEmoteBoard_EmoteBoards_EmoteBoardsId",
                        column: x => x.EmoteBoardsId,
                        principalTable: "EmoteBoards",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "EmoteBoardPosts",
                columns: table => new
                {
                    Id = table.Column<int>(type: "integer", nullable: false)
                        .Annotation("Npgsql:ValueGenerationStrategy", NpgsqlValueGenerationStrategy.IdentityByDefaultColumn),
                    UserId = table.Column<decimal>(type: "numeric(20,0)", nullable: false),
                    MessageId = table.Column<decimal>(type: "numeric(20,0)", nullable: false),
                    ChannelId = table.Column<decimal>(type: "numeric(20,0)", nullable: false),
                    EmoteBoardId = table.Column<int>(type: "integer", nullable: false),
                    Reactions = table.Column<decimal[]>(type: "numeric(20,0)[]", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_EmoteBoardPosts", x => x.Id);
                    table.ForeignKey(
                        name: "FK_EmoteBoardPosts_Channels_ChannelId",
                        column: x => x.ChannelId,
                        principalTable: "Channels",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                    table.ForeignKey(
                        name: "FK_EmoteBoardPosts_EmoteBoards_EmoteBoardId",
                        column: x => x.EmoteBoardId,
                        principalTable: "EmoteBoards",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                    table.ForeignKey(
                        name: "FK_EmoteBoardPosts_Users_UserId",
                        column: x => x.UserId,
                        principalTable: "Users",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "EmoteBoardMessages",
                columns: table => new
                {
                    Id = table.Column<int>(type: "integer", nullable: false)
                        .Annotation("Npgsql:ValueGenerationStrategy", NpgsqlValueGenerationStrategy.IdentityByDefaultColumn),
                    MessageId = table.Column<decimal>(type: "numeric(20,0)", nullable: false),
                    ChannelId = table.Column<decimal>(type: "numeric(20,0)", nullable: false),
                    EmoteBoardPostId = table.Column<int>(type: "integer", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_EmoteBoardMessages", x => x.Id);
                    table.ForeignKey(
                        name: "FK_EmoteBoardMessages_Channels_ChannelId",
                        column: x => x.ChannelId,
                        principalTable: "Channels",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                    table.ForeignKey(
                        name: "FK_EmoteBoardMessages_EmoteBoardPosts_EmoteBoardPostId",
                        column: x => x.EmoteBoardPostId,
                        principalTable: "EmoteBoardPosts",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateIndex(
                name: "IX_ChannelEmoteBoard_EmoteBoardsId",
                table: "ChannelEmoteBoard",
                column: "EmoteBoardsId");

            migrationBuilder.CreateIndex(
                name: "IX_EmoteBoardMessages_ChannelId",
                table: "EmoteBoardMessages",
                column: "ChannelId");

            migrationBuilder.CreateIndex(
                name: "IX_EmoteBoardMessages_EmoteBoardPostId",
                table: "EmoteBoardMessages",
                column: "EmoteBoardPostId");

            migrationBuilder.CreateIndex(
                name: "IX_EmoteBoardPosts_ChannelId",
                table: "EmoteBoardPosts",
                column: "ChannelId");

            migrationBuilder.CreateIndex(
                name: "IX_EmoteBoardPosts_EmoteBoardId",
                table: "EmoteBoardPosts",
                column: "EmoteBoardId");

            migrationBuilder.CreateIndex(
                name: "IX_EmoteBoardPosts_UserId",
                table: "EmoteBoardPosts",
                column: "UserId");

            migrationBuilder.CreateIndex(
                name: "IX_EmoteBoards_GuildId",
                table: "EmoteBoards",
                column: "GuildId");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "ChannelEmoteBoard");

            migrationBuilder.DropTable(
                name: "EmoteBoardMessages");

            migrationBuilder.DropTable(
                name: "EmoteBoardPosts");

            migrationBuilder.DropTable(
                name: "EmoteBoards");

            migrationBuilder.AlterDatabase()
                .Annotation("Npgsql:Enum:bot_auth_claims", "designated_channel_view,designated_channel_modify,custom_prefix_set,welcome_message_view,welcome_message_modify,tag_add,tag_delete,tag_transfer,assignable_roles_add,assignable_roles_delete,delete_message,emote_add,claims_view,claims_modify,manage_class_add,moderation_warn,moderation_ban,moderation_mute,moderation_purge,moderation_infraction_view,moderation_infraction_view_self,dashboard_view,dashboard_edit,guild_settings_view,guild_settings_edit,custom_tag_prefix_set,command_restrictions_edit,bypass_disabled_commands")
                .Annotation("Npgsql:Enum:command_restriction_type", "white_list,black_list")
                .Annotation("Npgsql:Enum:config_settings", "allow_embed_links")
                .Annotation("Npgsql:Enum:designated_channels", "message_log,moderation_log,user_join_log,user_leave_log,starboard,server_join_log,bot_dm_log")
                .Annotation("Npgsql:Enum:infraction_type", "ban,mute,warn")
                .OldAnnotation("Npgsql:Enum:bot_auth_claims", "designated_channel_view,designated_channel_modify,custom_prefix_set,welcome_message_view,welcome_message_modify,tag_add,tag_delete,tag_transfer,assignable_roles_add,assignable_roles_delete,delete_message,emote_add,claims_view,claims_modify,manage_class_add,moderation_warn,moderation_ban,moderation_mute,moderation_purge,moderation_infraction_view,moderation_infraction_view_self,dashboard_view,dashboard_edit,guild_settings_view,guild_settings_edit,custom_tag_prefix_set,command_restrictions_edit,bypass_disabled_commands,manage_emote_boards")
                .OldAnnotation("Npgsql:Enum:command_restriction_type", "white_list,black_list")
                .OldAnnotation("Npgsql:Enum:config_settings", "allow_embed_links")
                .OldAnnotation("Npgsql:Enum:designated_channels", "message_log,moderation_log,user_join_log,user_leave_log,starboard,server_join_log,bot_dm_log")
                .OldAnnotation("Npgsql:Enum:infraction_type", "ban,mute,warn");
        }
    }
}
