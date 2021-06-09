namespace ClemBot.Api.Core.Utilities
{
    public class AuthorizeResult<T>
    {
        public static Result<T, AuthorizeStatus> Success(T? val = default)
            => new(val, AuthorizeStatus.Success);

        public static Result<T, AuthorizeStatus> Forbidden()
            => new(default, AuthorizeStatus.Forbidden);
    }
}
