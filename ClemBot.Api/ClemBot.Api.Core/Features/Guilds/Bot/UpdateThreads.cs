using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Common.Utilities;
using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Data.Models;
using CsvHelper;
using FluentValidation;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Core.Features.Guilds.Bot;

public class UpdateThreads
{
    public class ThreadDto
    {
        public ulong ThreadId { get; set; }

        public string? Name { get; set; }

        public ulong ParentId { get; set; }
    }

    public record Command : IRequest<IQueryResult<ulong>>
    {
        public ulong GuildId { get; init; }

        public string ThreadCsv { get; set; } = null!;
    }

    public record Handler(ClemBotContext _context)
        : IRequestHandler<Command, IQueryResult<ulong>>
    {
        public async Task<IQueryResult<ulong>> Handle(Command request, CancellationToken cancellationToken)
        {
            using var csvReader = new CsvReader(new StringReader(request.ThreadCsv), CultureInfo.InvariantCulture);
            var threads = csvReader.GetRecords<ThreadDto>().ToList();

            var guildEntities = await _context.Guilds
                .Include(y => y.Channels)
                .ToListAsync();

            var guildEntity = guildEntities.FirstOrDefault(x => x.Id == request.GuildId);

            if (guildEntity is null)
            {
                return QueryResult<ulong>.NotFound();
            }

            var threadsEntity = guildEntity.Channels
                .Where(x => x.IsThread)
                .ToList();

            // Get all channels that are common to both enumerables and check for a name change
            foreach (var channelId in threadsEntity
                         .Select(x => x.Id)
                         .Intersect(threads
                             .Select(x => x.ThreadId)))
            {
                var role = threadsEntity.First(x => x.Id == channelId);
                role.Name = threads.First(x => x.ThreadId == channelId).Name;
            }

            // Get all channels that have been deleted
            foreach (var channel in threadsEntity
                         .Where(x =>
                             threads.All(y => y.ThreadId != x.Id))
                         .ToList())
            {
                _context.Channels.Remove(channel);
            }

            // get new channels
            foreach (var thread in threads
                         .Where(x =>
                             threadsEntity.All(y => y.Id != x.ThreadId))
                         .ToList())
            {
                var threadEntity = new Channel
                {
                    Id = thread.ThreadId,
                    Name = thread.Name,
                    GuildId = request.GuildId,
                    ParentId = thread.ParentId
                };
                _context.Channels.Add(threadEntity);
                guildEntity?.Channels?.Add(threadEntity);
            }


            await _context.SaveChangesAsync();

            return QueryResult<ulong>.Success(request.GuildId);
        }
    }
}
