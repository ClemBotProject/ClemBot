using System;
using System.Threading.Tasks;
using ClemBot.Api.Core.Features.Messages;
using ClemBot.Api.Core.Security;
using ClemBot.Api.Core.Security.Policies;
using ClemBot.Api.Core.Security.Policies.BotMaster;
using ClemBot.Api.Core.Utilities;
using MediatR;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace ClemBot.Api.Core.Features.Messages
{
    [ApiController]
    [Route("api")]
    public class MessagesController : ControllerBase
    {
        private readonly IMediator _mediator;

        public MessagesController(IMediator mediator)
        {
            _mediator = mediator;
        }

        [HttpPost("bot/[controller]")]
        [BotMasterAuthorize]
        public async Task<IActionResult> Create(Bot.Create.Command command) =>
            await _mediator.Send(command) switch
            {
                { Status: QueryStatus.Success } result => Ok(result.Value),
                { Status: QueryStatus.Conflict } => Conflict(),
                _ => throw new InvalidOperationException()
            };

        [HttpPatch("bot/[controller]")]
        [BotMasterAuthorize]
        public async Task<IActionResult> Edit(Bot.Edit.Command command) =>
            await _mediator.Send(command) switch
            {
                { Status: QueryStatus.Success } result => Ok(result.Value),
                _ => NotFound()
            };

        [HttpGet("bot/[controller]/{Id}")]
        [BotMasterAuthorize]
        public async Task<IActionResult> Details([FromRoute] Bot.Details.Query query) =>
            await _mediator.Send(query) switch
            {
                { Status: QueryStatus.Success } result => Ok(result.Value),
                _ => NoContent()
            };
    }
}
