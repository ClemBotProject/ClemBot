using System;
using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Services.Caching.Messages.Models;
using LazyCache;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Services.Caching.Messages;

public class CheckMessageExistsHandler : IRequestHandler<MessageExistsRequest, bool>
{
    private readonly IAppCache _cache;

    private readonly ClemBotContext _context;

    public CheckMessageExistsHandler(IAppCache cache, ClemBotContext context)
    {
        _cache = cache;
        _context = context;
    }

    public async Task<bool> Handle(MessageExistsRequest request, CancellationToken cancellationToken) =>
        await _cache.GetOrAddAsync(GetCacheKey(request.Id),
            () => _context.Messages.AnyAsync(x => x.Id == request.Id),
            TimeSpan.FromHours(3));

    private static string GetCacheKey(ulong id)
        => $"{nameof(MessageExistsRequest)}:{id}";
}
