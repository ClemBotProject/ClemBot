namespace ClemBot.Api.Common.Extensions;

public static class EnumerableExtensions
{
    public static IEnumerable<T> WhereNotNull<T>(this IEnumerable<T?> enumerable)
    {
        foreach (var val in enumerable)
        {
            if (val is not null)
            {
                yield return val;
            }
        }
    }

    public static IEnumerable<T> WhereNotNull<T>(this IEnumerable<T?> enumerable) where T : struct
    {
        foreach (var val in enumerable)
        {
            if (val is not null)
            {
                yield return (T)val;
            }
        }
    }
}
