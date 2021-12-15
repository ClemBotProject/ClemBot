using ClemBot.Api.Common;
using ClemBot.Api.Common.Utilities;
using ClemBot.Api.Core.Features.Authorization;
using ClemBot.Api.Data.Contexts;
using FluentValidation;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Core.Features.Guilds;

public class GetWelcomeMessage
{
    public class Validator : AbstractValidator<Command>
    {
        public Validator()
        {
            RuleFor(p => p.Id).NotNull();
        }
    }

    public record Command : IRequest<IQueryResult<IResponseModel>>
    {
        public ulong Id { get; set; }
    }

    public record Model : IResponseModel
    {
       public string? Message { get; init; }
    }

    public record Handler(ClemBotContext _context) : IRequestHandler<Command, IQueryResult<IResponseModel>>
    {
        public async Task<IQueryResult<IResponseModel>> Handle(Command request, CancellationToken cancellationToken)
        {
            var guild = await _context.Guilds
                .Select(x => new{ x.Id, x.WelcomeMessage })
                .FirstOrDefaultAsync(x => x.Id == request.Id);

            if (guild is null)
            {
                return QueryResult<IResponseModel>.NotFound();
            }

            return QueryResult<IResponseModel>.Success(new Model{ Message = guild.WelcomeMessage });
        }
    }
}
