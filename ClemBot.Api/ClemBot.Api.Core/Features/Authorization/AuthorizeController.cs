using System.Net;
using ClemBot.Api.Common.Utilities;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace ClemBot.Api.Core.Features.Authorization;

[ApiController]
[Route("api")]
public class AuthorizeController : ControllerBase
{
    private readonly IMediator _mediator;

    public AuthorizeController(IMediator mediator)
    {
        _mediator = mediator;
    }

    [AllowAnonymous]
    [HttpGet("bot/[controller]")]
    public async Task<IActionResult> Authorize([FromQuery] BotAuthorize.Query query) =>
        await _mediator.Send(query) switch
        {
            {Status: AuthorizeStatus.Success} result => Ok(result.Value),
            {Status: AuthorizeStatus.Forbidden} => Forbid(),
            _ => throw new InvalidOperationException()
        };

    [AllowAnonymous]
    [HttpPost("[controller]/login")]
    public async Task<IActionResult> Login([FromBody] SiteLogin.Query query) =>
        await _mediator.Send(query) switch
        {
            {Status: AuthorizeStatus.Success} result => Ok(result.Value),
            {Status: AuthorizeStatus.Forbidden} => Forbid(),
            _ => throw new InvalidOperationException()
        };

    [HttpGet("[controller]/User")]
    public async Task<IActionResult> GetUser() =>
        await _mediator.Send(new GetSiteUser.Query()) switch
        {
            {Status: AuthorizeStatus.Success} result => Ok(result.Value),
            {Status: AuthorizeStatus.Forbidden} => Forbid(),
            {Status: AuthorizeStatus.Failure} => Problem(),
            _ => throw new InvalidOperationException()
        };
}
