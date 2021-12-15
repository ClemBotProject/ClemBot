using System;
using System.Threading.Tasks;
using ClemBot.Api.Common.Security.Policies.BotMaster;
using ClemBot.Api.Common.Utilities;
using ClemBot.Api.Core.Features.Messages;
using MediatR;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace ClemBot.Api.Core.Features.Messages;

[ApiController]
[Route("api")]
public class MessagesController : ControllerBase
{
    private readonly IMediator _mediator;

    public MessagesController(IMediator mediator)
    {
        _mediator = mediator;
    }

    [HttpPost("bot/[controller]")]
    [BotMasterAuthorize]
    public async Task<IActionResult> Create(Bot.Create.Command command) =>
        await _mediator.Send(command) switch
        {
            { Status: QueryStatus.Success } result => Ok(result.Value),
            { Status: QueryStatus.NotFound } => NotFound(),
            _ => throw new InvalidOperationException()
        };

    [HttpPatch("bot/[controller]")]
    [BotMasterAuthorize]
    public async Task<IActionResult> Edit(Bot.Edit.Command command) =>
        await _mediator.Send(command) switch
        {
            { Status: QueryStatus.Success } result => Ok(result.Value),
            _ => NotFound()
        };

    [HttpGet("bot/[controller]/{Id}")]
    [BotMasterAuthorize]
    public async Task<IActionResult> Details([FromRoute] Bot.Details.Query query) =>
        await _mediator.Send(query) switch
        {
            { Status: QueryStatus.Success } result => Ok(result.Value),
            _ => NoContent()
        };

    [HttpGet("bot/[controller]/Count")]
    [BotMasterAuthorize]
    public async Task<IActionResult> Count(Bot.Count.Query query) =>
        await _mediator.Send(query) switch
        {
            {Status: QueryStatus.Success} result => Ok(result.Value),
            _ => NoContent()
        };
}