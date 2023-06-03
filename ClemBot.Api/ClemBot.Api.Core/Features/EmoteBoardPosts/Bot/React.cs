using ClemBot.Api.Common;
using FluentValidation;

namespace ClemBot.Api.Core.Features.EmoteBoardPosts.Bot;

public class React
{
    public class Validator : AbstractValidator<Command>
    {

    }

    public class EmoteBoardReactionDto : IResponseModel
    {

    }

    public class Command : IRequest<EmoteBoardReactionDto>
    {
        public ulong GuildId { get; set; }

        public ulong ChannelId { get; set; }

        public ulong MessageId { get; set; }

        public required List<ulong> UserReactions { get; set; }
    }
}
