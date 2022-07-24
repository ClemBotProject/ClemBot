using System.Text.Json;
using ClemBot.Api.Common;

namespace ClemBot.Api.Core.Behaviors;

public class LoggingBehavior<TRequest, TResponse> : IPipelineBehavior<TRequest, TResponse> where TRequest : notnull
{
    private readonly ILogger<LoggingBehavior<TRequest, TResponse>> _logger;

    public LoggingBehavior(ILogger<LoggingBehavior<TRequest, TResponse>> logger)
    {
        _logger = logger;
    }

    public async Task<TResponse> Handle(TRequest request,
        CancellationToken cancellationToken,
        RequestHandlerDelegate<TResponse> next)
    {
        _logger.LogInformation("{Request} Request Data: {@Data}", typeof(TRequest), request);
        var response = await next();

        var bodyJson = JsonSerializer.Serialize(response);

        if (sizeof(char) * bodyJson.Length < Constants.SeqBodySizeMax)
        {
            _logger.LogInformation("{Response} Response Data: {Body}", typeof(TRequest), bodyJson);
        }
        else
        {
            _logger.LogInformation("Response Data with type {Type} exceeded max logging body size", typeof(TResponse));
        }

        return response;
    }
}
