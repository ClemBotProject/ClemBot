using MediatR;

namespace ClemBot.Api.Services.Caching.Users.Models;

public class UserExistsRequest : ICacheRequest, IRequest<bool>
{
    public ulong Id { get; init; }
}
