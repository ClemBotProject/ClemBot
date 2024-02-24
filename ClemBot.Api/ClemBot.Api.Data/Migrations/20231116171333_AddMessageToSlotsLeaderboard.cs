using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace ClemBot.Api.Data.Migrations
{
    /// <inheritdoc />
    public partial class AddMessageToSlotsLeaderboard : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AddColumn<decimal>(
                name: "ChannelId",
                table: "SlotScores",
                type: "numeric(20,0)",
                nullable: true);

            migrationBuilder.AddColumn<decimal>(
                name: "MessageId",
                table: "SlotScores",
                type: "numeric(20,0)",
                nullable: true);

            migrationBuilder.CreateIndex(
                name: "IX_SlotScores_ChannelId",
                table: "SlotScores",
                column: "ChannelId");

            migrationBuilder.AddForeignKey(
                name: "FK_SlotScores_Channels_ChannelId",
                table: "SlotScores",
                column: "ChannelId",
                principalTable: "Channels",
                principalColumn: "Id");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropForeignKey(
                name: "FK_SlotScores_Channels_ChannelId",
                table: "SlotScores");

            migrationBuilder.DropIndex(
                name: "IX_SlotScores_ChannelId",
                table: "SlotScores");

            migrationBuilder.DropColumn(
                name: "ChannelId",
                table: "SlotScores");

            migrationBuilder.DropColumn(
                name: "MessageId",
                table: "SlotScores");
        }
    }
}
