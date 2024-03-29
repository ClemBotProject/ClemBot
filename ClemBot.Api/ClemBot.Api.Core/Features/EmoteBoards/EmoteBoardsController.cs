﻿using ClemBot.Api.Common.Security.Policies.BotMaster;
using ClemBot.Api.Core.Features.EmoteBoards.Bot;
using Microsoft.AspNetCore.Mvc;
using Index = ClemBot.Api.Core.Features.EmoteBoards.Bot.Index;

namespace ClemBot.Api.Core.Features.EmoteBoards;

[ApiController]
[Route("api")]
public class EmoteBoardsController : ControllerBase
{

    private readonly IMediator _mediator;

    public EmoteBoardsController(IMediator mediator)
    {
        _mediator = mediator;
    }

    [HttpGet("bot/[controller]/{GuildId}")]
    [BotMasterAuthorize]
    public async Task<IActionResult> Index([FromRoute] Index.Query query) =>
        await _mediator.Send(query) switch
        {
            { Status: QueryStatus.Success } result => Ok(result.Value),
            { Status: QueryStatus.NotFound } => NotFound(),
            _ => throw new InvalidOperationException()
        };

    [HttpPost("bot/[controller]/create")]
    [BotMasterAuthorize]
    public async Task<IActionResult> Create([FromBody] Create.Command command) =>
        await _mediator.Send(command) switch
        {
            { Status: QueryStatus.NoContent } => NoContent(),
            { Status: QueryStatus.NotFound } => NotFound(),
            { Status: QueryStatus.Conflict } => Conflict(),
            _ => throw new InvalidOperationException()
        };

    [HttpPatch("bot/[controller]/edit")]
    [BotMasterAuthorize]
    public async Task<IActionResult> Edit([FromBody] Edit.Command command) =>
        await _mediator.Send(command) switch
        {
            { Status: QueryStatus.NoContent } => NoContent(),
            { Status: QueryStatus.NotFound } => NotFound(),
            { Status: QueryStatus.Conflict } => Conflict(),
            _ => throw new InvalidOperationException()
        };

    [HttpGet("bot/[controller]/{GuildId}/{Name}")]
    [BotMasterAuthorize]
    public async Task<IActionResult> Details([FromRoute] Details.Query query) =>
        await _mediator.Send(query) switch
        {
            { Status: QueryStatus.Success } result => Ok(result.Value),
            { Status: QueryStatus.NotFound } => NotFound(),
            _ => throw new InvalidOperationException()
        };

    [HttpDelete("bot/[controller]/delete")]
    [BotMasterAuthorize]
    public async Task<IActionResult> Delete([FromBody] Delete.Command command) =>
        await _mediator.Send(command) switch
        {
            { Status: QueryStatus.NoContent } => NoContent(),
            { Status: QueryStatus.NotFound } => NotFound(),
            _ => throw new InvalidOperationException()
        };
}
