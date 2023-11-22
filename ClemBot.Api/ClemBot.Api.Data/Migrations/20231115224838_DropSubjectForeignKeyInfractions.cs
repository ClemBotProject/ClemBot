using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace ClemBot.Api.Data.Migrations
{
    /// <inheritdoc />
    public partial class DropSubjectForeignKeyInfractions : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropForeignKey(
                name: "FK_Infractions_Users_SubjectId",
                table: "Infractions");

            migrationBuilder.AlterColumn<decimal>(
                name: "SubjectId",
                table: "Infractions",
                type: "numeric(20,0)",
                nullable: true,
                oldClrType: typeof(decimal),
                oldType: "numeric(20,0)");

            migrationBuilder.AddForeignKey(
                name: "FK_Infractions_Users_SubjectId",
                table: "Infractions",
                column: "SubjectId",
                principalTable: "Users",
                principalColumn: "Id");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropForeignKey(
                name: "FK_Infractions_Users_SubjectId",
                table: "Infractions");

            migrationBuilder.AlterColumn<decimal>(
                name: "SubjectId",
                table: "Infractions",
                type: "numeric(20,0)",
                nullable: false,
                defaultValue: 0m,
                oldClrType: typeof(decimal),
                oldType: "numeric(20,0)",
                oldNullable: true);

            migrationBuilder.AddForeignKey(
                name: "FK_Infractions_Users_SubjectId",
                table: "Infractions",
                column: "SubjectId",
                principalTable: "Users",
                principalColumn: "Id",
                onDelete: ReferentialAction.Cascade);
        }
    }
}
