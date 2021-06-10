using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using ClemBot.Api.Core.Security.Policies.GuildSandbox;
using ClemBot.Api.Core.Utilities;
using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Data.Models;
using FluentValidation;
using MediatR;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Core.Features.Guilds.Bot
{
    public class UpdateChannels
    {
        public class ChannelDto
        {
            public ulong ChannelId { get; set; }

            public string? Name { get; set; }
        }

        public record GuildDto
        {
            public ulong GuildId { get; init; }

            public IReadOnlyList<ChannelDto> Channels { get; set; } = new List<ChannelDto>();
        }


        public record Command : IRequest<Result<IEnumerable<ulong>, QueryStatus>>
        {
            public IReadOnlyList<GuildDto> Guilds { get; set; } = new List<GuildDto>();
        }

        public record Handler(ClemBotContext _context)
            : IRequestHandler<Command, Result<IEnumerable<ulong>, QueryStatus>>
        {
            public async Task<Result<IEnumerable<ulong>, QueryStatus>> Handle(Command request, CancellationToken cancellationToken)
            {
                var guildEntities = await _context.Guilds
                    .Include(y => y.Channels)
                    .ToListAsync();

                foreach (var requestGuild in request.Guilds)
                {
                    var guildEntity = guildEntities.FirstOrDefault(x => x.Id == requestGuild.GuildId);

                    if (guildEntity is null)
                    {
                        continue;
                    }

                    var channels = guildEntity.Channels ?? new List<Channel>();

                    // Get all roles that are common to both enumerables and check for a name change
                    foreach (var channelId in channels
                        .Select(x => x.Id)
                        .Intersect(requestGuild.Channels
                            .Select(x => x.ChannelId)))
                    {
                        var role = channels.First(x => x.Id == channelId);
                        role.Name = requestGuild.Channels.First(x => x.ChannelId == channelId).Name;
                    }

                    // Get all roles that have been deleted
                    foreach (var channel in channels
                        .Where(x =>
                            requestGuild.Channels.All(y => y.ChannelId != x.Id))
                        .ToList())
                    {
                        _context.Channels.Remove(channel);
                    }

                    // get new channels
                    foreach (var channel in requestGuild.Channels
                        .Where(x =>
                            channels.All(y => y.Id != x.ChannelId))
                        .ToList())
                    {
                        var channelEntity = new Channel
                        {
                            Id = channel.ChannelId,
                            Name = channel.Name,
                            GuildId = requestGuild.GuildId
                        };
                        _context.Channels.Add(channelEntity);
                        guildEntity?.Channels?.Add(channelEntity);
                    }
                }


                await _context.SaveChangesAsync();

                return QueryResult<IEnumerable<ulong>>.Success(request.Guilds.Select(x => x.GuildId));
            }
        }
    }
}
