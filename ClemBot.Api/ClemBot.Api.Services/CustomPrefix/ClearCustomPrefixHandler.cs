using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Services.CustomPrefix.Models;
using LazyCache;
using MediatR;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Internal;

namespace ClemBot.Api.Services.CustomPrefix;

public class ClearCustomPrefixHandler : RequestHandler<ClearCustomPrefixRequest>
{
    private readonly IAppCache _cache;

    private readonly ClemBotContext _context;

    public ClearCustomPrefixHandler(IAppCache cache, ClemBotContext context)
    {
        _cache = cache;
        _context = context;
    }

    protected override void Handle(ClearCustomPrefixRequest request)
        => _cache.Remove(GetCacheKey(request.Id));

    private static string GetCacheKey(ulong id)
        => $"{nameof(GetCustomPrefixRequest)}:{id}";

}