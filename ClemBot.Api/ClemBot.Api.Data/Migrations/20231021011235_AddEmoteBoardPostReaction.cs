using Microsoft.EntityFrameworkCore.Migrations;
using Npgsql.EntityFrameworkCore.PostgreSQL.Metadata;

#nullable disable

namespace ClemBot.Api.Data.Migrations
{
    /// <inheritdoc />
    public partial class AddEmoteBoardPostReaction : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropColumn(
                name: "Reactions",
                table: "EmoteBoardPosts");

            migrationBuilder.CreateTable(
                name: "EmoteBoardPostReactions",
                columns: table => new
                {
                    Id = table.Column<int>(type: "integer", nullable: false)
                        .Annotation("Npgsql:ValueGenerationStrategy", NpgsqlValueGenerationStrategy.IdentityByDefaultColumn),
                    EmoteBoardPostId = table.Column<int>(type: "integer", nullable: false),
                    UserId = table.Column<decimal>(type: "numeric(20,0)", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_EmoteBoardPostReactions", x => x.Id);
                    table.ForeignKey(
                        name: "FK_EmoteBoardPostReactions_EmoteBoardPosts_EmoteBoardPostId",
                        column: x => x.EmoteBoardPostId,
                        principalTable: "EmoteBoardPosts",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateIndex(
                name: "IX_EmoteBoardPostReactions_EmoteBoardPostId",
                table: "EmoteBoardPostReactions",
                column: "EmoteBoardPostId");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "EmoteBoardPostReactions");

            migrationBuilder.AddColumn<decimal[]>(
                name: "Reactions",
                table: "EmoteBoardPosts",
                type: "numeric(20,0)[]",
                nullable: false,
                defaultValue: new decimal[0]);
        }
    }
}
