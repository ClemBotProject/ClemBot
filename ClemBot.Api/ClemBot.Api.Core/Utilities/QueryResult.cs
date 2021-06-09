namespace ClemBot.Api.Core.Utilities
{
    public static class QueryResult<T>
    {
        public static Result<T, QueryStatus> Success(T? val = default)
            => new(val, QueryStatus.Success);

        public static Result<T, QueryStatus> NotFound()
            => new(default, QueryStatus.NotFound);

        public static Result<T, QueryStatus> Conflict()
            => new(default, QueryStatus.Conflict);
    }
}
