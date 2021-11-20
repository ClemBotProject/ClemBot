using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Services.CustomPrefix.Models;
using LazyCache;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Services.CustomPrefix;

public class GetCustomPrefixHandler : IRequestHandler<GetCustomPrefixRequest, IEnumerable<string>>
{
    private readonly IAppCache _cache;

    private readonly ClemBotContext _context;

    public GetCustomPrefixHandler(IAppCache cache, ClemBotContext context)
    {
        _cache = cache;
        _context = context;
    }

    public async Task<IEnumerable<string>> Handle(GetCustomPrefixRequest request, CancellationToken cancellationToken) =>
        await _cache.GetOrAddAsync(GetCacheKey(request.Id),
            () => _context.CustomPrefixs
                .Where(x => x.Guild.Id == request.Id)
                .Select(y => y.Prefix)
                .ToListAsync());

    private static string GetCacheKey(ulong id)
        => $"{nameof(GetCustomPrefixRequest)}:{id}";
}