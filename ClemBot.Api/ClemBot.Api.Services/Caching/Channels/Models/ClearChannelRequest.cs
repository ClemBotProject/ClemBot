using MediatR;

namespace ClemBot.Api.Services.Caching.Channels.Models;

public class ClearChannelRequest : ICacheRequest, IRequest
{
    public ulong Id { get; init; }
}
