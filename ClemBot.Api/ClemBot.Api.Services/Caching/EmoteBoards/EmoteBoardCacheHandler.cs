using System;
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

public class EmoteBoardCacheHandler : IRequestHandler<ClearEmoteBoardsRequest>,
    IRequestHandler<GetEmoteBoardsRequest, List<EmoteBoardDto>>
{

    private readonly IAppCache _cache;
    private readonly ClemBotContext _context;

    public EmoteBoardCacheHandler(IAppCache cache, ClemBotContext context)
    {
        _cache = cache;
        _context = context;
    }

    public Task<Unit> Handle(ClearEmoteBoardsRequest request, CancellationToken cancellationToken)
    {
        _cache.Remove(GetCacheKey(request.GuildId));
        return Unit.Task;
    }

    public async Task<List<EmoteBoardDto>> Handle(GetEmoteBoardsRequest request, CancellationToken cancellationToken) =>
        await _cache.GetOrAddAsync(GetCacheKey(request.GuildId), async () => {
            var dtos = new List<EmoteBoardDto>();
            var boards = await _context.EmoteBoards
                .Where(b => b.GuildId == request.GuildId)
                .ToListAsync();
            var boardIds = boards.Select(board => board.Id);
            var channels = await _context.EmoteBoardChannelMappings
                .Where(cm => boardIds.Contains(cm.EmoteBoardId))
                .ToListAsync();
            foreach (var board in boards)
            {
                var boardChannels = channels
                    .Where(cm => cm.EmoteBoardId == board.Id)
                    .Select(cm => cm.ChannelId)
                    .ToList();
                dtos.Add(new EmoteBoardDto
                {
                    GuildId = board.GuildId,
                    Name = board.Name,
                    Emote = board.Emote,
                    ReactionThreshold = board.ReactionThreshold,
                    AllowBotPosts = board.AllowBotPosts,
                    Channels = boardChannels
                });
            }
            return dtos;
        }, TimeSpan.FromHours(12));

    private static string GetCacheKey(ulong guildId) => $"{typeof(EmoteBoardCacheHandler)}:{guildId}";
}
