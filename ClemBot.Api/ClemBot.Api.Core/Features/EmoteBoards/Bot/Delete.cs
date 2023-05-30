﻿using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Services.Caching.EmoteBoards.Models;
using ClemBot.Api.Services.Caching.Guilds.Models;
using FluentValidation;

namespace ClemBot.Api.Core.Features.EmoteBoards.Bot;

public class Delete
{

    public class Validator : AbstractValidator<Command>
    {
        public Validator()
        {
            RuleFor(c => c.GuildId).NotNull();
            RuleFor(c => c.Name).NotNull().Must(s => !s.Any(char.IsWhiteSpace));
        }
    }

    public class Command : IRequest<QueryResult<Unit>>
    {
        public ulong GuildId { get; set; }

        public string Name { get; set; } = null!;
    }

    public class Handler : IRequestHandler<Command, QueryResult<Unit>>
    {

        private readonly IMediator _mediator;
        private readonly ClemBotContext _context;

        public Handler(IMediator mediator, ClemBotContext context)
        {
            _mediator = mediator;
            _context = context;
        }

        public async Task<QueryResult<Unit>> Handle(Command request, CancellationToken cancellationToken)
        {
            var guildExists = await _mediator.Send(new GuildExistsRequest
            {
                Id = request.GuildId
            });

            if (!guildExists)
            {
                return QueryResult<Unit>.NotFound();
            }

            var boards = await _mediator.Send(new GetEmoteBoardsRequest
            {
                GuildId = request.GuildId
            });

            var board = boards.FirstOrDefault(b => string.Equals(b.Name, request.Name, StringComparison.OrdinalIgnoreCase));

            if (board is null)
            {
                return QueryResult<Unit>.NotFound();
            }

            _context.EmoteBoards.Remove(board);
            await _context.SaveChangesAsync();

            await _mediator.Send(new ClearEmoteBoardsRequest
            {
                GuildId = request.GuildId
            });

            return QueryResult<Unit>.NoContent();
        }
    }
}
