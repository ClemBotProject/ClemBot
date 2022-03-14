using System;
using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Services.Caching.GlobalStats.Models;
using LazyCache;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Services.Caching.GlobalStats;

public class GetGlobalCommandStats : IRequestHandler<GlobalCommandStatsRequest, int>
{
    private readonly IAppCache _cache;

    private readonly ClemBotContext _context;

    public GetGlobalCommandStats(IAppCache cache, ClemBotContext context)
    {
        _cache = cache;
        _context = context;
    }

    public async Task<int> Handle(GlobalCommandStatsRequest request, CancellationToken cancellationToken)
        => await _cache.GetOrAddAsync(GetCacheKey(),
            () => _context.CommandInvocations.CountAsync(),
            DateTimeOffset.Now.AddMinutes(30));

    private string GetCacheKey()
        => $"{nameof(GetGlobalCommandStats)}";
}
