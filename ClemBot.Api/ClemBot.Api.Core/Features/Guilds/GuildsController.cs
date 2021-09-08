using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using ClemBot.Api.Core.Features.Guilds;
using ClemBot.Api.Core.Security;
using ClemBot.Api.Core.Security.Policies;
using ClemBot.Api.Core.Security.Policies.BotMaster;
using ClemBot.Api.Core.Security.Policies.GuildSandbox;
using ClemBot.Api.Core.Utilities;
using ClemBot.Api.Data.Enums;
using MediatR;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;

namespace ClemBot.Api.Core.Features.Guilds
{
    [ApiController]
    [Route("api")]
    public class GuildsController : ControllerBase
    {
        private readonly ILogger<GuildsController> _logger;

        private readonly IMediator _mediator;

        public GuildsController(ILogger<GuildsController> logger, IMediator mediator)
        {
            _logger = logger;
            _mediator = mediator;
        }

        [HttpGet("bot/[controller]")]
        [BotMasterAuthorize]
        public async Task<IActionResult> Index() =>
            await _mediator.Send(new Bot.Index.Query()) switch
            {
                { Status: QueryStatus.Success } result => Ok(result.Value),
                _ => Ok(new List<ulong>())
            };

        [HttpGet("bot/[controller]/{id}")]
        [BotMasterAuthorize]
        public async Task<IActionResult> Details([FromRoute] Bot.Details.Query query) =>
            await _mediator.Send(query) switch
            {
                { Status: QueryStatus.Success } result => Ok(result.Value),
                _ => NoContent()
            };

        [HttpDelete("bot/[controller]/{Id}")]
        [BotMasterAuthorize]
        public async Task<IActionResult> Delete([FromRoute] Bot.Delete.Query query) =>
            await _mediator.Send(query) switch
            {
                { Status: QueryStatus.Success } result => Ok(result.Value),
                { Status: QueryStatus.NotFound } => NoContent(),
                _ => throw new InvalidOperationException()
            };

        [HttpPost("bot/[controller]")]
        [BotMasterAuthorize]
        public async Task<IActionResult> Create(Bot.Create.Command command) =>
            await _mediator.Send(command) switch
            {
                { Status: QueryStatus.Success } result => Ok(result.Value),
                { Status: QueryStatus.Conflict } => Conflict(),
                _ => throw new InvalidOperationException()
            };

        [HttpPost("bot/[controller]/AddUser")]
        [BotMasterAuthorize]
        public async Task<IActionResult> AddUser(Bot.AddUser.Command command) =>
            await _mediator.Send(command) switch
            {
                { Status: QueryStatus.Success } result => Ok(result.Value),
                { Status: QueryStatus.Conflict } => Conflict(),
                _ => throw new InvalidOperationException()
            };

        [HttpDelete("bot/[controller]/RemoveUser")]
        [BotMasterAuthorize]
        public async Task<IActionResult> RemoveUser(Bot.RemoveUser.Command command) =>
            await _mediator.Send(command) switch
            {
                { Status: QueryStatus.Success } result => Ok(result.Value),
                { Status: QueryStatus.NotFound } => NotFound(),
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

        [HttpPatch("bot/[controller]/Update/Users")]
        [Authorize(Policy = Policies.BotMaster)]
        public async Task<IActionResult> UpdateUsers(Bot.UpdateUsers.Command command) =>
            await _mediator.Send(command) switch
            {
                { Status: QueryStatus.Success } result => Ok(result.Value),
                { Status: QueryStatus.NotFound } => NotFound(),
                _ => throw new InvalidOperationException()
            };

        [HttpPatch("bot/[controller]/Update/Roles")]
        [BotMasterAuthorize]
        public async Task<IActionResult> UpdateRoles(Bot.UpdateRoles.Command command) =>
            await _mediator.Send(command) switch
            {
                { Status: QueryStatus.Success } result => Ok(result.Value),
                { Status: QueryStatus.NotFound } => NotFound(),
                _ => throw new InvalidOperationException()
            };

        [HttpPatch("bot/[controller]/Update/Channels")]
        [BotMasterAuthorize]
        public async Task<IActionResult> UpdateChannels(Bot.UpdateChannels.Command command) =>
            await _mediator.Send(command) switch
            {
                { Status: QueryStatus.Success } result => Ok(result.Value),
                { Status: QueryStatus.NotFound } => NotFound(),
                _ => throw new InvalidOperationException()
            };

        [HttpPatch("bot/[controller]/Update/Threads")]
        [BotMasterAuthorize]
        public async Task<IActionResult> UpdateThreads(Bot.UpdateThreads.Command command) =>
            await _mediator.Send(command) switch
            {
                { Status: QueryStatus.Success } result => Ok(result.Value),
                { Status: QueryStatus.NotFound } => NotFound(),
                _ => throw new InvalidOperationException()
            };

        [HttpPatch("bot/[controller]/Update/RoleUserMappings")]
        [BotMasterAuthorize]
        public async Task<IActionResult> UpdateChannels(Bot.UpdateRolesUserMappings.Command command) =>
            await _mediator.Send(command) switch
            {
                { Status: QueryStatus.Success } result => Ok(result.Value),
                { Status: QueryStatus.NotFound } => NotFound(),
                _ => throw new InvalidOperationException()
            };

        [HttpGet("bot/[controller]/{Id}/Roles")]
        [BotMasterAuthorize]
        public async Task<IActionResult> Roles([FromRoute] Bot.Roles.Query query) =>
            await _mediator.Send(query) switch
            {
                { Status: QueryStatus.Success } result => Ok(result.Value),
                { Status: QueryStatus.NotFound } => NoContent(),
                _ => throw new InvalidOperationException()
            };

        [HttpGet("bot/[controller]/{Id}/Tags")]
        [BotMasterAuthorize]
        public async Task<IActionResult> Tags([FromRoute] Bot.Tags.Query query) =>
            await _mediator.Send(query) switch
            {
                { Status: QueryStatus.Success } result => Ok(result.Value),
                { Status: QueryStatus.NotFound } => NoContent(),
                _ => throw new InvalidOperationException()
            };

        [HttpGet("bot/[controller]/{Id}/CustomPrefixes")]
        [BotMasterAuthorize]
        public async Task<IActionResult> CustomPrefixes([FromRoute] Bot.CustomPrefixes.Query query) =>
            await _mediator.Send(query) switch
            {
                { Status: QueryStatus.Success } result => Ok(result.Value),
                { Status: QueryStatus.NotFound } => NoContent(),
                _ => throw new InvalidOperationException()
            };

        [HttpGet("bot/[controller]/{Id}/Channels")]
        [BotMasterAuthorize]
        public async Task<IActionResult> CustomPrefixes([FromRoute] Bot.Channels.Query query) =>
            await _mediator.Send(query) switch
            {
                { Status: QueryStatus.Success } result => Ok(result.Value),
                { Status: QueryStatus.NotFound } => NoContent(),
                _ => throw new InvalidOperationException()
            };

        [HttpGet("bot/[controller]/{Id}/Threads")]
        [BotMasterAuthorize]
        public async Task<IActionResult> CustomPrefixes([FromRoute] Bot.Threads.Query query) =>
            await _mediator.Send(query) switch
            {
                { Status: QueryStatus.Success } result => Ok(result.Value),
                { Status: QueryStatus.NotFound } => NoContent(),
                _ => throw new InvalidOperationException()
            };

        [HttpGet("bot/[controller]/{Id}/DesignatedChannels")]
        [BotMasterAuthorize]
        public async Task<IActionResult> Index([FromRoute] Bot.DesignatedChannels.Query command) =>
            await _mediator.Send(command) switch
            {
                { Status: QueryStatus.Success } result => Ok(result.Value),
                { Status: QueryStatus.NotFound } => NoContent(),
                _ => throw new InvalidOperationException()
            };

        [HttpGet("bot/[controller]/{Id}/Infractions")]
        [BotMasterAuthorize]
        public async Task<IActionResult> Infractions([FromRoute] Bot.Infractions.Query command) =>
            await _mediator.Send(command) switch
            {
                { Status: QueryStatus.Success } result => Ok(result.Value),
                { Status: QueryStatus.NotFound } => NoContent(),
                _ => throw new InvalidOperationException()
            };

        [HttpPost("bot/[controller]/{Id}/SetWelcomeMessage")]
        [BotMasterAuthorize]
        public async Task<IActionResult> SetWelcomeMessage(ulong Id, [FromBody] Bot.SetWelcomeMessage.Command command) =>
            await _mediator.Send(command with { Id = Id }) switch
            {
                { Status: QueryStatus.Success } result => Ok(result.Value),
                { Status: QueryStatus.NotFound } => NoContent(),
                _ => throw new InvalidOperationException()
            };

        [HttpGet("bot/[controller]/{Id}/GetWelcomeMessage")]
        [BotMasterAuthorize]
        public async Task<IActionResult> GetWelcomeMessage([FromRoute] Bot.GetWelcomeMessage.Command command) =>
            await _mediator.Send(command) switch
            {
                { Status: QueryStatus.Success } result => Ok(result.Value),
                { Status: QueryStatus.NotFound } => NotFound(),
                _ => throw new InvalidOperationException()
            };

        [HttpGet("bot/[controller]/{Id}/DeleteWelcomeMessage")]
        [BotMasterAuthorize]
        public async Task<IActionResult> DeleteWelcomeMessage(ulong Id, Bot.DeleteWelcomeMessage.Command command) =>
            await _mediator.Send(command with { Id = Id }) switch
            {
                { Status: QueryStatus.Success } result => Ok(result.Value),
                { Status: QueryStatus.NotFound } => NotFound(),
                _ => throw new InvalidOperationException()
            };
    }
}
