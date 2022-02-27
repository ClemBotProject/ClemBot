using Microsoft.AspNetCore.Mvc;

namespace ClemBot.Api.Core.Features.HealthCheck;

[ApiController]
[Route("api")]
public class HealthCheckController : ControllerBase
{
    [HttpGet("[controller]/ping")]
    public IActionResult Ping() => Ok("pong!");
}
