namespace ClemBot.Api.Common.Utilities;

public class AuthorizeResult<T> : IResult<T, AuthorizeStatus>
{
    public T? Value { get; }

    public AuthorizeStatus Status { get; }

    private AuthorizeResult(AuthorizeStatus status)
    {
        Status = status;
    }

    private AuthorizeResult(T? val, AuthorizeStatus status)
    {
        Status = status;
        Value = val;
    }

    public static AuthorizeResult<T> Success(T? val = default)
        => new(val, AuthorizeStatus.Success);

    public static AuthorizeResult<T> Forbidden()
        => new(AuthorizeStatus.Forbidden);

    public static AuthorizeResult<T> Failure()
        => new(AuthorizeStatus.Failure);

}
