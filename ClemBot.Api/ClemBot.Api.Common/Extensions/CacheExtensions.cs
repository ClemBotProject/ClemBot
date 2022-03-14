using System.Reflection;
using LazyCache;
using Microsoft.Extensions.Caching.Memory;

namespace ClemBot.Api.Common.Extensions;

public static class CacheExtensions
{
    public static int Size(this IAppCache cache)
    {
        var memCache =  cache.CacheProvider.GetType().GetField("cache", BindingFlags.NonPublic | BindingFlags.Instance)?
            .GetValue(cache.CacheProvider) as MemoryCache;

        if (memCache is null)
        {
            throw new InvalidOperationException("Getting Mem-cache instance failed");
        }

        return memCache.Count;
    }
}
