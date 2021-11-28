
namespace ClemBot.Api.Common.Utilities;

/// <summary>
/// Result class that allows for Monad inspired result reporting
/// </summary>
/// <typeparam name="T"></typeparam>
/// <typeparam name="U"></typeparam>
public class Result<T, U> : IResult<T, U>
{
    public T? Value { get; }

    public U Status { get; }

    public Result(T? val, U status)
    {
        Value = val;
        Status = status;
    }
}
