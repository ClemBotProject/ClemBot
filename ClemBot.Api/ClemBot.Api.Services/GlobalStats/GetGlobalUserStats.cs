using System;
using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Services.GlobalStats.Models;
using LazyCache;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Services.GlobalStats
{
    public class GetGlobalUserStats : IRequestHandler<GlobalUserStatsRequest, int>
    {
        private readonly IAppCache _cache;

        private readonly ClemBotContext _context;

        public GetGlobalUserStats(IAppCache cache, ClemBotContext context)
        {
            _cache = cache;
            _context = context;
        }

        public async Task<int> Handle(GlobalUserStatsRequest request, CancellationToken cancellationToken) =>
            await _cache.GetOrAddAsync(GetCacheKey(),
                () => _context.Users.CountAsync(), TimeSpan.FromHours(1));

        private string GetCacheKey()
            => $"{nameof(GetGlobalUserStats)}";    }
}
