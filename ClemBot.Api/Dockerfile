# syntax=docker/dockerfile:1
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build-env
WORKDIR /ClemBot.Api

# Copy everything else and build
COPY . ./
RUN dotnet publish . -c Release -o out

# Build runtime image
FROM mcr.microsoft.com/dotnet/aspnet:8.0
WORKDIR /ClemBot.Api

COPY --from=build-env /ClemBot.Api/out .
ENTRYPOINT ["dotnet", "ClemBot.Api.Core.dll"]
