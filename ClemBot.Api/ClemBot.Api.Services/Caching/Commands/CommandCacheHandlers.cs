using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Data.Models;
using ClemBot.Api.Services.Caching.Commands.Models;
using LazyCache;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Services.Caching.Commands;

public class CommandCacheHandlers : RequestHandler<ClearCommandRestrictionRequest>,
    IRequestHandler<GetCommandRestrictionRequest, List<CommandRestriction>>
{

    private readonly IAppCache _cache;
    private readonly ClemBotContext _context;

    public CommandCacheHandlers(IAppCache cache, ClemBotContext context)
    {
        _cache = cache;
        _context = context;
    }

    protected override void Handle(ClearCommandRestrictionRequest request) =>
        _cache.Remove(GetCacheKey(request.Id, request.CommandName));

    public async Task<List<CommandRestriction>> Handle(GetCommandRestrictionRequest request, CancellationToken cancellationToken) =>
        await _cache.GetOrAddAsync(GetCacheKey(request.Id, request.CommandName),
            () => _context.CommandRestrictions
                .Where(c => c.GuildId == request.Id && c.CommandName == request.CommandName)
                .Select(item => new CommandRestriction
                {
                    Id = item.Id,
                    GuildId = item.GuildId,
                    CommandName = item.CommandName,
                    ChannelId = item.ChannelId,
                    SilentlyFail = item.SilentlyFail
                })
                .ToListAsync(), TimeSpan.FromHours(12));

    private static string GetCacheKey(ulong id, string commandName) =>
        $"{nameof(GetCommandRestrictionRequest)}:{id}:{commandName}";
}
