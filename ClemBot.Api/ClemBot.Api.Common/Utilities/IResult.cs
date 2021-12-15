namespace ClemBot.Api.Common.Utilities;

public interface IResult<T, U>
{
    T? Value { get; }
    U Status { get; }
}
