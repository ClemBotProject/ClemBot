# Thomas Delvaux
# 12-16-2020

import datetime as dt
import logging
import re

import aiohttp
import discord
import discord.ext.commands as commands

import bot.bot_secrets as bot_secrets
import bot.extensions as ext
from bot.consts import Colors
from bot.messaging.events import Events

log = logging.getLogger(__name__)
URL_WEATHER = "https://api.openweathermap.org/data/2.5/onecall"
URL_GEO = "https://geocode.xyz/"


class WeatherCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    def getPageData(self, Lat, Lon, res_weather_json, city, is_cond, is_hr, is_day):
        pages = []
        page = ''

        # For Converting Wind Degrees to Direction
        # Per http://snowfence.umn.edu/Components/winddirectionanddegrees.htm
        dirs = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']

        #########################################################
        # Normal Request with Current Conditions + Daily Forecast
        if is_cond:
            ################################
            # FIRST PAGE: Current Conditions

            # Current Conditions
            cond = res_weather_json.get('current', {})

            # Location
            # city = res_weather_json.get('name',{})

            # Current Temperature
            temp = cond.get('temp', {})

            # Weather Conditions
            desc = cond.get('weather', {})[0].get('description', {}).title()

            # Feels Like
            feels = cond.get('feels_like', {})

            # Humidity
            hum = cond.get('humidity', {})

            # Wind Speed and Direction
            wind = cond.get('wind_speed', {})
            wind_deg = cond.get('wind_deg', {})

            # Convert Wind Degrees to Direction
            ix = round(float(wind_deg) / (360. / len(dirs)))
            wind_dir = dirs[ix % len(dirs)]

            # Building the Page
            page += f'Location: {city} ({Lat},{Lon})\n'
            # page += f'Temperature: {round(temp,1)}°F\n'
            page += f'Temperature: {temp}°F / {round((temp - 32) * (5 / 9), 2)}°C\n'
            page += f'Condition:\t{desc}\n\n'

            page += f'Feels Like: {round(feels, 1)}°F / {round((feels - 32) * (5 / 9), 1)}°C\n'
            page += f'Humidity: {round(hum)}%\n'
            page += f'Wind: {round(wind, 1)} mph / {round(wind * 1.609344, 1)} kmh ({wind_dir})'

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
                forecast = res_weather_json.get('daily', {})
                num_day = len(forecast) - 1
            else:
                forecast = res_weather_json.get('hourly', {})
                num_hr = len(forecast)

            for i, val in enumerate(forecast):
                page = ''

                # Date
                date = val.get('dt', {})

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
                    day_temp = val.get('temp', {}).get('day', {})
                    night_temp = val.get('temp', {}).get('night', {})
                else:
                    temp = val.get('temp', {})

                # Chance of Precipitation
                precp = val.get('pop', {})

                # Weather Conditions
                desc = val.get('weather', {})[0].get('description', {}).title()

                # Humidity
                hum = val.get('humidity', {})

                # Wind Speed and Direction
                wind = val.get('wind_speed', {})
                wind_deg = val.get('wind_deg', {})
                ix = round(float(wind_deg) / (360. / len(dirs)))
                wind_dir = dirs[ix % len(dirs)]

                # Building the Page
                if req_type == 'day':
                    if i > 1:
                        page += f'{date_str}: {round(day_temp, 1)}°F / {round((day_temp - 32) * (5 / 9), 1)}°C\n'
                        page += f'{date_str} Night: {round(night_temp, 1)}°F / {round((night_temp - 32) * (5 / 9), 1)}°C\n'
                    elif i == 1:
                        page += f'Tomorrow: {round(day_temp, 1)}°F / {round((day_temp - 32) * (5 / 9), 1)}°C\n'
                        page += f'Tomorrow Night: {round(night_temp, 1)}°F / {round((night_temp - 32) * (5 / 9), 1)}°C\n'
                    else:
                        page += f'Today: {round(day_temp, 1)}°F / {round((day_temp - 32) * (5 / 9), 1)}°C\n'
                        page += f'Tonight: {round(night_temp, 1)}°F / {round((night_temp - 32) * (5 / 9), 1)}°C\n'
                else:
                    page += f'Time: {time_str}\n'
                    page += f'Temperature: {round(temp, 1)}°F / {round((temp - 32) * (5 / 9), 1)}°C\n'

                page += f'Condition: {desc}\n\n'
                page += f'Chance of Precipitation: {round(precp * 100)}%\n'
                page += f'Humidity: {round(hum)}%\n'
                page += f'Wind: {round(wind, 1)} mph / {round(wind * 1.609344, 1)} kmh ({wind_dir})\n\n'
                pages.append(page)

        return pages, num_hr, num_day

    async def weatherCode(self, ctx, loc, is_cond, is_hr, is_day):
        # Remove any characters not in ranges a-z, A-Z, or 0-9
        # Exceptions: & _ - , and <space>
        # per the ASCII Table https://www.asciitable.com
        loc = re.sub("[^a-zA-Z0-9 ,&_-]+", "", loc)

        # Geocoding URL
        url_Geo_API = f'{URL_GEO}{loc}'

        self.geocode_api_key = bot_secrets.secrets.geocode_key
        self.weather_api_key = bot_secrets.secrets.weather_key

        geo_queryparams = {
            'auth': self.geocode_api_key,
            'json': '1',
        }

        # Message to Display while APIs are called
        wait_msg = await ctx.send('Converting location')

        # Try Except for catching errors that could give away either API key
        try:
            async with aiohttp.request("GET", url_Geo_API, params=geo_queryparams) as response:
                if (response.status != 200):
                    embed = discord.Embed(title='OpenWeatherMap Weather', color=Colors.Error)
                    ErrMsg = f'Error Code: {response.status}'
                    embed.add_field(name='Error with geocode API', value=ErrMsg, inline=False)
                    await ctx.send(embed=embed)
                    return
                res_geo_json = await response.json()
        except Exception as err:
            err_str = str(err)
            err_str = re.sub(self.geocode_api_key, "CLASSIFIED", err_str)
            err_str = re.sub(self.weather_api_key, "CLASSIFIED", err_str)
            raise Exception(err_str).with_traceback(err.__traceback__)

        geo_err = res_geo_json.get('error', {}).get('code', {})
        geo_err_desc = res_geo_json.get('error', {}).get('description', {})
        city = res_geo_json.get('standard', {}).get('city', {})
        lon = res_geo_json.get('longt', {})
        lat = res_geo_json.get('latt', {})

        if geo_err:
            embed = discord.Embed(title='OpenWeatherMap Weather', color=Colors.Error)
            ErrMsg = f'Error Code {geo_err}: {geo_err_desc}'
            embed.add_field(name='Error with geocode API', value=ErrMsg, inline=False)
            await ctx.send(embed=embed)
            await wait_msg.delete()
            return

        queryparams = {
            'lat': lat,
            'lon': lon,
            'appid': self.weather_api_key,
            'units': 'imperial',
            'lang': 'en'
        }

        weatherPages = []
        await wait_msg.edit(content='Checking the weather')

        try:
            async with aiohttp.request("GET", URL_WEATHER, params=queryparams) as response:
                if (response.status != 200):
                    embed = discord.Embed(title='OpenWeatherMap Weather', color=Colors.Error)
                    ErrMsg = f'Error Code: {response.status}'
                    embed.add_field(name='Error with weather API', value=ErrMsg, inline=False)
                    await ctx.send(embed=embed)
                    return
                res_weather_json = await response.json()
        except Exception as err:
            err_str = str(err)
            err_str = re.sub(self.geocode_api_key, "CLASSIFIED", err_str)
            err_str = re.sub(self.weather_api_key, "CLASSIFIED", err_str)
            raise Exception(err_str).with_traceback(err.__traceback__)

        weatherPages, num_hr, num_day = self.getPageData(
            lat,
            lon,
            res_weather_json,
            city,
            is_cond,
            is_hr,
            is_day)

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
        await self.bot.messenger.publish(Events.on_set_pageable_text,
                                         embed_name='OpenWeatherMap Weather',
                                         field_title=msg_title,
                                         pages=weatherPages,
                                         author=ctx.author,
                                         channel=ctx.channel)

        """ 
        # FOR DEBUGGING. Takes a minute or two for message to display when enabled
        await self.bot.messenger.publish(Events.on_set_pageable_text,
            embed_name = 'Geocoding Results',
            field_title = 'Location',
            pages = [f'Query: {loc}\n\nLatitude: {lat}\nLongitude: {lon}'],
            author = ctx.author,
            channel = ctx.channel)
        """

    ##########################
    # USER EXECUTABLE COMMANDS    
    # Current Conditions with Daily Forecast
    @ext.group(case_insensitive=True, invoke_without_command=True, aliases=['forecast'])
    @ext.long_help(
        """
        This command provides the current weather conditions and daily forecast for a user-specified location, in that order.

        Examples of locations shown below.
        
        Note: The format `City, ST` (ST = State Abbreviation) is **not** currently supported.
        """
    )
    @ext.short_help('Provides location-based weather info')
    @ext.example(('weather <location>', 'weather Clemson', 'weather 29631', 'weather Clemson, South Carolina', \
                  'weather Clemson, SC, USA', 'weather 105 Sikes Hall, Clemson, SC 29634'))
    async def weather(self, ctx, *, location):  # the * is used to "greedily" catch all text after it in the variable "loc"
        await self.weatherCode(ctx, location, 1, 0, 1)

    # Current Conditions
    @weather.command(aliases=['conditions', 'current conditions'])
    @ext.long_help(
        """
        This sub-command provides the current weather conditions for a user-specified location.
        
        Additional examples of locations provided in the `weather` command help message.
        """
    )
    @ext.short_help('Current weather conditions')
    @ext.example('weather current Clemson')
    async def current(self, ctx, *, location):
        await self.weatherCode(ctx, location, 1, 0, 0)

    # Daily and Hourly Forecasts
    @weather.command(aliases=['forecasts'])
    @ext.long_help(
        """
        This sub-command provides the daily and hourly weather forecasts for a user-specified location, in that order.
        
        Additional examples of locations provided in the `weather` command help message.
        """
    )
    @ext.short_help('Daily and hourly forecasts')
    @ext.example('weather forecast Clemson')
    async def forecast(self, ctx, *, location):
        await self.weatherCode(ctx, location, 0, 1, 1)

    # Hourly Forecast
    @weather.command()
    @ext.long_help(
        """
        This sub-command provides the hourly weather forecast for a user-specified location.
        
        Additional examples of locations provided in the `weather` command help message.
        """
    )
    @ext.short_help('Hourly forecast')
    @ext.example('weather hourly Clemson')
    async def hourly(self, ctx, *, location):
        await self.weatherCode(ctx, location, 0, 1, 0)

    # Daily Forecast
    @weather.command()
    @ext.long_help(
        """
        This sub-command provides the daily weather forecast for a user-specified location.
        
        Additional examples of locations provided in the `weather` command help message.
        """
    )
    @ext.short_help('Daily forecast')
    @ext.example('weather daily Clemson')
    async def daily(self, ctx, *, location):
        await self.weatherCode(ctx, location, 0, 0, 1)

    # Current Conditions with Daily and Hourly Forecasts
    @weather.command(aliases=['everything'])
    @ext.long_help(
        """
        This sub-command provides the current weather conditions with daily and hourly forecasts for a user-specified location, in that order.
        
        Additional examples of locations provided in the `weather` command help message.
        """
    )
    @ext.short_help('Current conditions w/hourly and daily forecast')
    @ext.example(('weather all Clemson', 'weather everything Clemson'))
    async def all(self, ctx, *, location):
        await self.weatherCode(ctx, location, 1, 1, 1)


def setup(bot):
    bot.add_cog(WeatherCog(bot))
