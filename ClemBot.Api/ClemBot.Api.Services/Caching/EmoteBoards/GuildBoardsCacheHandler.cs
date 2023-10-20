using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Services.Caching.EmoteBoards.Models;
using LazyCache;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Services.Caching.EmoteBoards;

public class GuildBoardsCacheHandler : IRequestHandler<GetGuildBoardsRequest, Dictionary<string, string>>,
    IRequestHandler<ClearGuildBoardsRequest, Unit>
{

    private readonly IAppCache _cache;
    private readonly ClemBotContext _context;

    public GuildBoardsCacheHandler(IAppCache cache, ClemBotContext context)
    {
        _cache = cache;
        _context = context;
    }

    public Task<Unit> Handle(ClearGuildBoardsRequest request, CancellationToken cancellationToken)
    {
        _cache.Remove(GetCacheKey(request.GuildId));
        return Unit.Task;
    }

    public async Task<Dictionary<string, string>> Handle(GetGuildBoardsRequest request, CancellationToken cancellationToken) =>
        await _context.EmoteBoards
            .Where(b => b.GuildId == request.GuildId)
            .ToDictionaryAsync(b => b.Name, b => b.Emote);

    private static string GetCacheKey(ulong guildId) => $"{nameof(GuildBoardsCacheHandler)}:{guildId}";
}
