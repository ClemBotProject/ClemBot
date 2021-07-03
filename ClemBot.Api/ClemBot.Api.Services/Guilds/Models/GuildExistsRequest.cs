using MediatR;

namespace ClemBot.Api.Services.Guilds.Models
{
    public class GuildExistsRequest : IRequest<bool>
    {
        public ulong Id { get; init; }
    }
}
