using ClemBot.Api.Common.Extensions;
using ClemBot.Api.Services.Caching;
using LazyCache;

namespace ClemBot.Api.Core.Behaviors;

public class CacheRequestBehavior<TRequest, TResponse> :
    IPipelineBehavior<TRequest, TResponse> where TRequest : ICacheRequest
{
    private readonly ILogger<CacheRequestBehavior<TRequest, TResponse>> _logger;

    private readonly IAppCache _cache;

    public CacheRequestBehavior(ILogger<CacheRequestBehavior<TRequest, TResponse>> logger, IAppCache cache)
    {
        _logger = logger;
        _cache = cache;
    }

    public async Task<TResponse> Handle(TRequest request,
        CancellationToken cancellationToken,
        RequestHandlerDelegate<TResponse> next)
    {
        _logger.LogInformation("Cache Request: {Request} for Id: {Id}", typeof(TRequest).Name, request.Id);
        var result = await next();
        _logger.LogInformation("{Cache} request for Id: {Id} completed with result: {Result}",
            typeof(TRequest).Name,
            request.Id,
            result);

        _logger.LogInformation("Current API internal cache size: {Size}", _cache.Size());

        return result;
    }
}
