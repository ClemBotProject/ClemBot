using System.Threading.Tasks;
using ClemBot.Api.Data.Contexts;
using Microsoft.EntityFrameworkCore;
using Quartz;
using Serilog;

namespace ClemBot.Api.Services.Jobs;

public class MessageContentDeletionJob : IJob
{
    private readonly ClemBotContext _context;
    private readonly ILogger _logger;

    private const int MESSAGE_RETENTION_TIME = 30;

    public MessageContentDeletionJob(ClemBotContext context, ILogger logger)
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
        _logger.Information("Beginning Discord compliance Message Content Deletion");

        _context.Database.SetCommandTimeout(9000);
        var result = await _context.Database.ExecuteSqlRawAsync(@$"
                UPDATE ""MessageContents""
                SET ""Content"" = 'Content Deleted'
                WHERE ""MessageContents"".""Time""::date <= (NOW()::date -{MESSAGE_RETENTION_TIME}) at time zone 'utc'
                ");

        _logger.Information("Discord compliance Message Content Deletion complete: {Result} row(s) effected", result);
    }
}
