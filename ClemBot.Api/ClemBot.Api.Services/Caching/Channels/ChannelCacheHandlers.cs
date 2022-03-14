using System;
using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Services.Caching.Channels.Models;
using LazyCache;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Services.Caching.Channels;

public class ChannelCacheHandlers :
    RequestHandler<ClearChannelRequest>,
    IRequestHandler<ChannelExistsRequest, bool>
{
    private readonly IAppCache _cache;

    private readonly ClemBotContext _context;

    public ChannelCacheHandlers(IAppCache cache, ClemBotContext context)
    {
        _cache = cache;
        _context = context;
    }

    public async Task<bool> Handle(ChannelExistsRequest request, CancellationToken cancellationToken)
        => await _cache.GetOrAddAsync(GetCacheKey(request.Id),
            () => _context.Channels.AnyAsync(x => x.Id == request.Id),
            TimeSpan.FromHours(6));

    protected override void Handle(ClearChannelRequest request)
        => _cache.Remove(GetCacheKey(request.Id));

    private static string GetCacheKey(ulong id)
        => $"{nameof(ChannelExistsRequest)}:{id}";

}
