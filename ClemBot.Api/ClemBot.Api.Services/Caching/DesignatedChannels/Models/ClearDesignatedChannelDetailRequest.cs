using MediatR;

namespace ClemBot.Api.Services.Caching.DesignatedChannels.Models;

public class ClearDesignatedChannelDetailRequest : ICacheRequest, IRequest
{
    public ulong Id { get; init; }

    public Common.Enums.DesignatedChannels Designation { get; init; }
}
