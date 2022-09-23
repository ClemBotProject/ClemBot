namespace ClemBot.Api.Common.Utilities;

public class QueryResult<T> : IResult<T, QueryStatus>
{
    public T? Value { get; }
    public QueryStatus Status { get; }

    public QueryResult(QueryStatus status)
    {
        Status = status;
    }

    private QueryResult(T? val, QueryStatus status)
    {
        Value = val;
        Status = status;
    }

    public static QueryResult<T> Success(T? val = default)
        => new(val, QueryStatus.Success);

    public static QueryResult<T> Invalid(T? val = default)
        => new(val, QueryStatus.Invalid);

    public static QueryResult<T> NotFound()
        => new(default, QueryStatus.NotFound);

    public static QueryResult<T> Conflict()
        => new(default, QueryStatus.Conflict);

    public static QueryResult<T> Forbidden()
        => new(default, QueryStatus.Forbidden);

    public static QueryResult<T> NoContent()
        => new(default, QueryStatus.NoContent);
}
