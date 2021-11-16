using MediatR;

namespace ClemBot.Api.Services.Users.Models;

public class UserExistsRequest : IRequest<bool>
{
    public ulong Id { get; init; }
}