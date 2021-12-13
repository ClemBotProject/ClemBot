namespace ClemBot.Api.Common.Utilities;

public interface IAuthorizeResult<T> : IResult<T, AuthorizeStatus>
{
    static abstract IAuthorizeResult<T> Success(T? val);
    static abstract IAuthorizeResult<T> Forbidden();
}

public class AuthorizeResult<T> : IAuthorizeResult<T>
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

    public static IAuthorizeResult<T> Success(T? val = default)
        => new AuthorizeResult<T>(val, AuthorizeStatus.Success);

    public static IAuthorizeResult<T> Forbidden()
        => new AuthorizeResult<T>(AuthorizeStatus.Forbidden);

    public static IAuthorizeResult<T> Failure()
        => new AuthorizeResult<T>(AuthorizeStatus.Failure);

}
