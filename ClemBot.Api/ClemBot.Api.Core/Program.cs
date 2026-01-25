using System.Text;
using System.Text.Json.Serialization;
using ClemBot.Api.Common;
using ClemBot.Api.Common.Exceptions;
using ClemBot.Api.Common.Security;
using ClemBot.Api.Common.Security.JwtToken;
using ClemBot.Api.Common.Security.OAuth;
using ClemBot.Api.Common.Security.Policies;
using ClemBot.Api.Common.Security.Policies.BotMaster;
using ClemBot.Api.Core.Behaviors;
using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Services.Authorization;
using ClemBot.Api.Services.GuildSettings;
using ClemBot.Api.Services.Jobs;
using FluentValidation;
using FluentValidation.AspNetCore;
using LinqToDB.EntityFrameworkCore;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Mvc.Infrastructure;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.IdentityModel.Tokens;
using Microsoft.OpenApi.Models;
using NodaTime;
using NodaTime.Serialization.SystemTextJson;
using Npgsql;
using Quartz;
using Serilog;
using Serilog.Events;
using Serilog.Formatting.Compact;
using Serilog.Formatting.Json;

Log.Logger = new LoggerConfiguration()
    .MinimumLevel.Override("Microsoft", LogEventLevel.Information)
    .Enrich.FromLogContext()
    .WriteTo.Console()
    .CreateBootstrapLogger();

const int discordMessageComplianceJobInterval = 24;


// ****** Creating the WebHostBuilder ******
Log.Information("Starting ClemBot.Api web host");
var builder = WebApplication.CreateBuilder(args);
// ******

// ****** Configure the host ******

//Set our user secrets as optional so
builder.Configuration.AddUserSecrets<ClemBotContext>(true);
builder.Configuration.AddEnvironmentVariables();

builder.Host.UseSerilog((context, provider, config) => {
    if (context.HostingEnvironment.IsProduction())
    {
        config.MinimumLevel.Override("Microsoft", LogEventLevel.Information)
            .Enrich.FromLogContext()
            .WriteTo.Console(new JsonFormatter());
    }
    else
    {
        config.MinimumLevel.Override("Microsoft", LogEventLevel.Information)
            .Enrich.FromLogContext()
            .WriteTo.Console();
    }
});

builder.Services.AddFluentValidationAutoValidation();
builder.Services.AddValidatorsFromAssemblyContaining<Program>();

builder.Services.AddControllers()
    .AddJsonOptions(options => {
        options.JsonSerializerOptions.Converters.Add(new JsonStringEnumConverter());
        options.JsonSerializerOptions.ConfigureForNodaTime(DateTimeZoneProviders.Tzdb);
    });
// ******

// ****** Configure Services ******

// Get Bots api key to check requests for from config
var apiKey = builder.Configuration[ConfigurationKeys.BotApiKey];
if (apiKey is null)
{
    throw new ConfigurationException("Failed to get bot api key from config object");
}

builder.Services.AddSingleton(new ApiKey { Key = apiKey });

// Generate JWT token with random access key
var jwtTokenConfig = builder.Configuration.GetSection("JwtTokenConfig").Get<JwtTokenConfig>();
if (jwtTokenConfig is null)
{
    throw new ConfigurationException($"Failed to get {nameof(JwtTokenConfig)} from config object");
}

jwtTokenConfig.Secret = Guid.NewGuid().ToString();
builder.Services.AddSingleton(jwtTokenConfig);

// *** Add Security Services to container ***
// Add JWT generator to DI
builder.Services.AddScoped<IJwtAuthManager, JwtAuthManager>();

// Add the discord oauth service
builder.Services.AddScoped<IDiscordAuthManager, DiscordAuthManager>();

// Configure Mediatr and the pipelines
builder.Services.AddMediatR(config =>
{
    config.RegisterServicesFromAssemblyContaining<Program>();
    config.RegisterServicesFromAssemblyContaining<GuildSandboxAuthorizeService>();
    config.AddOpenBehavior(typeof(LoggingBehavior<,>));
    config.AddOpenBehavior(typeof(GuildSandboxAuthorizeBehavior<,>));
    config.AddOpenBehavior(typeof(CacheRequestBehavior<,>));
});

// Specify Swagger startup options
builder.Services.AddSwaggerGen(o => {
    o.SwaggerDoc("v1",
        new OpenApiInfo
        {
            Title = "ClemBot.Api",
            Version = "1.0.0",
            Description = "ClemBot Backend API Implementation",
            License = new OpenApiLicense
            {
                Name = "Use under MIT",
                Url = new Uri("https://opensource.org/licenses/MIT")
            }
        });
    o.CustomSchemaIds(type => type.ToString());
    o.AddSecurityDefinition("Bearer", new OpenApiSecurityScheme
    {
        In = ParameterLocation.Header,
        Description = "Please insert JWT with Bearer into field",
        Name = "Authorization",
        Type = SecuritySchemeType.ApiKey
    });
    o.AddSecurityRequirement(new OpenApiSecurityRequirement {
        {
            new OpenApiSecurityScheme
            {
                Reference = new OpenApiReference
                {
                    Type = ReferenceType.SecurityScheme,
                    Id = "Bearer"
                }
            },
            new string[] { }
        }
    });
});

// Add our caching dependency
builder.Services.AddLazyCache();

// Set up quartz
builder.Services.AddQuartz(options => {
    options.UseMicrosoftDependencyInjectionJobFactory();

    options.ScheduleJob<MessageContentDeletionJob>(trigger => trigger
        .WithIdentity("MessageContentDeletion", "DiscordCompliance")
        .StartNow()
        .WithSimpleSchedule(x => x
            .WithIntervalInHours(discordMessageComplianceJobInterval)
            .RepeatForever())
        .WithDescription("Discord Compliance Message Content Deletion Job")
    );
});

builder.Services.AddQuartzServer(options => options.WaitForJobsToComplete = true);

builder.Services.AddCors(options => options.AddDefaultPolicy(
        policyBuilder => {
            policyBuilder.AllowAnyOrigin();
            policyBuilder.AllowAnyHeader();
            policyBuilder.AllowAnyMethod();
        }));

// Grab connection string from config
var connectionString = builder.Configuration[ConfigurationKeys.DbConnectionString];
if (connectionString is null)
{
    throw new ConfigurationException("Failed to get database Connection String from config object");
}

// Set the db context for DI injection
builder.Services.AddDbContext<ClemBotContext>(options =>
    options.UseNpgsql(connectionString, optionsBuilder => optionsBuilder.UseNodaTime()));

builder.Services.AddHttpClient();
builder.Services.AddHttpContextAccessor();

// Initialize the Authentication middleware
builder.Services.AddAuthentication(options => {
    options.DefaultAuthenticateScheme = JwtBearerDefaults.AuthenticationScheme;
    options.DefaultChallengeScheme = JwtBearerDefaults.AuthenticationScheme;
}).AddJwtBearer(x => {
    x.SaveToken = true;
    x.TokenValidationParameters = new TokenValidationParameters
    {
        ValidIssuer = jwtTokenConfig.Issuer,
        ValidateIssuer = true,
        ValidateIssuerSigningKey = true,
        IssuerSigningKey = new SymmetricSecurityKey(Encoding.ASCII.GetBytes(jwtTokenConfig.Secret)),
        ValidAudience = jwtTokenConfig.Audience,
        ValidateAudience = true,
        ValidateLifetime = true
    };
});

builder.Services.AddAuthorization(options => options.AddPolicy(Policies.BotMaster, policy => policy.RequireClaim(Claims.BotApiKey)));
// Add authorization policy providers
builder.Services.AddScoped<IAuthorizationHandler, BotMasterAuthHandler>();
builder.Services.AddSingleton<IAuthorizationPolicyProvider, GuildSandboxPolicyProvider>();

// Register services
builder.Services.AddScoped<IGuildSandboxAuthorizeService, GuildSandboxAuthorizeService>();
builder.Services.AddScoped<IGuildSettingsService, GuildSettingsService>();
builder.Services.AddSingleton<IActionContextAccessor, ActionContextAccessor>();

GuildConfig.Initialize();
// ******


// ****** Build and configure the WebApplication ******
var app = builder.Build();

// ****** Create the EF Context scope and inject ClemBotContext
using var scope = app.Services.CreateScope();
var context = scope.ServiceProvider.GetRequiredService<ClemBotContext>();
// ******

if (app.Environment.IsDevelopment())
{
    app.UseDeveloperExceptionPage();
    app.UseSwagger();
    app.UseSwaggerUI(c => c.SwaggerEndpoint("/swagger/v1/swagger.json", "ClemBot.Api 1.0.0"));
}

app.UseSerilogRequestLogging();

app.UseRouting();

app.UseCors();

app.UseAuthentication();
app.UseAuthorization();

app.MapControllers();

// Apply any new migrations
context.Database.Migrate();

// ensure pg_trgm is installed (needed for trigrams support)
context.Database.ExecuteSqlRaw("CREATE EXTENSION IF NOT EXISTS pg_trgm");

// Load linq2db for bulk copies
LinqToDBForEFTools.Initialize();

// Reload enum types after a migration
await using (var conn = (NpgsqlConnection)context.Database.GetDbConnection())
{
    await conn.OpenAsync();
    await conn.ReloadTypesAsync();
}
// ******


// ****** Run the API ******
try
{
    await app.RunAsync();
}
catch (Exception ex)
{
    Log.Fatal(ex, "ClemBot.Api terminated unexpectedly");
    return 1;
}
finally
{
    Log.CloseAndFlush();
}

return 0;
