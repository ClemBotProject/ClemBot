using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace ClemBot.Api.Data.Migrations
{
    public partial class DropCommandInvocationFkConstraint : Migration
    {
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropForeignKey(
                name: "FK_CommandInvocations_Channels_ChannelId",
                table: "CommandInvocations");

            migrationBuilder.DropForeignKey(
                name: "FK_CommandInvocations_Guilds_GuildId",
                table: "CommandInvocations");

            migrationBuilder.DropForeignKey(
                name: "FK_CommandInvocations_Users_UserId",
                table: "CommandInvocations");

            migrationBuilder.DropIndex(
                name: "IX_CommandInvocations_ChannelId",
                table: "CommandInvocations");

            migrationBuilder.DropIndex(
                name: "IX_CommandInvocations_GuildId",
                table: "CommandInvocations");

            migrationBuilder.DropIndex(
                name: "IX_CommandInvocations_UserId",
                table: "CommandInvocations");
        }

        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.CreateIndex(
                name: "IX_CommandInvocations_ChannelId",
                table: "CommandInvocations",
                column: "ChannelId");

            migrationBuilder.CreateIndex(
                name: "IX_CommandInvocations_GuildId",
                table: "CommandInvocations",
                column: "GuildId");

            migrationBuilder.CreateIndex(
                name: "IX_CommandInvocations_UserId",
                table: "CommandInvocations",
                column: "UserId");

            migrationBuilder.AddForeignKey(
                name: "FK_CommandInvocations_Channels_ChannelId",
                table: "CommandInvocations",
                column: "ChannelId",
                principalTable: "Channels",
                principalColumn: "Id",
                onDelete: ReferentialAction.Cascade);

            migrationBuilder.AddForeignKey(
                name: "FK_CommandInvocations_Guilds_GuildId",
                table: "CommandInvocations",
                column: "GuildId",
                principalTable: "Guilds",
                principalColumn: "Id",
                onDelete: ReferentialAction.Cascade);

            migrationBuilder.AddForeignKey(
                name: "FK_CommandInvocations_Users_UserId",
                table: "CommandInvocations",
                column: "UserId",
                principalTable: "Users",
                principalColumn: "Id",
                onDelete: ReferentialAction.Cascade);
        }
    }
}
