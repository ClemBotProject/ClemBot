using System;
using System.Threading.Tasks;
using ClemBot.Api.Common.Security.Policies.BotMaster;
using ClemBot.Api.Common.Security.Policies.GuildSandbox;
using ClemBot.Api.Common.Utilities;
using ClemBot.Api.Core.Features.Tags;
using MediatR;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace ClemBot.Api.Core.Features.Tags;

[ApiController]
[Route("api")]
public class TagsController : ControllerBase
{
    private readonly IMediator _mediator;

    public TagsController(IMediator mediator)
    {
        _mediator = mediator;
    }

    [HttpPost("[controller]")]
    [GuildSandboxAuthorize(BotAuthClaims.tag_add)]
    public async Task<IActionResult> Create(Create.Command command) =>
        await _mediator.Send(command) switch
        {
            { Status: QueryStatus.Success } result => Ok(result.Value),
            { Status: QueryStatus.Conflict } => Conflict(),
            { Status: QueryStatus.Forbidden } => Forbid(),
            _ => throw new InvalidOperationException()
        };

    [HttpPatch("bot/[controller]")]
    [BotMasterAuthorize]
    public async Task<IActionResult> Edit(Edit.Command command) =>
        await _mediator.Send(command) switch
        {
            { Status: QueryStatus.Success } result => Ok(result.Value),
            _ => NotFound()
        };

    [HttpGet("bot/[controller]")]
    [BotMasterAuthorize]
    public async Task<IActionResult> Details(Details.Query query) =>
        await _mediator.Send(query) switch
        {
            { Status: QueryStatus.Success } result => Ok(result.Value),
            _ => NoContent()
        };

    [HttpDelete("bot/[controller]")]
    [BotMasterAuthorize]
    public async Task<IActionResult> Delete(Delete.Command command) =>
        await _mediator.Send(command) switch
        {
            { Status: QueryStatus.Success } result => Ok(result.Value),
            { Status: QueryStatus.NotFound } => NoContent(),
            _ => throw new InvalidOperationException()
        };

    [HttpPost("bot/[controller]/invoke")]
    [BotMasterAuthorize]
    public async Task<IActionResult> AddUse(Bot.Invoke.Command command) =>
        await _mediator.Send(command) switch
        {
            { Status: QueryStatus.Success } result => Ok(result.Value),
            { Status: QueryStatus.Conflict } => Conflict(),
            _ => throw new InvalidOperationException()
        };

    [HttpPost("[controller]/AddCustomTagPrefix")]
    [GuildSandboxAuthorize(BotAuthClaims.custom_tag_prefix_set)]
    public async Task<IActionResult> AddCustomTagPrefix(SetCustomTagPrefix.Command command) =>
        await _mediator.Send(command) switch
        {
            { Status: QueryStatus.Success } result => Ok(result.Value),
            { Status: QueryStatus.Forbidden } => Forbid(),
            _ => throw new InvalidOperationException()
        };

    [HttpDelete("bot/[controller]/DeleteCustomTagPrefix")]
    [BotMasterAuthorize]
    public async Task<IActionResult> DeleteCustomTagPrefix(Bot.DeleteCustomTagPrefix.Command command) =>
        await _mediator.Send(command) switch
        {
            { Status: QueryStatus.Success } result => Ok(result.Value),
            _ => throw new InvalidOperationException()
        };
}
