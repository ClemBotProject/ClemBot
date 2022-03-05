using ClemBot.Api.Common.Security.Policies.BotMaster;
using Microsoft.AspNetCore.Mvc;

namespace ClemBot.Api.Core.Features.HealthCheck;

[ApiController]
[Route("api")]
public class HealthCheckController : ControllerBase
{
    [HttpGet("[controller]/ping")]
    [BotMasterAuthorize]
    public IActionResult Ping() => Ok("pong!");
}
