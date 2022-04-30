using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Common.Utilities;
using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Services.Caching.Channels.Models;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Core.Features.Channels.Bot;

public class Delete
{
    public class Query : IRequest<IQueryResult<Model>>
    {
        public ulong Id { get; set; }
    }

    public class Model
    {
        public ulong Id { get; init; }

        public string? Name { get; init; }
    }

    public class QueryHandler : IRequestHandler<Query, IQueryResult<Model>>
    {
        public ClemBotContext _context { get; init; }

        public IMediator _mediatr { get; init; }

        public QueryHandler(ClemBotContext context, IMediator mediatr)
        {
            _context = context;
            _mediatr = mediatr;
        }

        public async Task<IQueryResult<Model>> Handle(Query request, CancellationToken cancellationToken)
        {
            var channel = await _context.Channels
                .FirstOrDefaultAsync(g => g.Id == request.Id);

            if (channel is null)
            {
                return QueryResult<Model>.NotFound();
            }

            // Grab any child threads the channel contains and delete those as well
            // to preserve referential integrity
            var childThreads = await _context.Channels
                .Where(x => x.ParentId == channel.Id)
                .ToListAsync();

            _context.Channels.Remove(channel);
            _context.Channels.RemoveRange(childThreads);

            await _context.SaveChangesAsync();

            // Clear the channel from the cache so we dont try to insert a new message batch into it
            await _mediatr.Send(new ClearChannelRequest {Id = request.Id});

            return QueryResult<Model>.Success(new Model()
            {
                Id = channel.Id,
                Name = channel.Name
            });
        }

        public void Deconstruct(out ClemBotContext _context, out IMediator _mediatr)
        {
            _context = this._context;
            _mediatr = this._mediatr;
        }
    }
}
