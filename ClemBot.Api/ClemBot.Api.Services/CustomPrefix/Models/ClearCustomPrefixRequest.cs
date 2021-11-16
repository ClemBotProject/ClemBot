using System.Collections.Generic;
using MediatR;

namespace ClemBot.Api.Services.CustomPrefix.Models;

public class ClearCustomPrefixRequest : IRequest
{
    public ulong Id { get; init; }
}