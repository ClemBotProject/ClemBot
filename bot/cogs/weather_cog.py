# Thomas Delvaux
# 12-16-2020

import logging

import discord
import discord.ext.commands as commands
from bot.messaging.events import Events
from bot.bot_secrets import BotSecrets
from bot.consts import Colors

import aiohttp
import asyncio
import re
import datetime as dt

log = logging.getLogger(__name__)
url = "https://api.openweathermap.org/data/2.5/onecall"
url_Geo = "https://geocode.xyz/"

class WeatherCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    def getPageData(self, Lat, Lon, res_json, city, is_cond, is_hr, is_day):
        pages = []
        page = ''

        # For Converting Wind Degrees to Direction
        # Per http://snowfence.umn.edu/Components/winddirectionanddegrees.htm
        dirs = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']

        print(f'\nThis is fine 2\n')

        #########################################################
        # Normal Request with Current Conditions + Daily Forecast
        if is_cond:
            ################################
            # FIRST PAGE: Current Conditions

            # Current Conditions
            cond = res_json.get('current',{})

            # Location
            #city = res_json.get('name',{})

            # Current Temperature
            temp = cond.get('temp',{})

            # Weather Conditions
            desc = cond.get('weather',{})[0].get('description',{}).title()
            
            # Feels Like
            feels = cond.get('feels_like',{})

            # Humidity
            hum = cond.get('humidity',{})

            # Wind Speed and Direction
            wind = cond.get('wind_speed',{})
            wind_deg = cond.get('wind_deg',{})

            # Convert Wind Degrees to Direction
            ix = round(float(wind_deg) / (360. / len(dirs)))
            wind_dir = dirs[ix % len(dirs)]

            # Building the Page
            page += f'Location: {city} ({Lat},{Lon})\n'
            #page += f'Temperature: {round(temp,1)}°F\n'
            page += f'Temperature: {temp}°F\n'
            page += f'Condition:\t{desc}\n\n'

            page += f'Feels Like: {round(feels,1)}°F\n'
            page += f'Humidity: {round(hum)}%\n'
            page += f'Wind: {round(wind,1)} mph ({wind_dir})'
            
            pages.append(page)
            
        ######################
        # MULTI-PAGE: Forecast
        if is_hr and is_day:
            req_types = ['day', 'hr']
        elif is_hr:
            req_types = ['hr']
        elif is_day:
            req_types = ['day']
        else:
            req_types = []

        num_hr = ''
        num_day = ''

        for j, req_type in enumerate(req_types):
            if req_type == 'day':
                forecast = res_json.get('daily',{})
                num_day = len(forecast)-1
            else:
                forecast = res_json.get('hourly',{})
                num_hr = len(forecast)

            for i, val in enumerate(forecast):
                page=''
                
                # Date
                date = val.get('dt',{})

                if req_type == 'day':
                    date_num = dt.date.today() + dt.timedelta(days=i)
                    date_str = date_num.strftime("%A") 
                    # For reference: https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
                else:
                    time_num = dt.datetime.now().today() + dt.timedelta(hours=i)
                    if time_num.strftime("%d") == dt.datetime.now().today().strftime("%d"):
                        time_str = time_num.strftime("%I:%M %p (Today)")
                    else:
                        time_str = time_num.strftime("%I:%M %p (%A)")

                # Temperatures
                if req_type == 'day':
                    day_temp = val.get('temp',{}).get('day',{})
                    night_temp = val.get('temp',{}).get('night',{})
                else:
                    temp = val.get('temp',{})

                # Chance of Precipitation
                precp = val.get('pop',{})
                
                # Weather Conditions
                desc = val.get('weather',{})[0].get('description',{}).title()

                # Humidity
                hum = val.get('humidity',{})

                # Wind Speed and Direction
                wind = val.get('wind_speed',{})
                wind_deg = val.get('wind_deg',{})
                ix = round(float(wind_deg) / (360. / len(dirs)))
                wind_dir = dirs[ix % len(dirs)]

                # Building the Page
                if req_type == 'day':
                    if i > 1:
                        page += f'{date_str}: {round(day_temp,1)}°F\n'
                        page += f'{date_str} Night: {round(night_temp,1)}°F\n'
                    elif i == 1:
                        page += f'Tomorrow: {round(day_temp,1)}°F\n'
                        page += f'Tomorrow Night: {round(night_temp,1)}°F\n'
                    else:
                        page += f'Today: {round(day_temp,1)}°F\n'
                        page += f'Tonight: {round(night_temp,1)}°F\n'
                else:
                    page += f'Time: {time_str}\n'
                    page += f'Temperature: {round(temp,1)}°F\n'
                
                page += f'Condition: {desc}\n\n'
                page += f'Chance of Precipitation: {round(precp*100)}%\n'
                page += f'Humidity: {round(hum)}%\n'
                page += f'Wind: {round(wind,1)} mph ({wind_dir})\n\n'
                pages.append(page)
        
        return pages, num_hr, num_day

    async def weatherCode(self, ctx, loc, is_cond, is_hr, is_day):
        # Remove any characters not in ranges a-z, A-Z, or 0-9
        # Exceptions: & _ - , and <space>
        # per the ASCII Table https://www.asciitable.com
        loc = re.sub("[^a-zA-Z0-9 ,&_-]+", "", loc)

        # Geocoding URL
        url_GeoAPI = f'{url_Geo}{loc}'

        self.geocode_api_key = BotSecrets.get_instance().geocode_key
        self.weather_api_key = BotSecrets.get_instance().weather_key

        geo_queryparams = {
            'auth' : self.geocode_api_key,
            'json' : '1',
            }

        # Message to Display while APIs are called
        wait_msg = await ctx.send('Converting location')

        # Try Except for catching errors that could give away either API key
        try:
            async with aiohttp.request("GET", url_GeoAPI, params=geo_queryparams) as response:
                if (response.status == 200):
                    res_geo_json = await response.json()
                    city = res_geo_json.get('standard',{}).get('city',{})
                    lon = res_geo_json.get('longt',{})
                    lat = res_geo_json.get('latt',{})

                    queryparams = {
                        'lat' : lat,
                        'lon' : lon,
                        'appid' : self.weather_api_key,
                        'units' : 'imperial',
                        'lang' : 'en'
                        }

                    weatherPages = []
                    await wait_msg.edit(content='Checking the weather')
                    
                    async with aiohttp.request("GET", url, params=queryparams) as response:
                        if (response.status == 200):
                            res_json = await response.json()
                            print(f'\nThis is fine 1\n')
                            weatherPages, num_hr, num_day = self.getPageData(lat, lon, res_json, city, \
                                is_cond, is_hr, is_day)
                        
                        else:
                            embed = discord.Embed(title='OpenWeatherMap Weather', color=Colors.Error)
                            ErrMsg = f'Error Code: {response.status}'
                            embed.add_field(name='Error with weather API', value=ErrMsg, inline=False)
                            await ctx.send(embed=embed)
                            return

                        # Construct Title Message
                        msg_title = ''
                        if is_cond:
                            msg_title += f'Current Conditions'
                        if is_cond and (is_hr or is_day):
                            msg_title += ' with '
                        
                        if is_hr and is_day:
                            msg_title += 'Forecast'
                        elif is_hr:
                            msg_title += f'{num_hr}-Hour Forecast'
                        elif is_day:
                            msg_title += f'{num_day}-Day Forecast'

                        await wait_msg.delete()
                        await self.bot.messenger.publish(Events.on_set_pageable,
                            embed_name = 'OpenWeatherMap Weather',
                            field_title = msg_title,
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

    ##########################
    # USER EXECUTABLE COMMANDS    
    # Current Conditions with Daily Forecast
    @commands.group(pass_context=True, invoke_without_command=True, aliases=['forecast'])
    async def weather(self, ctx, loc):
        await self.weatherCode(ctx, loc, 1, 0, 1)

    # Current Conditions
    @weather.command(aliases=['conditions', 'current conditions'])
    async def current(self, ctx, loc):
        await self.weatherCode(ctx, loc, 1, 0, 0)
    
    # Daily and Hourly Forecasts
    @weather.command()
    async def forecast(self, ctx, loc):
        await self.weatherCode(ctx, loc, 0, 1, 1)

    # Hourly Forecast
    @weather.command()
    async def hourly(self, ctx, loc):
        await self.weatherCode(ctx, loc, 0, 1, 0)

    # Daily Forecast
    @weather.command()
    async def daily(self, ctx, loc):
        await self.weatherCode(ctx, loc, 0, 0, 1)

    # Current Conditions with Daily and Hourly Forecasts
    @weather.command(aliases=['everything'])
    async def all(self, ctx, loc):
        await self.weatherCode(ctx, loc, 1, 1, 1)

def setup(bot):
    bot.add_cog(WeatherCog(bot))