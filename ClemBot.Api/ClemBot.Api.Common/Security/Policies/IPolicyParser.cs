namespace ClemBot.Api.Common.Security.Policies;

public interface IPolicyParser<T>
{
    /// <summary>
    /// Defines a method to Parse out a given policies value
    /// that is provided to the PolicyProvider
    /// </summary>
    /// <param name="t"> Value to Serialize</param>
    /// <returns>Serialized Policy Values</returns>
    public string Serialize(T? t);

    /// <summary>
    /// Defines a method to Deserialize out a given policies value
    /// that is provided to the PolicyProvider
    /// </summary>
    /// <param name="val">String to deserialize into a T</param>
    /// <returns>Deserialized Policy Values</returns>
    public T? Deserialize(string val);
}
