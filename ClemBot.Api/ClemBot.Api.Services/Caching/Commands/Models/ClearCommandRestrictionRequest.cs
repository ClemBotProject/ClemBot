using MediatR;

namespace ClemBot.Api.Services.Caching.Commands.Models;

public class ClearCommandRestrictionRequest : ICacheRequest, IRequest
{
    public ulong Id { get; init; }

    public string CommandName { get; set; }
}
