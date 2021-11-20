using Microsoft.EntityFrameworkCore.Migrations;

namespace ClemBot.Api.Data.Migrations
{
    public partial class AddThreadChannelEntityData : Migration
    {
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AddColumn<decimal>(
                name: "ParentId",
                table: "Channels",
                type: "numeric(20,0)",
                nullable: true);

            migrationBuilder.AddColumn<bool>(
                name: "IsThread",
                table: "Channels",
                type: "boolean",
                nullable: false,
                computedColumnSql: "\"Channels\".\"ParentId\" IS NOT null",
                stored: true);

            migrationBuilder.CreateIndex(
                name: "IX_Channels_ParentId",
                table: "Channels",
                column: "ParentId");

            migrationBuilder.AddForeignKey(
                name: "FK_Channels_Channels_ParentId",
                table: "Channels",
                column: "ParentId",
                principalTable: "Channels",
                principalColumn: "Id",
                onDelete: ReferentialAction.Restrict);
        }

        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropForeignKey(
                name: "FK_Channels_Channels_ParentId",
                table: "Channels");

            migrationBuilder.DropIndex(
                name: "IX_Channels_ParentId",
                table: "Channels");

            migrationBuilder.DropColumn(
                name: "IsThread",
                table: "Channels");

            migrationBuilder.DropColumn(
                name: "ParentId",
                table: "Channels");
        }
    }
}
