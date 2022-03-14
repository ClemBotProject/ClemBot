using System;
using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Services.Caching.Users.Models;
using LazyCache;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Services.Caching.Users;

public class CheckUserExists : IRequestHandler<UserExistsRequest, bool>
{
    private readonly IAppCache _cache;

    private readonly ClemBotContext _context;

    public CheckUserExists(IAppCache cache, ClemBotContext context)
    {
        _cache = cache;
        _context = context;
    }

    public async Task<bool> Handle(UserExistsRequest request, CancellationToken cancellationToken)
        => await _cache.GetOrAddAsync(GetCacheKey(request.Id),
            () => _context.Users.AnyAsync(x => x.Id == request.Id),
            TimeSpan.FromHours(12));

    private string GetCacheKey(ulong id)
        => $"{nameof(UserExistsRequest)}:{id}";
}
