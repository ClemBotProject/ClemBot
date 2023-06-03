using ClemBot.Api.Common.Security.Policies.BotMaster;
using Microsoft.AspNetCore.Mvc;
using Index = ClemBot.Api.Core.Features.EmoteBoardPosts.Bot.Index;

namespace ClemBot.Api.Core.Features.EmoteBoardPosts;

[ApiController]
[Route("api")]
public class EmoteBoardPostsController : ControllerBase
{

    private readonly IMediator _mediator;

    public EmoteBoardPostsController(IMediator mediator)
    {
        _mediator = mediator;
    }

    [HttpGet("bot/[controller]")]
    [BotMasterAuthorize]
    public async Task<IActionResult> Index([FromBody] Index.Query query) =>
        await _mediator.Send(query) switch
        {
            { Status: QueryStatus.Success } result => Ok(result.Value),
            { Status: QueryStatus.NotFound } => NotFound(),
            _ => throw new InvalidOperationException()
        };
}
