using System;
using System.Threading.Tasks;
using ClemBot.Api.Common.Security.Policies.BotMaster;
using ClemBot.Api.Common.Utilities;
using ClemBot.Api.Core.Features.DesignatedChannels.Bot;
using MediatR;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Index = ClemBot.Api.Core.Features.DesignatedChannels.Bot.Index;

namespace ClemBot.Api.Core.Features.DesignatedChannels;

[ApiController]
[Route("api")]
public class DesignatedChannelsController : ControllerBase
{
    private readonly IMediator _mediator;

    public DesignatedChannelsController(IMediator mediator)
    {
        _mediator = mediator;
    }

    [HttpGet("bot/[controller]/{Designation}/index")]
    [BotMasterAuthorize]
    public async Task<IActionResult> Index([FromRoute] Index.Query command) =>
        await _mediator.Send(command) switch
        {
            { Status: QueryStatus.Success } result => Ok(result.Value),
            _ => NoContent()
        };

    [HttpGet("bot/[controller]/details")]
    [BotMasterAuthorize]
    public async Task<IActionResult> Details(Details.Command command) =>
        await _mediator.Send(command) switch
        {
            { Status: QueryStatus.Success } result => Ok(result.Value),
            _ => NoContent()
        };

    [HttpDelete("bot/[controller]")]
    [BotMasterAuthorize]
    public async Task<IActionResult> Delete(Delete.Command query) =>
        await _mediator.Send(query) switch
        {
            { Status: QueryStatus.Success } result => Ok(result.Value),
            { Status: QueryStatus.NotFound } => NoContent(),
            _ => throw new InvalidOperationException()
        };

    [HttpPost("bot/[controller]")]
    [BotMasterAuthorize]
    public async Task<IActionResult> Register(Register.Command command) =>
        await _mediator.Send(command) switch
        {
            { Status: QueryStatus.Success } result => Ok(result.Value),
            { Status: QueryStatus.Conflict } => Conflict(),
            { Status: QueryStatus.Invalid } => BadRequest("Can not register a thread"),
            _ => throw new InvalidOperationException()
        };
}