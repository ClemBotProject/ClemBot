using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Data.Models;
using ClemBot.Api.Services.Caching.EmoteBoards.Models;
using LazyCache;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Services.Caching.EmoteBoards;

public class EmoteBoardCacheHandler : IRequestHandler<ClearEmoteBoardsRequest>,
    IRequestHandler<GetEmoteBoardsRequest, List<EmoteBoard>>
{

    private readonly IAppCache _cache;
    private readonly ClemBotContext _context;

    public EmoteBoardCacheHandler(IAppCache cache, ClemBotContext context)
    {
        _cache = cache;
        _context = context;
    }

    public Task<Unit> Handle(ClearEmoteBoardsRequest request, CancellationToken cancellationToken)
    {
        _cache.Remove(GetCacheKey(request.GuildId));
        return Unit.Task;
    }

    public async Task<List<EmoteBoard>> Handle(GetEmoteBoardsRequest request, CancellationToken cancellationToken) =>
        await _cache.GetOrAddAsync(GetCacheKey(request.GuildId), async () =>
            await _context.EmoteBoards
                .Include(b => b.Channels)
                .ThenInclude(c => c.EmoteBoards)
                .Where(b => b.GuildId == request.GuildId)
                .ToListAsync(), TimeSpan.FromHours(12));

    private static string GetCacheKey(ulong guildId) => $"{typeof(EmoteBoardCacheHandler)}:{guildId}";
}
