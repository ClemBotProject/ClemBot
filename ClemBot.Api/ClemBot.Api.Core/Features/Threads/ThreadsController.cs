using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using ClemBot.Api.Common.Utilities;
using ClemBot.Api.Core.Features.Threads.Bot;
using MediatR;
using Microsoft.AspNetCore.Mvc;
using Index = ClemBot.Api.Core.Features.Threads.Bot.Index;

namespace ClemBot.Api.Core.Features.Threads;

[ApiController]
[Route("api")]
public class ThreadsController : ControllerBase
{
    private readonly IMediator _mediator;

    public ThreadsController(IMediator mediator)
    {
        _mediator = mediator;
    }

    [HttpGet("bot/[controller]")]
    public async Task<IActionResult> Index() =>
        await _mediator.Send(new Index.Query()) switch
        {
            { Status: QueryStatus.Success } result => Ok(result.Value),
            _ => Ok(new List<ulong>())
        };

    [HttpGet("bot/[controller]/{Id}")]
    public async Task<IActionResult> Details([FromRoute] Details.Query query) =>
        await _mediator.Send(query) switch
        {
            { Status: QueryStatus.Success } result => Ok(result.Value),
            _ => NoContent()
        };

    [HttpDelete("bot/[controller]/{Id}")]
    public async Task<IActionResult> Delete([FromRoute] Delete.Query query) =>
        await _mediator.Send(query) switch
        {
            { Status: QueryStatus.Success } result => Ok(result.Value),
            { Status: QueryStatus.NotFound } => NoContent(),
            _ => throw new InvalidOperationException()
        };

    [HttpPost("bot/[controller]")]
    public async Task<IActionResult> Create(Create.Command command) =>
        await _mediator.Send(command) switch
        {
            { Status: QueryStatus.Success } result => Ok(result.Value),
            { Status: QueryStatus.Conflict } => Conflict(),
            _ => throw new InvalidOperationException()
        };

    [HttpPatch("bot/[controller]")]
    public async Task<IActionResult> Edit(Edit.Command command) =>
        await _mediator.Send(command) switch
        {
            { Status: QueryStatus.Success } result => Ok(result.Value),
            _ => NotFound()
        };
}