using ClemBot.Api.Common.Security.Policies.BotMaster;
using Microsoft.AspNetCore.Mvc;

namespace ClemBot.Api.Core.Features.CustomPrefixes;

[ApiController]
[Route("api")]
public class CustomPrefixesController : ControllerBase
{
    private readonly IMediator _mediator;

    public CustomPrefixesController(IMediator mediator)
    {
        _mediator = mediator;
    }

    [HttpPost("[controller]/Add")]
    [GuildSandboxAuthorize(BotAuthClaims.custom_prefix_set)]
    public async Task<IActionResult> Add(Set.Command command) =>
        await _mediator.Send(command) switch
        {
            { Status: QueryStatus.Success } result => Ok(result.Value),
            { Status: QueryStatus.Forbidden } => Forbid(),
            _ => throw new InvalidOperationException()
        };

    [HttpDelete("bot/[controller]/Delete")]
    [BotMasterAuthorize]
    public async Task<IActionResult> Delete(Bot.Delete.Command command) =>
        await _mediator.Send(command) switch
        {
            { Status: QueryStatus.Success } result => Ok(result.Value),
            _ => throw new InvalidOperationException()
        };

}
