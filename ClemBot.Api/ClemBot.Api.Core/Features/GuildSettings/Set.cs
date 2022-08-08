using ClemBot.Api.Common;
using ClemBot.Api.Common.Security.Policies.GuildSandbox;
using ClemBot.Api.Common.Utilities;
using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Data.Models;
using ClemBot.Api.Services.GuildSettings;
using FluentValidation;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace ClemBot.Api.Core.Features.GuildSettings;

public class Set
{
    public class Validator : AbstractValidator<Command>
    {
        public Validator()
        {
            RuleFor(p => p.GuildId).NotNull();
            RuleFor(p => p.Setting).NotNull();
        }
    }

    public record Command : IGuildSandboxModel, IRequest<IQueryResult<Model>>
    {
        [FromRoute]
        public ulong GuildId { get; init; }

        [FromRoute]
        public ConfigSettings Setting { get; init; }

        [FromBody]
        public string? Value { get; init; }
    }

    public class Model : IResponseModel
    {
    }

    public class Handler : IRequestHandler<Command, IQueryResult<Model>>
    {
        private readonly IGuildSettingsService _settingsService;

        public Handler(IGuildSettingsService settingsService)
        {
            _settingsService = settingsService;
        }

        public async Task<IQueryResult<Model>> Handle(Command request, CancellationToken cancellationToken) =>
            await _settingsService.SetPropertyAsync(request.Setting, request.GuildId, request.Value) switch
            {
                true => QueryResult<Model>.Success(),
                false => QueryResult<Model>.Invalid()
            };
    }
}
