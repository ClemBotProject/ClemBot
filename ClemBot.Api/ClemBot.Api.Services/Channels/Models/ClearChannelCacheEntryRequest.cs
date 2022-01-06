using MediatR;
using Microsoft.AspNetCore.Diagnostics;

namespace ClemBot.Api.Services.Channels.Models;

public class ClearChannelCacheEntryRequest : IRequest
{
    public ulong Id { get; init; }
}
