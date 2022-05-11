using System;
using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Services.Caching.GlobalStats.Models;
using LazyCache;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Services.Caching.GlobalStats;

public class GetGlobalGuildStats : IRequestHandler<GlobalGuildStatsRequest, int>
{
    private readonly IAppCache _cache;

    private readonly ClemBotContext _context;

    public GetGlobalGuildStats(IAppCache cache, ClemBotContext context)
    {
        _cache = cache;
        _context = context;
    }

    public async Task<int> Handle(GlobalGuildStatsRequest request, CancellationToken cancellationToken)
        => await _cache.GetOrAddAsync(GetCacheKey(),
            () => _context.Guilds.CountAsync(),
            DateTimeOffset.Now.AddHours(1));

    private string GetCacheKey()
        => $"{nameof(GetGlobalGuildStats)}";
}
