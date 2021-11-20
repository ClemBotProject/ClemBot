using System.Collections.Generic;
using MediatR;

namespace ClemBot.Api.Services.CustomPrefix.Models;

public class GetCustomPrefixRequest : IRequest<IEnumerable<string>>
{
    public ulong Id { get; init; }
}