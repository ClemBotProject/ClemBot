namespace ClemBot.Api.Common;

public static class Constants
{

    /// <summary>
    /// Configured max seq logging body size, if a log message exceeds this we will lose the message
    /// </summary>
    public static int SeqBodySizeMax => 262144;
}
