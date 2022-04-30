using MediatR;

namespace ClemBot.Api.Services.Caching.CustomTagPrefix.Models;

public class ClearCustomTagPrefixRequest : ICacheRequest, IRequest
{
    public ulong Id { get; init; }
}
