using ClemBot.Api.Common.Security.Policies.BotMaster;
using ClemBot.Api.Core.Features.Reminders.Bot;
using Microsoft.AspNetCore.Mvc;

namespace ClemBot.Api.Core.Features.Reminders;

[ApiController]
[Route("api")]
public class RemindersController : ControllerBase
{

    private readonly IMediator _mediator;

    public RemindersController(IMediator mediator)
    {
        _mediator = mediator;
    }

    [HttpPost("bot/[controller]")]
    [BotMasterAuthorize]
    public async Task<IActionResult> Create(Create.Model model) =>
        await _mediator.Send(model) switch
        {
            { Status: QueryStatus.Success } result => Ok(result.Value),
            _ => throw new InvalidOperationException()
        };

    [HttpPatch("bot/[controller]/{Id}/dispatch")]
    [BotMasterAuthorize]
    public async Task<IActionResult> Dispatch([FromRoute] Dispatch.Query query) =>
        await _mediator.Send(query) switch
        {
            { Status: QueryStatus.Success } result => Ok(result.Value),
            { Status: QueryStatus.NotFound } => NotFound(),
            { Status: QueryStatus.Conflict } => Conflict(),
            _ => throw new InvalidOperationException()
        };

    [HttpGet("bot/[controller]/{Id}/details")]
    [BotMasterAuthorize]
    public async Task<IActionResult> Details([FromRoute] Details.Query query) =>
        await _mediator.Send(query) switch
        {
            { Status: QueryStatus.Success } result => Ok(result.Value),
            { Status: QueryStatus.NotFound } => NotFound(),
            _ => throw new InvalidOperationException()
        };
}
