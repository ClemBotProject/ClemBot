using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Text.Json.Serialization;
using System.Threading.Tasks;
using ClemBot.Api.Core.Behaviors;
using ClemBot.Api.Core.Security;
using ClemBot.Api.Core.Security.JwtToken;
using ClemBot.Api.Core.Security.Policies;
using ClemBot.Api.Core.Security.Policies.BotMaster;
using ClemBot.Api.Core.Security.Policies.GuildSandbox;
using ClemBot.Api.Data.Contexts;
using ClemBot.Api.Data.Enums;
using ClemBot.Api.Services.Guilds.Models;
using FluentValidation.AspNetCore;
using LinqToDB.EntityFrameworkCore;
using MediatR;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.HttpsPolicy;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using Microsoft.IdentityModel.Tokens;
using Microsoft.OpenApi.Models;
using Npgsql;
using Serilog;

namespace ClemBot.Api.Core
{
    public class Startup
    {
        public Startup(IConfiguration configuration)
        {
            Configuration = configuration;
        }

        public IConfiguration Configuration { get; }

        // This method gets called by the runtime. Use this method to add services to the container.
        public void ConfigureServices(IServiceCollection services)
        {

            services.AddControllers()
                .AddFluentValidation(s => {
                    s.RegisterValidatorsFromAssemblyContaining<Startup>();
                })
                .AddJsonOptions(options => {
                    options.JsonSerializerOptions.Converters.Add(new JsonStringEnumConverter());
                });

            // Get Bots api key to check requests for from config
            var apiKey = Configuration["BotApiKey"];
            services.AddSingleton(new ApiKey() { Key = apiKey });

            // Generate JWT token with random access key
            var jwtTokenConfig = Configuration.GetSection("JwtTokenConfig").Get<JwtTokenConfig>();
            jwtTokenConfig.Secret = Guid.NewGuid().ToString();
            services.AddSingleton(jwtTokenConfig);

            // Add JWT generator to DI
            services.AddScoped<IJwtAuthManager, JwtAuthManager>();

            services.AddMediatR(typeof(Startup), typeof(GuildExistsRequest));
            services.AddScoped(typeof(IPipelineBehavior<,>), typeof(LoggingBehavior<,>));

            // Specify Swagger startup options
            services.AddSwaggerGen(o => {
                o.SwaggerDoc("v1", new OpenApiInfo
                {
                    Title = "ClemBot.Api",
                    Version = "1.0.0",
                    Description = "ClemBot Backend API Implementation",
                    License = new OpenApiLicense()
                    {
                        Name = "Use under MIT",
                        Url = new Uri("https://opensource.org/licenses/MIT")
                    }
                });
                o.CustomSchemaIds(type => type.ToString());
            });

            // Add our caching dependency
            services.AddLazyCache();

            services.AddCors(options => {
                options.AddDefaultPolicy(
                    builder => {
                        builder.WithOrigins("http://localhost:3000");
                    });
            });

            // Grab connection string from config
            var connectionString = Configuration["ClemBotConnectionString"];

            // Set the db context for DI injection
            services.AddDbContext<ClemBotContext>(options =>
                options.UseNpgsql(connectionString));

            services.AddHttpClient();
            services.AddHttpContextAccessor();

            // Initialize the Authentication middleware
            services.AddAuthentication(options => {
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
                    ValidateAudience = true
                };
            });

            services.AddAuthorization(options => {
                options.AddPolicy(Policies.BotMaster, policy => {
                    policy.RequireClaim(Claims.BotApiKey);
                });
            });
            // Add authorization policy providers
            services.AddScoped<IAuthorizationHandler, BotMasterAuthHandler>();
            services.AddScoped<IAuthorizationHandler, GuildSandboxAuthHandler>();
            services.AddSingleton<IAuthorizationPolicyProvider, GuildSandboxPolicyProvider>();

        }

        // This method gets called by the runtime. Use this method to configure the HTTP request pipeline.
        public void Configure(IApplicationBuilder app, IWebHostEnvironment env, ClemBotContext context)
        {
            if (env.IsDevelopment())
            {
                app.UseDeveloperExceptionPage();
                app.UseSwagger();
                app.UseSwaggerUI(c => c.SwaggerEndpoint("/swagger/v1/swagger.json", "ClemBot.Api 1.0.0"));
            }
            app.UseSerilogRequestLogging();

            app.UseHttpsRedirection();

            app.UseRouting();

            app.UseCors();

            app.UseAuthentication();
            app.UseAuthorization();

            app.UseEndpoints(endpoints => endpoints.MapControllers());

            // Apply any new migrations
            context.Database.Migrate();

            // Load linq2db for bulk copies
            LinqToDBForEFTools.Initialize();


            // Reload enum types after a migration
            using var conn = (NpgsqlConnection)context.Database.GetDbConnection();
            conn.Open();
            conn.ReloadTypes();
        }
    }
}
