using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using ClemBot.Api.Core.Utilities;
using MediatR;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace ClemBot.Api.Core.Features.Authorization
{
    [ApiController]
    [Route("api")]
    [AllowAnonymous]
    public class AuthorizeController : ControllerBase
    {
        private readonly IMediator _mediator;

        public AuthorizeController(IMediator mediator)
        {
            _mediator = mediator;
        }

        [HttpGet("bot/[controller]")]
        public async Task<IActionResult> Authorize([FromQuery] BotAuthorize.Query query) =>
            await _mediator.Send(query) switch
            {
                { Status: AuthorizeStatus.Success } result => Ok(result.Value),
                { Status: AuthorizeStatus.Forbidden } => Forbid(),
                _ => throw new InvalidOperationException()
            };
    }
}
