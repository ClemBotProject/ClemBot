using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Common.Utilities;
using ClemBot.Api.Data.Contexts;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Core.Features.Roles.Bot;

public class Details
{
    public class Query : IRequest<IQueryResult<Model>>
    {
        public ulong Id { get; init; }
    }

    public class Model
    {
        public ulong Id { get; init; }

        public string? Name { get; init; }

        public ulong GuildId { get; init; }

        public bool Admin { get; init; }

        public bool IsAssignable { get; init; }
    }

    public record QueryHandler(ClemBotContext _context) : IRequestHandler<Query, IQueryResult<Model>>
    {
        public async Task<IQueryResult<Model>> Handle(Query request, CancellationToken cancellationToken)
        {
            var role = await _context.Roles
                .Where(x => x.Id == request.Id)
                .FirstAsync();

            if (role is null)
            {
                return QueryResult<Model>.NotFound();
            }

            return QueryResult<Model>.Success(new Model()
            {
                Id = role.Id,
                Name = role.Name,
                GuildId = role.GuildId,
                IsAssignable = role.IsAssignable ?? false,
                Admin = role.Admin
            });
        }
    }
}
