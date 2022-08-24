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
public class CommandsController : ControllerBase
{
    private readonly IMediator _mediator;

    public CommandsController(IMediator mediator)
    {
        _mediator = mediator;
    }

    [HttpPost("bot/[controller]")]
    [BotMasterAuthorize]
    public async Task<IActionResult> AddInvocation(AddInvocation.Command command) =>
        await _mediator.Send(command) switch
        {
            { Status: QueryStatus.Success } result => Ok(result.Value),
            _ => throw new InvalidOperationException()
        };

    [HttpGet("bot/[controller]/{GuildId}/{ChannelId}/{CommandName}/status")]
    [BotMasterAuthorize]
    public async Task<IActionResult> Status([FromRoute] Status.Query query) =>
        await _mediator.Send(query) switch
        {
            { Status: QueryStatus.Success } result => Ok(result.Value),
            { Status: QueryStatus.NotFound } => NotFound(),
            _ => throw new InvalidOperationException()
        };

    [HttpGet("bot/[controller]/{GuildId}/{ChannelId}/{CommandName}/details")]
    [BotMasterAuthorize]
    public async Task<IActionResult> Details([FromRoute] Details.Command command) =>
        await _mediator.Send(command) switch
        {
            { Status: QueryStatus.Success } result => Ok(result.Value),
            { Status: QueryStatus.NotFound } => NotFound(),
            _ => throw new InvalidOperationException()
        };

    [HttpDelete("bot/[controller]/enable")]
    [BotMasterAuthorize]
    public async Task<IActionResult> Enable([FromBody] Enable.Query query) =>
        await _mediator.Send(query) switch
        {
            { Status: QueryStatus.NoContent } => NoContent(),
            { Status: QueryStatus.NotFound } => NotFound(),
            _ => throw new InvalidOperationException()
        };

    [HttpPut("/bot/[controller]/disable")]
    [BotMasterAuthorize]
    public async Task<IActionResult> Disable([FromBody] Disable.Query query) =>
        await _mediator.Send(query) switch
        {
            { Status: QueryStatus.NoContent } => NoContent(),
            { Status: QueryStatus.Conflict } => Conflict(),
            { Status: QueryStatus.NotFound } => NotFound(),
            _ => throw new InvalidOperationException()
        };
}
