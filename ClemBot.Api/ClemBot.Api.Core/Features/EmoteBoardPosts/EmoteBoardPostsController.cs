using ClemBot.Api.Common.Security.Policies.BotMaster;
using ClemBot.Api.Core.Features.EmoteBoardPosts.Bot;
using ClemBot.Api.Core.Features.EmoteBoardPosts.Bot.Leaderboard;
using Microsoft.AspNetCore.Mvc;

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

    [HttpPut("bot/[controller]/create")]
    [BotMasterAuthorize]
    public async Task<IActionResult> Create([FromBody] Create.Command command) =>
        await _mediator.Send(command) switch
        {
            { Status: QueryStatus.NoContent } => NoContent(),
            { Status: QueryStatus.Conflict } => Conflict(),
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

    [HttpGet("bot/[controller]/{GuildId}/{Name?}/{MessageId}")]
    [BotMasterAuthorize]
    public async Task<IActionResult> Details([FromRoute] Details.Query query) =>
        await _mediator.Send(query) switch
        {
            { Status: QueryStatus.Success } result => Ok(result.Value),
            { Status: QueryStatus.NotFound } => NotFound(),
            _ => throw new InvalidOperationException()
        };

    [HttpPatch("bot/[controller]/react")]
    [BotMasterAuthorize]
    public async Task<IActionResult> React([FromBody] React.Command command) =>
        await _mediator.Send(command) switch
        {
            { Status: QueryStatus.Success } result => Ok(result.Value),
            { Status: QueryStatus.NotFound } => NotFound(),
            { Status: QueryStatus.Conflict } => Conflict(),
            _ => throw new InvalidOperationException()
        };

    [HttpGet("bot/[controller]/leaderboard/{GuildId}/{Name?}/popular")]
    [BotMasterAuthorize]
    public async Task<IActionResult> Popular([FromRoute] Popular.Query query) =>
        await _mediator.Send(query) switch
        {
            { Status: QueryStatus.Success } result => Ok(result.Value),
            { Status: QueryStatus.NotFound } => NotFound(),
            _ => throw new InvalidOperationException()
        };

    [HttpGet("bot/[controller]/leaderboard/{GuildId}/{Name?}/posts")]
    [BotMasterAuthorize]
    public async Task<IActionResult> Posts([FromRoute] Posts.Query query) =>
        await _mediator.Send(query) switch
        {
            { Status: QueryStatus.Success } result => Ok(result.Value),
            { Status: QueryStatus.NotFound } => NotFound(),
            _ => throw new InvalidOperationException()
        };
}
