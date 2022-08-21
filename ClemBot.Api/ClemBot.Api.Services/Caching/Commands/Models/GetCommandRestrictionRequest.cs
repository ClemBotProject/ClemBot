using System.Collections.Generic;
using ClemBot.Api.Data.Models;
using MediatR;

namespace ClemBot.Api.Services.Caching.Commands.Models;

public class GetCommandRestrictionRequest : ICacheRequest, IRequest<List<CommandRestriction>>
{
    public ulong Id { get; init; }

    public string CommandName { get; set; }
}
