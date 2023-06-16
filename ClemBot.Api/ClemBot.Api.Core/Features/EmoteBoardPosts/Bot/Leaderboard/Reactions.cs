using ClemBot.Api.Common;
using FluentValidation;

namespace ClemBot.Api.Core.Features.EmoteBoardPosts.Bot.Leaderboard;

/// <summary>
/// This route returns a leaderboard categorized by the number of total reactions a user received.
/// </summary>
public class Reactions
{
    public class Validator : AbstractValidator<Query>
    {
        public Validator()
        {

        }
    }

    public class LeaderboardSlot : IResponseModel
    {
        public ulong UserId { get; init; }

        public int ReactionCount { get; init; }
    }

    public class Query : IRequest<QueryResult<List<LeaderboardSlot>>>
    {

    }
}
