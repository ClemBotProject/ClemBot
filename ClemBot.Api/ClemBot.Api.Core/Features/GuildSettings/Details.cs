using ClemBot.Api.Common;
using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Services.GuildSettings;

namespace ClemBot.Api.Core.Features.GuildSettings;

public class Details
{
    public class Query : IGuildSandboxModel, IRequest<QueryResult<Model>>
    {
        public ulong GuildId { get; init; }

        public ConfigSettings Setting { get; init; }
    }

    public class Model : IResponseModel
    {
        public ConfigSettings Setting { get; init; }

        public object? Value { get; init; }
    }

    public class QueryHandler : IRequestHandler<Query, QueryResult<Model>>
    {
        private readonly IGuildSettingsService _settingsService;

        public QueryHandler(IGuildSettingsService settingsService)
        {
            _settingsService = settingsService;
        }

        public async Task<QueryResult<Model>> Handle(Query request, CancellationToken cancellationToken)
        {
            var setting = await _settingsService.GetPropertyAsync(request.Setting, request.GuildId);

            return QueryResult<Model>.Success(
                new Model
                {
                    Setting = request.Setting,
                    Value = setting
                });
        }
    }
}
