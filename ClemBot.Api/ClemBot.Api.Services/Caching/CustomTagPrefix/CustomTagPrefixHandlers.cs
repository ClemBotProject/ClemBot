using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Services.Caching.CustomTagPrefix.Models;
using LazyCache;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Services.Caching.CustomTagPrefix;

public class CustomTagPrefixHandlers :
    RequestHandler<ClearCustomTagPrefixRequest>,
    IRequestHandler<GetCustomTagPrefixRequest, IEnumerable<string>>
{
    private readonly IAppCache _cache;

    private readonly ClemBotContext _context;

    public CustomTagPrefixHandlers(IAppCache cache, ClemBotContext context)
    {
        _cache = cache;
        _context = context;
    }

    public async Task<IEnumerable<string>> Handle(GetCustomTagPrefixRequest request, CancellationToken cancellationToken)
        => await _cache.GetOrAddAsync(GetCacheKey(request.Id),
            () => _context.CustomTagPrefixs
                .Where(x => x.Guild.Id == request.Id)
                .Select(y => y.TagPrefix)
                .ToListAsync(),
            TimeSpan.FromHours(12));

    protected override void Handle(ClearCustomTagPrefixRequest request)
        => _cache.Remove(GetCacheKey(request.Id));

    private static string GetCacheKey(ulong id)
        => $"{nameof(GetCustomTagPrefixRequest)}:{id}";
}
