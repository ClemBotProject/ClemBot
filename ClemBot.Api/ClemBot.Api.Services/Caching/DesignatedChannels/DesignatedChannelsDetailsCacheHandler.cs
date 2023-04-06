using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Data.Models;
using ClemBot.Api.Services.Caching.DesignatedChannels.Models;
using LazyCache;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Services.Caching.DesignatedChannels;

public class DesignatedChannelsCacheHandler: IRequestHandler<ClearDesignatedChannelDetailRequest>, IRequestHandler<GetDesignatedChannelDetailRequest, List<DesignatedChannelMapping>>
{
    private readonly IAppCache _cache;
    private readonly ClemBotContext _context;

    public DesignatedChannelsCacheHandler(IAppCache cache, ClemBotContext context)
    {
        _cache = cache;
        _context = context;
    }

    public async Task<List<DesignatedChannelMapping>> Handle(GetDesignatedChannelDetailRequest request, CancellationToken cancellationToken) =>
        await _cache.GetOrAddAsync(GetCacheKey(request.Id, request.Designation),
            () => _context.DesignatedChannelMappings
                .Where(x => x.Channel.Guild.Id == request.Id && x.Type == request.Designation)
                .ToListAsync(), TimeSpan.FromHours(1));

    public Task<Unit> Handle(ClearDesignatedChannelDetailRequest request, CancellationToken cancellationToken)
    {
        _cache.Remove(GetCacheKey(request.Id, request.Designation));
        return Unit.Task;
    }

    private static string GetCacheKey(ulong id, Common.Enums.DesignatedChannels designation) =>
        $"{nameof(GetDesignatedChannelDetailRequest)}:{id}:{designation}";
}
