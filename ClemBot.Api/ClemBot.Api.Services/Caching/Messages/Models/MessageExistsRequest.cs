using MediatR;

namespace ClemBot.Api.Services.Caching.Messages.Models;

public class MessageExistsRequest : IRequest<bool>
{
    public ulong Id { get; init; }
}
