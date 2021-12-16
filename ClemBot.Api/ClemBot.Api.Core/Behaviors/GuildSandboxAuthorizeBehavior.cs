using System.Security.Claims;
using ClemBot.Api.Common;
using ClemBot.Api.Common.Security.Policies.GuildSandbox;
using ClemBot.Api.Common.Utilities;
using ClemBot.Api.Services.Authorization;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore.Metadata.Internal;

namespace ClemBot.Api.Core.Behaviors;

public class GuildSandboxAuthorizeBehavior<TRequest, TResponse> :
    IPipelineBehavior<TRequest, TResponse>
    where TRequest : IGuildSandboxModel
{
    private readonly ILogger<GuildSandboxAuthorizeBehavior<TRequest, TResponse>> _logger;

    private readonly IGuildSandboxAuthorizeService _authorizeService;

    public GuildSandboxAuthorizeBehavior(ILogger<GuildSandboxAuthorizeBehavior<TRequest, TResponse>> logger,
        IGuildSandboxAuthorizeService authorizeService)
    {
        _logger = logger;
        _authorizeService = authorizeService;
    }

    public async Task<TResponse> Handle(TRequest request,
        CancellationToken cancellationToken,
        RequestHandlerDelegate<TResponse> next)
    {
        if (!await _authorizeService.AuthorizeUser(request))
        {
            var genericResultType = typeof(TResponse).GetGenericArguments().First();
            var resultType = typeof(QueryResult<>).MakeGenericType(genericResultType);
            return (TResponse) Activator.CreateInstance(resultType, QueryStatus.Forbidden)!;
        }

        return await next();
    }

}
