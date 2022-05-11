namespace ClemBot.Api.Common
{
    public static class LinqExtensions
    {
        public static IQueryable<T> QueryIfElse<T>(this IQueryable<T> query,
                Func<bool> predicate,
                Func<IQueryable<T>, IQueryable<T>> @if,
                Func<IQueryable<T>, IQueryable<T>> @else) =>
            predicate() ? @if(query) : @else(query);
    }
}
