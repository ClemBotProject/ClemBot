
namespace ClemBot.Api.Core.Utilities
{
    /// <summary>
    /// Result class that allows for Monad inspired result reporting
    /// </summary>
    /// <typeparam name="T"></typeparam>
    /// <typeparam name="U"></typeparam>
    public readonly struct Result<T, U>
    {
        public T? Value { get; }

        public U Status { get; }

        public Result(T? val, U status)
        {
            Value = val;
            Status = status;
        }
    }
}
