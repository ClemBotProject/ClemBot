using System;
using Microsoft.EntityFrameworkCore.Migrations;
using NodaTime;

#nullable disable

namespace ClemBot.Api.Data.Migrations
{
    public partial class UpdateRemindersTable : Migration
    {
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropForeignKey(
                name: "FK_Reminders_Guilds_MessageId",
                table: "Reminders");

            migrationBuilder.DropIndex(
                name: "IX_Reminders_MessageId",
                table: "Reminders");

            migrationBuilder.DropColumn(
                name: "MessageId",
                table: "Reminders");

            migrationBuilder.AlterColumn<LocalDateTime>(
                name: "Time",
                table: "Reminders",
                type: "timestamp without time zone",
                nullable: false,
                oldClrType: typeof(DateTime),
                oldType: "timestamp with time zone");

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
        }

        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropColumn(
                name: "Content",
                table: "Reminders");

            migrationBuilder.DropColumn(
                name: "Dispatched",
                table: "Reminders");

            migrationBuilder.AlterColumn<DateTime>(
                name: "Time",
                table: "Reminders",
                type: "timestamp with time zone",
                nullable: false,
                oldClrType: typeof(LocalDateTime),
                oldType: "timestamp without time zone");

            migrationBuilder.AddColumn<decimal>(
                name: "MessageId",
                table: "Reminders",
                type: "numeric(20,0)",
                nullable: false,
                defaultValue: 0m);

            migrationBuilder.CreateIndex(
                name: "IX_Reminders_MessageId",
                table: "Reminders",
                column: "MessageId");

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
