using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using ClemBot.Api.Core.Features.Roles.Bot;
using ClemBot.Api.Core.Security;
using ClemBot.Api.Core.Security.Policies;
using ClemBot.Api.Core.Security.Policies.BotMaster;
using ClemBot.Api.Core.Utilities;
using MediatR;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace ClemBot.Api.Core.Features.CustomPrefixes
{
    [ApiController]
    [Route("api")]
    public class CustomPrefixesController : ControllerBase
    {
        private readonly IMediator _mediator;

        public CustomPrefixesController(IMediator mediator)
        {
            _mediator = mediator;
        }

        [HttpPost("bot/[controller]/Add")]
        [BotMasterAuthorize]
        public async Task<IActionResult> Add(Bot.Add.Command command) =>
            await _mediator.Send(command) switch
            {
                { Status: QueryStatus.Success } result => Ok(result.Value),
                _ => throw new InvalidOperationException()
            };

        [HttpDelete("bot/[controller]/Delete")]
        [BotMasterAuthorize]
        public async Task<IActionResult> Add(Bot.Delete.Command command) =>
            await _mediator.Send(command) switch
            {
                { Status: QueryStatus.Success } result => Ok(result.Value),
                _ => throw new InvalidOperationException()
            };

    }
}
