using ClemBot.Api.Services.Caching;

namespace ClemBot.Api.Core.Behaviors;

public class CacheRequestBehavior<TRequest, TResponse> :
    IPipelineBehavior<TRequest, TResponse> where TRequest : ICacheRequest
{
    private readonly ILogger<CacheRequestBehavior<TRequest, TResponse>> _logger;

    public CacheRequestBehavior(ILogger<CacheRequestBehavior<TRequest, TResponse>> logger)
    {
        _logger = logger;
    }

    public async Task<TResponse> Handle(TRequest request,
        CancellationToken cancellationToken,
        RequestHandlerDelegate<TResponse> next)
    {
        _logger.LogInformation("Cache Request for  Data: {@Data}", request.GetType(), request);
        var response = await next();
        _logger.LogInformation("Response Data: {@Body}", response);

        return response;
    }
}
