using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Services.Caching.CustomPrefix.Models;
using LazyCache;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Services.Caching.CustomPrefix;

public class CustomPrefixHandlers :
    RequestHandler<ClearCustomPrefixRequest>,
    IRequestHandler<GetCustomPrefixRequest, IEnumerable<string>>
{
    private readonly IAppCache _cache;

    private readonly ClemBotContext _context;

    public CustomPrefixHandlers(IAppCache cache, ClemBotContext context)
    {
        _cache = cache;
        _context = context;
    }

    public async Task<IEnumerable<string>> Handle(GetCustomPrefixRequest request, CancellationToken cancellationToken)
        => await _cache.GetOrAddAsync(GetCacheKey(request.Id),
            () => _context.CustomPrefixs
                .Where(x => x.Guild.Id == request.Id)
                .Select(y => y.Prefix)
                .ToListAsync(),
            TimeSpan.FromHours(12));

    protected override void Handle(ClearCustomPrefixRequest request)
        => _cache.Remove(GetCacheKey(request.Id));

    private static string GetCacheKey(ulong id)
        => $"{nameof(GetCustomPrefixRequest)}:{id}";
}
