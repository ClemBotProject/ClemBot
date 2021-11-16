using MediatR;

namespace ClemBot.Api.Services.Channels.Models;

public class ChannelExistsRequest : IRequest<bool>
{
    public ulong Id { get; init; }
}