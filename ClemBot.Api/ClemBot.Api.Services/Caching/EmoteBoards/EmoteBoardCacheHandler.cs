using System;
using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Data.Models;
using ClemBot.Api.Services.Caching.EmoteBoards.Models;
using LazyCache;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Services.Caching.EmoteBoards;

public class EmoteBoardCacheHandler : IRequestHandler<GetEmoteBoardRequest, EmoteBoard>,
    IRequestHandler<ClearEmoteBoardRequest, Unit>
{

    private readonly IAppCache _cache;
    private readonly ClemBotContext _context;

    public EmoteBoardCacheHandler(IAppCache cache, ClemBotContext context)
    {
        _cache = cache;
        _context = context;
    }

    public Task<Unit> Handle(ClearEmoteBoardRequest request, CancellationToken cancellationToken)
    {
        _cache.Remove(GetCacheKey(request.GuildId, request.Name));
        return Unit.Task;
    }

    public async Task<EmoteBoard> Handle(GetEmoteBoardRequest request, CancellationToken cancellationToken) =>
        await _context.EmoteBoards.FirstOrDefaultAsync(
            b => b.GuildId == request.GuildId
                 && string.Equals(b.Name, request.Name, StringComparison.OrdinalIgnoreCase));

    private static string GetCacheKey(ulong guildId, string name) => $"{nameof(EmoteBoardCacheHandler)}:{guildId}:{name}";
}
