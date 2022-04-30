using System.Collections.Generic;
using MediatR;

namespace ClemBot.Api.Services.Caching.CustomTagPrefix.Models;

public class GetCustomTagPrefixRequest : ICacheRequest, IRequest<IEnumerable<string>>
{
    public ulong Id { get; init; }
}
