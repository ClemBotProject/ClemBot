using System;

namespace ClemBot.Api.Data.Exceptions;

public class EntityStateException<T> : Exception
{
    public T InvalidObject { get; set; }

    public EntityStateException(string message, T invalidEntity)
        :base(message)
    {
        InvalidObject = invalidEntity;
    }
}