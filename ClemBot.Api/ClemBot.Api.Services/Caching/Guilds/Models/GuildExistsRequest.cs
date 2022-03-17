using MediatR;

namespace ClemBot.Api.Services.Caching.Guilds.Models;

public class GuildExistsRequest : ICacheRequest, IRequest<bool>
{
    public ulong Id { get; init; }
}
