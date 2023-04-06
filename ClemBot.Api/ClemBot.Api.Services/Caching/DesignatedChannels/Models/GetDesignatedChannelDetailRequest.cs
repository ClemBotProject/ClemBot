using System.Collections.Generic;
using ClemBot.Api.Data.Models;
using MediatR;

namespace ClemBot.Api.Services.Caching.DesignatedChannels.Models;

public class GetDesignatedChannelDetailRequest : ICacheRequest, IRequest<List<DesignatedChannelMapping>>
{
    public ulong Id { get; init; }

    public Common.Enums.DesignatedChannels Designation { get; init; }
}
