using MediatR;

namespace ClemBot.Api.Services.Messages.Models;

public class MessageExistsRequest : IRequest<bool>
{
    public ulong Id { get; init; }
}