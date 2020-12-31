# Thomas Delvaux
# 12-16-2020

# API Used:
# 

import logging

import discord
import discord.ext.commands as commands
from bot.messaging.events import Events
from bot.bot_secrets import BotSecrets
from bot.consts import Colors

#import requests
import aiohttp
import asyncio
import re

log = logging.getLogger(__name__)

class WeatherCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    def getPageData(self,Lat,Lon,res_json,city):
        pages = []
        
        # FIRST PAGE: Current Conditions
        page = ''

        # Location
        #city = res_json.get('name',{})
        page += f'Location: {city} ({Lat},{Lon})\n'

        # Current Temperature
        temp = res_json.get('current',{}).get('temp',{})
        page += f'Temperature: {temp}°F\n'

        # Weather Conditions
        desc = res_json.get('current',{}).get('weather',{})[0].get('description',{}).title()
        page += f'Condition:\t{desc}\n\n'
        
        # Feels Like
        feels = res_json.get('current',{}).get('feels_like',{})
        page += f'Feels Like: {feels}°F\n'

        # Humidity
        hum = res_json.get('current',{}).get('humidity',{})
        page += f'Humidity: {hum}%\n'

        # Wind Speed and Direction
        wind = res_json.get('current',{}).get('wind_speed',{})
        wind_deg = res_json.get('current',{}).get('wind_deg',{})

        # Convert Wind Degrees to Direction
        # Per http://snowfence.umn.edu/Components/winddirectionanddegrees.htm
        dirs = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
        ix = round(float(wind_deg) / (360. / len(dirs)))
        wind_dir = dirs[ix % len(dirs)]

        page += f'Wind: {wind} mph ({wind_dir})'
        
        pages.append(page)
        
        # MULTI-PAGE: Forecast
        for i in range(8):
            page=''
            
            # Temperatures
            day_temp = res_json.get('daily',{})[i].get('temp',{}).get('day',{})
            night_temp = res_json.get('daily',{})[i].get('temp',{}).get('night',{})
            
            # Chance of Precipitation
            precp = res_json.get('daily',{})[i].get('pop',{})
            
            # Weather Conditions
            desc = res_json.get('daily',{})[i].get('weather',{})[0].get('description',{}).title()

            # Humidity
            hum = res_json.get('daily',{})[i].get('humidity',{})

            # Wind Speed and Direction
            wind = res_json.get('daily',{})[i].get('wind_speed',{})
            wind_deg = res_json.get('daily',{})[i].get('wind_deg',{})
            ix = round(float(wind_deg) / (360. / len(dirs)))
            wind_dir = dirs[ix % len(dirs)]

            if i > 1:
                page += f'Day {i}: {day_temp}°F\n'
                page += f'Night {i}: {night_temp}°F\n'
            elif i == 1:
                page += f'Tomorrow: {day_temp}°F\n'
                page += f'Tomorrow Night: {night_temp}°F\n'
            else:
                page += f'Today: {day_temp}°F\n'
                page += f'Tonight: {night_temp}°F\n'
            
            page += f'Condition: {desc}\n\n'
            page += f'Chance of Precipitation: {round(precp*100)}%\n'
            page += f'Humidity: {hum}%\n'
            page += f'Wind: {wind} mph ({wind_dir})\n\n'
            pages.append(page)

            '''
            if i % 2 != 0 and i != 7:
                pages.append(page)
                page = ''
            else:
                page += '\n\n' 
            '''
        pages.append(page)
        
        return pages

    @commands.command()
    async def weather(self, ctx, loc):
        """
        Determine the weather at a given location

        USE:
        EXAMPLE:
        """

        # Remove any characters besides &, _, or - that are not in ranges a-z, A-Z, or 0-9
        # Exceptions:
        # & _ - and ,
        # per the ASCII Table https://www.asciitable.com
        loc = re.sub("[^a-zA-Z0-9 ,&_-]+", "", loc)

        # Geocoding URL
        url_GeoAPI = f'https://geocode.xyz/{loc}'

        self.geocode_api_key = BotSecrets.get_instance().geocode_key
        self.weather_api_key = BotSecrets.get_instance().weather_key

        geo_queryparams = {
            'auth' : self.geocode_api_key,
            'json' : '1',
            }

        # Try Except for catching errors that could give away either API key
        try:
            async with aiohttp.request("GET", url_GeoAPI, params=geo_queryparams) as response:
                if (response.status == 200):
                    res_geo_json = await response.json()
                    city = res_geo_json.get('standard',{}).get('city',{})
                    lon = res_geo_json.get('longt',{})
                    lat = res_geo_json.get('latt',{})
                    
                    url = "https://api.openweathermap.org/data/2.5/onecall"

                    queryparams = {
                        'lat' : lat,
                        'lon' : lon,
                        'exclude' : 'minutely,hourly',
                        'appid' : self.weather_api_key,
                        'units' : 'imperial',
                        'lang' : 'en'
                        }

                    weatherPages = []

                    async with aiohttp.request("GET", url, params=queryparams) as response:
                        if (response.status == 200):
                            res_json = await response.json()
                            weatherPages = self.getPageData(lat,lon,res_json,city)
                        
                        else:
                            embed = discord.Embed(title='OpenWeatherMap Weather', color=Colors.Error)
                            ErrMsg = f'Error Code: {response.status}'
                            embed.add_field(name='Error with weather API', value=ErrMsg, inline=False)
                            await ctx.send(embed=embed)
                            return

                        await self.bot.messenger.publish(Events.on_set_pageable,
                            embed_name = 'OpenWeatherMap Weather',
                            field_title = 'Current Conditions and 7-Day Forecast',
                            pages = weatherPages,
                            author = ctx.author,
                            channel = ctx.channel)
                
                else:
                    embed = discord.Embed(title='OpenWeatherMap Weather', color=Colors.Error)
                    ErrMsg = f'Error Code: {response.status}'
                    embed.add_field(name='Error with geocode API', value=ErrMsg, inline=False)
                    await ctx.send(embed=embed)
                    return
                """ 
                # FOR DEBUGGING. Takes a minute or two for message to display when enabled
                await self.bot.messenger.publish(Events.on_set_pageable,
                    embed_name = 'Geocoding Results',
                    field_title = 'Location',
                    pages = [f'Query: {loc}\n\nLatitude: {lat}\nLongitude: {lon}'],
                    author = ctx.author,
                    channel = ctx.channel)
                """
        except Exception as err:
            err_str = str(err)
            err_str = re.sub(self.geocode_api_key, "CLASSIFIED", err_str)
            err_str = re.sub(self.weather_api_key, "CLASSIFIED", err_str)
            raise Exception(err_str).with_traceback(err.__traceback__)

def setup(bot):
    bot.add_cog(WeatherCog(bot))