using System;
using System.Threading.Tasks;
using ClemBot.Api.Core.Features.Commands.Bot;
using ClemBot.Api.Core.Features.Public;
using ClemBot.Api.Core.Security.Policies.BotMaster;
using ClemBot.Api.Core.Utilities;
using MediatR;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace ClemBot.Api.Core.Features.Commands
{
    [ApiController]
    [Route("api")]
    public class CommandsController : ControllerBase
    {
        private readonly IMediator _mediator;

        public CommandsController(IMediator mediator)
        {
            _mediator = mediator;
        }

        [HttpPost("bot/[controller]")]
        [BotMasterAuthorize]
        public async Task<IActionResult> AddInvocation(AddInvocation.Command command) =>
            await _mediator.Send(command) switch
            {
                { Status: QueryStatus.Success } result => Ok(result.Value),
                _ => throw new InvalidOperationException()
            };
    }
}
