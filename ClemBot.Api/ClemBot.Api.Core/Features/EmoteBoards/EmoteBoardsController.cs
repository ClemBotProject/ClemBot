using ClemBot.Api.Common.Security.Policies.BotMaster;
using Microsoft.AspNetCore.Mvc;

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
    public async Task<IActionResult> Index([FromRoute] Bot.Index.Query query) =>
        await _mediator.Send(query) switch
        {
            { Status: QueryStatus.Success } result => Ok(result.Value),
            { Status: QueryStatus.NotFound } => NotFound(),
            _ => throw new InvalidOperationException()
        };
}
