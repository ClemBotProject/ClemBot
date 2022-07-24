using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace ClemBot.Api.Data.Migrations
{
    public partial class AddReminderContentDispatched : Migration
    {
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropForeignKey(
                name: "FK_Reminders_Guilds_MessageId",
                table: "Reminders");

            migrationBuilder.AddColumn<string>(
                name: "Content",
                table: "Reminders",
                type: "text",
                nullable: true);

            migrationBuilder.AddColumn<bool>(
                name: "Dispatched",
                table: "Reminders",
                type: "boolean",
                nullable: false,
                defaultValue: false);

            migrationBuilder.AddColumn<decimal>(
                name: "GuildId",
                table: "Reminders",
                type: "numeric(20,0)",
                nullable: true);

            migrationBuilder.CreateIndex(
                name: "IX_Reminders_GuildId",
                table: "Reminders",
                column: "GuildId");

            migrationBuilder.AddForeignKey(
                name: "FK_Reminders_Guilds_GuildId",
                table: "Reminders",
                column: "GuildId",
                principalTable: "Guilds",
                principalColumn: "Id");

            migrationBuilder.AddForeignKey(
                name: "FK_Reminders_Messages_MessageId",
                table: "Reminders",
                column: "MessageId",
                principalTable: "Messages",
                principalColumn: "Id",
                onDelete: ReferentialAction.Cascade);
        }

        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropForeignKey(
                name: "FK_Reminders_Guilds_GuildId",
                table: "Reminders");

            migrationBuilder.DropForeignKey(
                name: "FK_Reminders_Messages_MessageId",
                table: "Reminders");

            migrationBuilder.DropIndex(
                name: "IX_Reminders_GuildId",
                table: "Reminders");

            migrationBuilder.DropColumn(
                name: "Content",
                table: "Reminders");

            migrationBuilder.DropColumn(
                name: "Dispatched",
                table: "Reminders");

            migrationBuilder.DropColumn(
                name: "GuildId",
                table: "Reminders");

            migrationBuilder.AddForeignKey(
                name: "FK_Reminders_Guilds_MessageId",
                table: "Reminders",
                column: "MessageId",
                principalTable: "Guilds",
                principalColumn: "Id",
                onDelete: ReferentialAction.Cascade);
        }
    }
}
