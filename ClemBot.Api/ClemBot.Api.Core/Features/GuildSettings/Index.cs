using ClemBot.Api.Common;
using ClemBot.Api.Services.GuildSettings;

namespace ClemBot.Api.Core.Features.GuildSettings;

public class Index
{
    public class Query : IGuildSandboxModel, IRequest<IQueryResult<Model>>
    {
        public ulong GuildId { get; init; }

        public ConfigSettings Setting { get; init; }
    }

    public class Config
    {
        public ConfigSettings Setting { get; init; }

        public object? Value { get; init; }
    }

    public class Model : IResponseModel
    {
        public Dictionary<ConfigSettings, object> Settings { get; init; } = null!;
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
            var settings = await _settingsService.GetAllSettingsAsync(request.GuildId);

            return QueryResult<Model>.Success(new Model{Settings = settings});
        }
    }
}
