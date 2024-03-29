﻿using ClemBot.Api.Common;
using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Data.Models;
using ClemBot.Api.Services.Caching.Guilds.Models;
using FluentValidation;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Core.Features.EmoteBoardPosts.Bot.Leaderboard;

/// <summary>
/// This route returns a leaderboard categorized by how many reactions a single post received.
/// </summary>
public class Popular
{
    public class Validator : AbstractValidator<Query>
    {
        public Validator()
        {
            RuleFor(q => q.GuildId).NotNull();
            RuleFor(q => q.Limit).NotNull().Must(l => l is > 0 and <= 50);
            RuleFor(q => q.Name).Must(s => s is null || !s.Any(char.IsWhiteSpace));
        }
    }

    public class LeaderboardSlot : IResponseModel
    {
        public ulong UserId { get; init; }

        public ulong ChannelId { get; init; }

        public ulong MessageId { get; init; }

        public int ReactionCount { get; init; }

        public required string Emote { get; init; }
    }

    public class Query : IRequest<QueryResult<List<LeaderboardSlot>>>
    {
        public ulong GuildId { get; init; }

        public string? Name { get; init; }

        public int Limit { get; init; }
    }

    public class Handler : IRequestHandler<Query, QueryResult<List<LeaderboardSlot>>>
    {

        private readonly IMediator _mediator;
        private readonly ClemBotContext _context;

        public Handler(IMediator mediator, ClemBotContext context)
        {
            _mediator = mediator;
            _context = context;
        }

        public async Task<QueryResult<List<LeaderboardSlot>>> Handle(Query request, CancellationToken cancellationToken)
        {
            var guildExists = await _mediator.Send(new GuildExistsRequest
            {
                Id = request.GuildId
            });

            if (!guildExists)
            {
                return QueryResult<List<LeaderboardSlot>>.NotFound();
            }

            EmoteBoard? board = null;

            if (request.Name is not null)
            {
                board = await _context.EmoteBoards
                    .FirstOrDefaultAsync(b => b.GuildId == request.GuildId && b.Name == request.Name);

                if (board is null)
                {
                    return QueryResult<List<LeaderboardSlot>>.NotFound();
                }
            }

            var posts = await _context.EmoteBoardPosts
                .Where(p => board != null ? p.EmoteBoardId == board.Id : p.EmoteBoard.GuildId == request.GuildId)
                .Include(p => p.Reactions)
                .OrderByDescending(p => p.Reactions.Count)
                .Take(request.Limit)
                .Select(p => new LeaderboardSlot
                {
                    UserId = p.UserId,
                    ChannelId = p.ChannelId,
                    MessageId = p.MessageId,
                    ReactionCount = p.Reactions.Count,
                    Emote = board != null ? board.Emote : p.EmoteBoard.Emote
                })
                .ToListAsync();

            return QueryResult<List<LeaderboardSlot>>.Success(posts);
        }
    }
}
