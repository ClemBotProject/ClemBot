using System;
using System.Collections.Generic;
using System.Security.Claims;

namespace ClemBot.Api.Core.Security.JwtToken
{
    public interface IJwtAuthManager
    {
        /// <summary>
        /// Generates a JWT Token for a given enumerable of claims and date
        /// </summary>
        /// <param name="claims"></param>
        /// <param name="now"></param>
        /// <returns></returns>
        public string GenerateToken(IEnumerable<Claim> claims, DateTime now);
    }
}
