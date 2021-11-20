using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Services.Guilds.Models;
using LazyCache;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Services.Guilds;

public class CheckGuildExistsHandler : IRequestHandler<GuildExistsRequest, bool>
{
    private readonly IAppCache _cache;

    private readonly ClemBotContext _context;

    public CheckGuildExistsHandler(IAppCache cache, ClemBotContext context)
    {
        _cache = cache;
        _context = context;
    }

    public async Task<bool> Handle(GuildExistsRequest request, CancellationToken cancellationToken) =>
        await _cache.GetOrAddAsync(GetCacheKey(request.Id),
            () => _context.Guilds.AnyAsync(x => x.Id == request.Id));

    private string GetCacheKey(ulong id)
        => $"{nameof(GuildExistsRequest)}:{id}";
}