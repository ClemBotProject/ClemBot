using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace ClemBot.Api.Core.Features.GuildSettings;

[ApiController]
[Route("api")]
public class GuildSettingsController : ControllerBase
{
    private readonly ILogger<GuildSettingsController> _logger;

    private readonly IMediator _mediator;

    public GuildSettingsController(ILogger<GuildSettingsController> logger, IMediator mediator)
    {
        _logger = logger;
        _mediator = mediator;
    }

    [HttpGet("[controller]/{GuildId}")]
    [GuildSandboxAuthorize(BotAuthClaims.guild_settings_view)]
    public async Task<IActionResult> Index() =>
        await _mediator.Send(new Index.Query()) switch
        {
            { Status: QueryStatus.Success } result => Ok(result.Value),
            { Status: QueryStatus.Forbidden } => Forbid(),
            _ => Ok(new List<ulong>())
        };
    [HttpGet("[controller]/{GuildId}/{Setting}")]
    [GuildSandboxAuthorize(BotAuthClaims.guild_settings_view)]
    public async Task<IActionResult> Details([FromRoute] Details.Query command) =>
        await _mediator.Send(command) switch
        {
            { Status: QueryStatus.Success } result => Ok(result.Value),
            { Status: QueryStatus.Forbidden } => Forbid(),
            _ => throw new InvalidOperationException()
        };

    [HttpPost("[controller]/{GuildId}/{Setting}")]
    [GuildSandboxAuthorize(BotAuthClaims.guild_settings_edit)]
    public async Task<IActionResult> Set([FromRoute] Set.Command command, [FromQuery] bool value) =>
        await _mediator.Send(command with { Value = value }) switch
        {
            { Status: QueryStatus.Success } result => Ok(result.Value),
            { Status: QueryStatus.Forbidden } => Forbid(),
            _ => throw new InvalidOperationException()
        };
}
