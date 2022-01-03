using System;
using System.Threading.Tasks;
using ClemBot.Api.Common.Security.Policies.BotMaster;
using ClemBot.Api.Common.Utilities;
using ClemBot.Api.Core.Features.Commands.Bot;
using ClemBot.Api.Core.Features.Public;
using MediatR;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace ClemBot.Api.Core.Features.Commands;

[ApiController]
[Route("api")]
public class SlotScoresController : ControllerBase
{
    private readonly IMediator _mediator;

    public SlotScoresController(IMediator mediator)
    {
        _mediator = mediator;
    }

    [HttpPost("bot/[controller]")]
    [BotMasterAuthorize]
    public async Task<IActionResult> AddScore(AddScore.Command command) =>
        await _mediator.Send(command) switch
        {
            { Status: QueryStatus.Success } result => Ok(result.Value),
            _ => throw new InvalidOperationException()
        };
}
