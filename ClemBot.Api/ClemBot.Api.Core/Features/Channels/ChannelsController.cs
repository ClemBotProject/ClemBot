using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using ClemBot.Api.Common.Security.Policies.BotMaster;
using ClemBot.Api.Common.Utilities;
using ClemBot.Api.Core.Features.Channels.Bot;
using MediatR;
using Microsoft.AspNetCore.Mvc;
using Index = ClemBot.Api.Core.Features.Channels.Bot.Index;

namespace ClemBot.Api.Core.Features.Channels;

[ApiController]
[Route("api")]
public class ChannelsController : ControllerBase
{
    private readonly IMediator _mediator;

    public ChannelsController(IMediator mediator)
    {
        _mediator = mediator;
    }

    [HttpGet("bot/[controller]")]
    [BotMasterAuthorize]
    public async Task<IActionResult> Index() =>
        await _mediator.Send(new Index.Query()) switch
        {
            { Status: QueryStatus.Success } result => Ok(result.Value),
            _ => Ok(new List<ulong>())
        };

    [HttpGet("bot/[controller]/{Id}")]
    [BotMasterAuthorize]
    public async Task<IActionResult> Details([FromRoute] Details.Query query) =>
        await _mediator.Send(query) switch
        {
            { Status: QueryStatus.Success } result => Ok(result.Value),
            _ => NoContent()
        };

    [HttpDelete("bot/[controller]/{Id}")]
    [BotMasterAuthorize]
    public async Task<IActionResult> Delete([FromRoute] Delete.Query query) =>
        await _mediator.Send(query) switch
        {
            { Status: QueryStatus.Success } result => Ok(result.Value),
            { Status: QueryStatus.NotFound } => NoContent(),
            _ => throw new InvalidOperationException()
        };

    [HttpPost("bot/[controller]")]
    [BotMasterAuthorize]
    public async Task<IActionResult> Create(Create.Command command) =>
        await _mediator.Send(command) switch
        {
            { Status: QueryStatus.Success } result => Ok(result.Value),
            { Status: QueryStatus.Conflict } => Conflict(),
            _ => throw new InvalidOperationException()
        };

    [HttpPatch("bot/[controller]")]
    [BotMasterAuthorize]
    public async Task<IActionResult> Edit(Edit.Command command) =>
        await _mediator.Send(command) switch
        {
            { Status: QueryStatus.Success } result => Ok(result.Value),
            _ => NotFound()
        };
}
