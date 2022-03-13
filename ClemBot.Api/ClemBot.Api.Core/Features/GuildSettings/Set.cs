using ClemBot.Api.Common;
using ClemBot.Api.Common.Security.Policies.GuildSandbox;
using ClemBot.Api.Common.Utilities;
using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Data.Models;
using ClemBot.Api.Services.GuildSettings;
using FluentValidation;
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
        public ulong GuildId { get; init; }

        public ConfigSettings Setting { get; init; }

        public object? Value { get; init; }
    }

    public class Model : IResponseModel
    {
        public bool Status { get; set; }
    }

    public class Handler : IRequestHandler<Command, IQueryResult<Model>>
    {
        private readonly IGuildSettingsService _settingsService;

        public Handler(IGuildSettingsService settingsService)
        {
            _settingsService = settingsService;
        }

        public async Task<IQueryResult<Model>> Handle(Command request, CancellationToken cancellationToken)
        {
            var status = request.Setting switch
            {
                ConfigSettings.allow_embed_links => await _settingsService.SetCanEmbedLink(request.GuildId, (bool)request.Value!),
                _ => throw new ArgumentOutOfRangeException()
            };

            return QueryResult<Model>.Success(new Model{ Status = status });
        }
    }
}
