namespace ClemBot.Api.Common.Utilities;

public class QueryResult<T> : IQueryResult<T>
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

    public static IQueryResult<T> Success(T? val)
        => new QueryResult<T>(val, QueryStatus.Success);

    public static IQueryResult<T> Invalid(T? val)
        => new QueryResult<T>(val, QueryStatus.Invalid);

    public static IQueryResult<T> NotFound()
        => new QueryResult<T>(default, QueryStatus.NotFound);

    public static IQueryResult<T> Conflict()
        => new QueryResult<T>(default, QueryStatus.Conflict);

    public static IQueryResult<T> Forbidden()
        => new QueryResult<T>(default, QueryStatus.Forbidden);
}
