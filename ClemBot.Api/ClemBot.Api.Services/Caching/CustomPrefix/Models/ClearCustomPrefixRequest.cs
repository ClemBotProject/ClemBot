using MediatR;

namespace ClemBot.Api.Services.Caching.CustomPrefix.Models;

public class ClearCustomPrefixRequest : ICacheRequest, IRequest
{
    public ulong Id { get; init; }
}
