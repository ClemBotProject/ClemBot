using System.Threading.Tasks;
using ClemBot.Api.Data.Contexts;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Logging;
using Quartz;

namespace ClemBot.Api.Services.Jobs;

public class MessageContentDeletionJob : IJob
{
    private readonly ClemBotContext _context;
    private readonly ILogger<MessageContentDeletionJob> _logger;

    private const int MESSAGE_RETENTION_TIME = 30;

    public MessageContentDeletionJob(ClemBotContext context, ILogger<MessageContentDeletionJob> logger)
    {
        _context = context;
        _logger = logger;
    }

    /// <summary>
    /// Job method that defines the compliance task to be executed on a Quartz.Net timer
    /// </summary>
    /// <param name="context"></param>
    public async Task Execute(IJobExecutionContext context)
    {
        _logger.LogInformation("Beginning Discord compliance Message Content Deletion");

        _context.Database.SetCommandTimeout(9000);
        var result = await _context.Database.ExecuteSqlRawAsync(
            @$"DELETE FROM ""Messages""
            WHERE ""Messages"".""Id"" IN
            (
                SELECT ""MessageId"" FROM ""MessageContents""
                WHERE ""MessageContents"".""Time""::date <= (NOW()::date -{MESSAGE_RETENTION_TIME}) at time zone 'utc'
                )"
            );
        _logger.LogInformation("Discord compliance Message Content Deletion complete: {Result} row(s) effected", result);
    }
}
