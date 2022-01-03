using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using ClemBot.Api.Common.Security.Policies.BotMaster;
using ClemBot.Api.Common.Utilities;
using MediatR;
using Microsoft.AspNetCore.Mvc;

namespace ClemBot.Api.Core.Features.Users;

[ApiController]
[Route("api")]
public class UsersController : ControllerBase
{
    private readonly IMediator _mediator;

    public UsersController(IMediator mediator)
    {
        _mediator = mediator;
    }

    [HttpGet("bot/[controller]")]
    [BotMasterAuthorize]
    public async Task<IActionResult> Index() =>
        await _mediator.Send(new Bot.Index.Query()) switch
        {
            { Status: QueryStatus.Success } result => Ok(result.Value),
            _ => Ok(new List<ulong>())
        };


    [HttpGet("bot/[controller]/{Id}")]
    [BotMasterAuthorize]
    public async Task<IActionResult> Details([FromRoute] Bot.Details.Query query) =>
        await _mediator.Send(query) switch
        {
            { Status: QueryStatus.Success } result => Ok(result.Value),
            _ => NoContent()
        };

    [HttpPost("bot/[controller]")]
    [BotMasterAuthorize]
    public async Task<IActionResult> Create(Bot.Create.Command command) =>
        await _mediator.Send(command) switch
        {
            { Status: QueryStatus.Success } result => Ok(result.Value),
            { Status: QueryStatus.Conflict } => Conflict(),
            _ => throw new InvalidOperationException()
        };

    [HttpGet("bot/[controller]/{UserId}/{GuildId}/slotscores")]
    //[BotMasterAuthorize]
    public async Task<IActionResult> Index([FromRoute] Bot.GetSlotsScores.Query command, int limit) =>
        await _mediator.Send(command with { Limit = limit}) switch
        {
            { Status: QueryStatus.Success } result => Ok(result.Value),
            { Status: QueryStatus.NotFound } => NoContent(),
            _ => throw new InvalidOperationException()
        };

    [HttpPost("bot/[controller]/CreateBulk")]
    [BotMasterAuthorize]
    public async Task<IActionResult> Create(Bot.CreateBulk.Command command) =>
        await _mediator.Send(command) switch
        {
            { Status: QueryStatus.Success } result => Ok(result.Value),
            { Status: QueryStatus.Conflict } => Conflict(),
            _ => throw new InvalidOperationException()
        };

    [HttpPatch("bot/[controller]")]
    [BotMasterAuthorize]
    public async Task<IActionResult> Edit(Bot.Edit.Command command) =>
        await _mediator.Send(command) switch
        {
            { Status: QueryStatus.Success } result => Ok(result.Value),
            { Status: QueryStatus.NotFound } => NotFound(),
            _ => throw new InvalidOperationException()
        };

    [HttpGet("bot/[controller]/infractions/{UserId}/{GuildId}/{Type?}")]
    [BotMasterAuthorize]
    public async Task<IActionResult> Infractions([FromRoute] Bot.Infractions.Query command) =>
        await _mediator.Send(command) switch
        {
            { Status: QueryStatus.Success } result => Ok(result.Value),
            { Status: QueryStatus.NotFound } => NotFound(),
            _ => throw new InvalidOperationException()
        };

    [HttpGet("bot/[controller]/{UserId}/{GuildId}/claims")]
    [BotMasterAuthorize]
    public async Task<IActionResult> Claims([FromRoute] Bot.GetGuildClaims.Query command) =>
        await _mediator.Send(command) switch
        {
            { Status: QueryStatus.Success } result => Ok(result.Value),
            { Status: QueryStatus.NotFound } => NotFound(),
            _ => throw new InvalidOperationException()
        };

    [HttpPost("bot/[controller]/{Id}/updateroles")]
    [BotMasterAuthorize]
    public async Task<IActionResult> UpdateRoles(ulong Id, Bot.UpdateRoles.Command command) =>
        await _mediator.Send(command with { Id = Id }) switch
        {
            { Status: QueryStatus.Success } result => Ok(result.Value),
            { Status: QueryStatus.NotFound } => NotFound(),
            _ => throw new InvalidOperationException()
        };
}
