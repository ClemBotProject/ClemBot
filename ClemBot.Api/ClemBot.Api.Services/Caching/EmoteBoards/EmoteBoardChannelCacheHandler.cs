using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Services.Caching.EmoteBoards.Models;
using LazyCache;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Services.Caching.EmoteBoards;

public class EmoteBoardChannelCacheHandler : IRequestHandler<ClearEmoteBoardChannelsRequest>,
    IRequestHandler<GetEmoteBoardChannelsRequest, List<ulong>>
{

    private readonly IAppCache _cache;
    private readonly ClemBotContext _context;

    public EmoteBoardChannelCacheHandler(IAppCache cache, ClemBotContext context)
    {
        _cache = cache;
        _context = context;
    }

    public Task<Unit> Handle(ClearEmoteBoardChannelsRequest request, CancellationToken cancellationToken)
    {
        _cache.Remove(GetCacheKey(request.EmoteBoardId));
        return Unit.Task;
    }

    public async Task<List<ulong>> Handle(GetEmoteBoardChannelsRequest request, CancellationToken cancellationToken) =>
        await _cache.GetOrAddAsync(GetCacheKey(request.EmoteBoardId),
            () => _context.EmoteBoardChannelMappings
                .Where(cm => cm.EmoteBoardId == request.EmoteBoardId)
                .Select(cm => cm.ChannelId)
                .ToListAsync(), TimeSpan.FromHours(12));

    private static string GetCacheKey(int emoteBoardId) => $"{typeof(EmoteBoardChannelCacheHandler)}:{emoteBoardId}";
}
