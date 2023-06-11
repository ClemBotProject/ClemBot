using System;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Services.Caching.EmoteBoardPosts.Models;
using LazyCache;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Services.Caching.EmoteBoardPosts;

public class EmoteBoardPostCacheHandler : IRequestHandler<EmoteBoardPostExistsRequest, bool>,
    IRequestHandler<ClearEmoteBoardPostExistsRequest, Unit>
{

    private readonly IAppCache _cache;
    private readonly ClemBotContext _context;

    public EmoteBoardPostCacheHandler(IAppCache cache, ClemBotContext context)
    {
        _cache = cache;
        _context = context;
    }

    public Task<Unit> Handle(ClearEmoteBoardPostExistsRequest request, CancellationToken cancellationToken)
    {
        _cache.Remove(GetCacheKey(request.BoardId, request.MessageId));
        return Unit.Task;
    }

    public async Task<bool> Handle(EmoteBoardPostExistsRequest request, CancellationToken cancellationToken) =>
        await _cache.GetOrAddAsync(GetCacheKey(request.BoardId, request.MessageId), () => _context.EmoteBoardPosts
                .AnyAsync(p => p.MessageId == request.MessageId && p.EmoteBoardId == request.BoardId),
            TimeSpan.FromHours(12));

    private static string GetCacheKey(int boardId, ulong messageId) =>
        $"{nameof(EmoteBoardPostCacheHandler)}:{boardId}:{messageId}";
}
