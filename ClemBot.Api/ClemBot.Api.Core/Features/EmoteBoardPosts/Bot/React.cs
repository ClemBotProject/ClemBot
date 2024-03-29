﻿using ClemBot.Api.Common;
using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Data.Models;
using ClemBot.Api.Services.Caching.EmoteBoardPosts.Models;
using ClemBot.Api.Services.Caching.Guilds.Models;
using FluentValidation;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Core.Features.EmoteBoardPosts.Bot;

public class React
{
    public class Validator : AbstractValidator<Command>
    {
        public Validator()
        {
            RuleFor(c => c.GuildId).NotNull();
            RuleFor(c => c.Name).NotNull().NotEmpty().Must(s => !s.Any(char.IsWhiteSpace));
            RuleFor(c => c.MessageId).NotNull();
            RuleFor(c => c.UserReactions).NotNull().NotEmpty();
        }
    }

    public class EmoteBoardReactionDto : IResponseModel
    {
        public bool Update { get; init; }

        public int? ReactionCount { get; init; }
    }

    public class Command : IRequest<QueryResult<EmoteBoardReactionDto>>
    {
        public ulong GuildId { get; set; }

        public required string Name { get; set; }

        public ulong MessageId { get; set; }

        public required List<ulong> UserReactions { get; set; }
    }

    public class Handler : IRequestHandler<Command, QueryResult<EmoteBoardReactionDto>>
    {

        private readonly IMediator _mediator;
        private readonly ClemBotContext _context;

        public Handler(IMediator mediator, ClemBotContext context)
        {
            _mediator = mediator;
            _context = context;
        }

        public async Task<QueryResult<EmoteBoardReactionDto>> Handle(Command request, CancellationToken cancellationToken)
        {
            var guildExists = await _mediator.Send(new GuildExistsRequest
            {
                Id = request.GuildId
            });

            if (!guildExists)
            {
                return QueryResult<EmoteBoardReactionDto>.NotFound();
            }

            var board = await _context.EmoteBoards
                .FirstOrDefaultAsync(b => b.GuildId == request.GuildId && b.Name == request.Name);

            if (board is null)
            {
                return QueryResult<EmoteBoardReactionDto>.NotFound();
            }

            var postExists = await _mediator.Send(new EmoteBoardPostExistsRequest
            {
                BoardId = board.Id,
                MessageId = request.MessageId
            });

            if (!postExists)
            {
                return QueryResult<EmoteBoardReactionDto>.NotFound();
            }

            var post = await _context.EmoteBoardPosts
                .FirstOrDefaultAsync(p => p.EmoteBoardId == board.Id && p.MessageId == request.MessageId);

            if (post is null)
            {
                return QueryResult<EmoteBoardReactionDto>.Conflict();
            }

            var currentReactions = await _context.EmoteBoardPostReactions
                .Where(rp => rp.EmoteBoardPostId == post.Id)
                .Select(rp => rp.UserId)
                .ToListAsync();

            var newReactions = request.UserReactions
                .Where(id => !currentReactions.Contains(id))
                .ToList();

            if (newReactions.Count == 0)
            {
                return QueryResult<EmoteBoardReactionDto>.Success(new EmoteBoardReactionDto
                {
                    Update = false
                });
            }

            post.Reactions.AddRange(newReactions.Select(id => new EmoteBoardPostReaction
                {
                    UserId = id
                })
            );

            await _context.SaveChangesAsync();

            return QueryResult<EmoteBoardReactionDto>.Success(new EmoteBoardReactionDto
            {
                Update = true,
                ReactionCount = currentReactions.Count + newReactions.Count
            });
        }
    }
}
