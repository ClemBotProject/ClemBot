using ClemBot.Api.Common.Security.Policies.BotMaster;
using ClemBot.Api.Core.Features.EmoteBoardPosts.Bot;
using ClemBot.Api.Core.Features.EmoteBoardPosts.Bot.Leaderboard;
using Microsoft.AspNetCore.Mvc;

namespace ClemBot.Api.Core.Features.EmoteBoardPosts;

[ApiController]
[Route("api")]
public class EmoteBoardPostsController : ControllerBase
{

    private const int DefaultLimit = 5;

    private readonly IMediator _mediator;

    public EmoteBoardPostsController(IMediator mediator)
    {
        _mediator = mediator;
    }

    [HttpPost("bot/[controller]/create")]
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

    [HttpGet("bot/[controller]/{GuildId}/{MessageId}")]
    [BotMasterAuthorize]
    public async Task<IActionResult> Details([FromRoute] ulong guildId, [FromRoute] ulong messageId, [FromQuery] string? name) =>
        await _mediator.Send(new Details.Query
            {
                GuildId = guildId,
                MessageId = messageId,
                Name = name
            }) switch
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

    [HttpGet("bot/[controller]/leaderboard/{GuildId}/popular")]
    [BotMasterAuthorize]
    public async Task<IActionResult> Popular([FromRoute] ulong guildId, [FromQuery] string? name, [FromQuery] int? limit) =>
        await _mediator.Send(new Popular.Query
            {
                GuildId = guildId,
                Name = name,
                Limit = limit ?? DefaultLimit
            }) switch
            {
                { Status: QueryStatus.Success } result => Ok(result.Value),
                { Status: QueryStatus.NotFound } => NotFound(),
                _ => throw new InvalidOperationException()
            };

    [HttpGet("bot/[controller]/leaderboard/{GuildId}/posts")]
    [BotMasterAuthorize]
    public async Task<IActionResult> Posts([FromRoute] ulong guildId, [FromQuery] string? name, [FromQuery] int? limit) =>
        await _mediator.Send(new Posts.Query
            {
                GuildId = guildId,
                Name = name,
                Limit = limit ?? DefaultLimit
            }) switch
            {
                { Status: QueryStatus.Success } result => Ok(result.Value),
                { Status: QueryStatus.NotFound } => NotFound(),
                _ => throw new InvalidOperationException()
            };

    [HttpGet("bot/[controller]/leaderboard/{GuildId}/reactions")]
    [BotMasterAuthorize]
    public async Task<IActionResult> Reactions([FromRoute] ulong guildId, [FromQuery] string? name, [FromQuery] int? limit) =>
        await _mediator.Send(new Reactions.Query
            {
                GuildId = guildId,
                Name = name,
                Limit = limit ?? DefaultLimit
            }) switch
            {
                { Status: QueryStatus.Success } result => Ok(result.Value),
                { Status: QueryStatus.NotFound } => NotFound(),
                _ => throw new InvalidOperationException()
            };
}
