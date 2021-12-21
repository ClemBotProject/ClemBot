using ClemBot.Api.Common;
using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Services.GuildSettings;

namespace ClemBot.Api.Core.Features.GuildSettings;

public class Details
{
    public class Query : IGuildSandboxModel, IRequest<IQueryResult<Model>>
    {
        public ulong GuildId { get; init; }

        public ConfigSettings Setting { get; init; }
    }

    public class Model : IResponseModel
    {
        public ConfigSettings Setting { get; init; }

        public object? Value { get; init; }
    }

    public class QueryHandler : IRequestHandler<Query, IQueryResult<Model>>
    {
        private readonly IGuildSettingsService _settingsService;

        public QueryHandler(IGuildSettingsService settingsService)
        {
            _settingsService = settingsService;
        }

        public async Task<IQueryResult<Model>> Handle(Query request, CancellationToken cancellationToken)
        {
            var setting = request.Setting switch
            {
                ConfigSettings.allow_embed_links => await _settingsService.GetCanEmbedLink(request.GuildId),
                _ => throw new ArgumentOutOfRangeException()
            };

            return QueryResult<Model>.Success(
                new Model
                {
                    Setting = request.Setting,
                    Value = setting
                });
        }
    }
}
