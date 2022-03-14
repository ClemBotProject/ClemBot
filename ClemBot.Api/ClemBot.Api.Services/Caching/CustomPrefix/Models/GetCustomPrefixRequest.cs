using System.Collections.Generic;
using MediatR;

namespace ClemBot.Api.Services.Caching.CustomPrefix.Models;

public class GetCustomPrefixRequest : ICacheRequest, IRequest<IEnumerable<string>>
{
    public ulong Id { get; init; }
}
