namespace ClemBot.Api.Common.Utilities;

public interface IQueryResult<T> : IResult<T, QueryStatus>
{
    static abstract IQueryResult<T> Success(T? val);
    static abstract IQueryResult<T> Invalid(T? val);
    static abstract IQueryResult<T> NotFound();
    static abstract IQueryResult<T> Conflict();
    static abstract IQueryResult<T> Forbidden();
}
