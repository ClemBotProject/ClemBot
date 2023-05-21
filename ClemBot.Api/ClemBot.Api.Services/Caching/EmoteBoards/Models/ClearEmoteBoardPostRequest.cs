namespace ClemBot.Api.Services.Caching.EmoteBoards.Models;

public class ClearEmoteBoardPostRequest
{
    public ulong UserId { get; set; }

    public ulong MessageId { get; set; }
}
