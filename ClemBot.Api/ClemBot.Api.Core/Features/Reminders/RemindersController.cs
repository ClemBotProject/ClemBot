using Microsoft.AspNetCore.Mvc;

namespace ClemBot.Api.Core.Features.Reminders;

[ApiController]
[Route("api")]
public class RemindersController : ControllerBase
{

    private readonly IMediator _mediator;

    public RemindersController(IMediator mediator)
    {
        _mediator = mediator;
    }

    [HttpPost("[controller]")]
    public async Task<IActionResult> Create(Create.Model model) =>
        await _mediator.Send(model) switch
        {
            { Status: QueryStatus.Success } result => Ok(result.Value),
            _ => throw new InvalidOperationException()
        };

}
