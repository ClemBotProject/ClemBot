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

public class CommandCacheHandler : IRequestHandler<ClearCommandRestrictionRequest>,
    IRequestHandler<GetCommandRestrictionRequest, List<CommandRestriction>>
{

    private readonly IAppCache _cache;
    private readonly ClemBotContext _context;

    public CommandCacheHandler(IAppCache cache, ClemBotContext context)
    {
        _cache = cache;
        _context = context;
    }

    public Task Handle(ClearCommandRestrictionRequest request, CancellationToken cancellationToken)
    {
        _cache.Remove(GetCacheKey(request.Id, request.CommandName));
        return Task.CompletedTask;
    }

    public async Task<List<CommandRestriction>> Handle(GetCommandRestrictionRequest request, CancellationToken cancellationToken) =>
        await _cache.GetOrAddAsync(GetCacheKey(request.Id, request.CommandName),
            () => _context.CommandRestrictions
                .Where(c => c.GuildId == request.Id && c.CommandName == request.CommandName)
                .Select(item => new CommandRestriction
                {
                    Id = item.Id,
                    GuildId = item.GuildId,
                    CommandName = item.CommandName,
                    RestrictionType = item.RestrictionType,
                    ChannelId = item.ChannelId,
                    SilentlyFail = item.SilentlyFail
                })
                .ToListAsync(), TimeSpan.FromHours(12));

    private static string GetCacheKey(ulong id, string commandName) =>
        $"{nameof(GetCommandRestrictionRequest)}:{id}:{commandName}";
}
