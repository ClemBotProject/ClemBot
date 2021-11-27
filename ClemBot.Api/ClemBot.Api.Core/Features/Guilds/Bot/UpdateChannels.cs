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

public class UpdateChannels
{
    public class ChannelDto
    {
        public ulong ChannelId { get; set; }

        public string? Name { get; set; }
    }

    public record Command : IRequest<IQueryResult<ulong>>
    {
        public ulong GuildId { get; init; }

        public string ChannelCsv { get; set; } = null!;
    }

    public record Handler(ClemBotContext _context)
        : IRequestHandler<Command, IQueryResult<ulong>>
    {
        public async Task<IQueryResult<ulong>> Handle(Command request, CancellationToken cancellationToken)
        {
            using var csvReader = new CsvReader(new StringReader(request.ChannelCsv), CultureInfo.InvariantCulture);
            var channels = csvReader.GetRecords<ChannelDto>().ToList();

            var guildEntities = await _context.Guilds
                .Include(y => y.Channels)
                .ToListAsync();

            var guildEntity = guildEntities.FirstOrDefault(x => x.Id == request.GuildId);

            if (guildEntity is null)
            {
                return QueryResult<ulong>.NotFound();
            }

            var channelsEntity = guildEntity.Channels
                .Where(x => !x.IsThread)
                .ToList();

            // Get all channels that are common to both enumerables and check for a name change
            foreach (var channelId in channelsEntity
                         .Select(x => x.Id)
                         .Intersect(channels
                             .Select(x => x.ChannelId)))
            {
                var role = channelsEntity.First(x => x.Id == channelId);
                role.Name = channels.First(x => x.ChannelId == channelId).Name;
            }

            // Get all channels that have been deleted
            foreach (var channel in channelsEntity
                         .Where(x =>
                             channels.All(y => y.ChannelId != x.Id))
                         .ToList())
            {
                _context.Channels.Remove(channel);
            }

            // get new channels
            foreach (var channel in channels
                         .Where(x =>
                             channelsEntity.All(y => y.Id != x.ChannelId))
                         .ToList())
            {
                var channelEntity = new Channel
                {
                    Id = channel.ChannelId,
                    Name = channel.Name,
                    GuildId = request.GuildId
                };
                _context.Channels.Add(channelEntity);
                guildEntity?.Channels?.Add(channelEntity);
            }


            await _context.SaveChangesAsync();

            return QueryResult<ulong>.Success(request.GuildId);
        }
    }
}
