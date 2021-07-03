using Microsoft.EntityFrameworkCore.Migrations;

namespace ClemBot.Api.Data.Migrations
{
    public partial class ChangedGuildUserJunctionRelationship : Migration
    {
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropForeignKey(
                name: "FK_GuildUser_Guilds_GuildsId",
                table: "GuildUser");

            migrationBuilder.DropForeignKey(
                name: "FK_GuildUser_Users_UsersId",
                table: "GuildUser");

            migrationBuilder.RenameColumn(
                name: "UsersId",
                table: "GuildUser",
                newName: "UserId");

            migrationBuilder.RenameColumn(
                name: "GuildsId",
                table: "GuildUser",
                newName: "GuildId");

            migrationBuilder.RenameIndex(
                name: "IX_GuildUser_UsersId",
                table: "GuildUser",
                newName: "IX_GuildUser_UserId");

            migrationBuilder.AddForeignKey(
                name: "FK_GuildUser_Guilds_GuildId",
                table: "GuildUser",
                column: "GuildId",
                principalTable: "Guilds",
                principalColumn: "Id",
                onDelete: ReferentialAction.Cascade);

            migrationBuilder.AddForeignKey(
                name: "FK_GuildUser_Users_UserId",
                table: "GuildUser",
                column: "UserId",
                principalTable: "Users",
                principalColumn: "Id",
                onDelete: ReferentialAction.Cascade);
        }

        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropForeignKey(
                name: "FK_GuildUser_Guilds_GuildId",
                table: "GuildUser");

            migrationBuilder.DropForeignKey(
                name: "FK_GuildUser_Users_UserId",
                table: "GuildUser");

            migrationBuilder.RenameColumn(
                name: "UserId",
                table: "GuildUser",
                newName: "UsersId");

            migrationBuilder.RenameColumn(
                name: "GuildId",
                table: "GuildUser",
                newName: "GuildsId");

            migrationBuilder.RenameIndex(
                name: "IX_GuildUser_UserId",
                table: "GuildUser",
                newName: "IX_GuildUser_UsersId");

            migrationBuilder.AddForeignKey(
                name: "FK_GuildUser_Guilds_GuildsId",
                table: "GuildUser",
                column: "GuildsId",
                principalTable: "Guilds",
                principalColumn: "Id",
                onDelete: ReferentialAction.Cascade);

            migrationBuilder.AddForeignKey(
                name: "FK_GuildUser_Users_UsersId",
                table: "GuildUser",
                column: "UsersId",
                principalTable: "Users",
                principalColumn: "Id",
                onDelete: ReferentialAction.Cascade);
        }
    }
}
