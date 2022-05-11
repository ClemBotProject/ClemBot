using MediatR;

namespace ClemBot.Api.Services.Caching.Channels.Models;

public class ChannelExistsRequest : ICacheRequest, IRequest<bool>
{
    public ulong Id { get; init; }
}
