using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Design;
using Microsoft.Extensions.Configuration;

namespace ClemBot.Api.Data.Contexts;

public class ClemBotContextDesignFactory : IDesignTimeDbContextFactory<ClemBotContext>
{
    public ClemBotContext CreateDbContext(string[] args)
    {
        var configuration = new ConfigurationBuilder()
            .AddUserSecrets<ClemBotContext>()
            .Build();

        var builder = new DbContextOptionsBuilder<ClemBotContext>();
        builder.UseNpgsql(configuration["ClemBotConnectionString"],
            o => o.UseNodaTime());

        return new ClemBotContext(builder.Options);
    }
}
