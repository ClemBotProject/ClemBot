using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using System.Text;
using Microsoft.IdentityModel.Tokens;

namespace ClemBot.Api.Common.Security.JwtToken;

public class JwtAuthManager : IJwtAuthManager
{
    private readonly JwtTokenConfig _jwtTokenConfig;
    private readonly byte[] _secret;

    public JwtAuthManager(JwtTokenConfig jwtTokenConfig)
    {
        _jwtTokenConfig = jwtTokenConfig;
        _secret = Encoding.ASCII.GetBytes(_jwtTokenConfig.Secret);
    }

    /// <inheritdoc cref="IJwtAuthManager.GenerateToken"/>
    public string GenerateToken(IEnumerable<Claim> claims, DateTime expires)
    {
        var tokenDescriptor = new SecurityTokenDescriptor
        {
            Subject = new ClaimsIdentity(claims),
            Expires = expires,
            SigningCredentials = new SigningCredentials(
                new SymmetricSecurityKey(_secret),
                SecurityAlgorithms.HmacSha256Signature),
            Audience = _jwtTokenConfig.Audience,
            Issuer = _jwtTokenConfig.Issuer
        };

        var tokenHandler = new JwtSecurityTokenHandler();
        var securityToken = tokenHandler.CreateToken(tokenDescriptor);
        var token = tokenHandler.WriteToken(securityToken);
        return token;
    }
}
