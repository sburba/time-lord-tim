import os
from datetime import datetime, tzinfo, timedelta
import re
from enum import Enum, auto
from typing import Optional, Iterator

import pytz
from discord import Intents
from pytz import timezone

from src.best_distinct_spans import best_distinct_spans

import discord

strict_time_regex = re.compile(
    r"\d{1,2}\s*(am|pm)|\d{1,2}:\d{2}(\s*(am|pm))?", re.IGNORECASE
)

lenient_time_regex = re.compile(r"(at \d{1,2})|((?<!in )\d{1,2}\s*ish)", re.IGNORECASE)

intents = Intents.default()
intents.members = True
client = discord.Client(intents=Intents(messages=True, members=True))


@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")


timezones_by_user_id: dict[int, tzinfo] = {
    147404516248125441: timezone("America/Detroit"),  # Sam
    286342167436328960: timezone("America/Los_Angeles"),  # Stephen
}


@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:
        return

    user_tz = timezones_by_user_id.get(message.author.id)
    if not user_tz:
        await message.channel.send("PUT YOUR FUCKING TIMEZONE IN")
        return

    priority_matches = strict_time_regex.finditer(message.content)
    secondary_matches = lenient_time_regex.finditer(message.content)
    matches = best_distinct_spans(priority_matches, secondary_matches)
    times = [parse_time(match.group(0), user_tz) for match in matches]

    if times:
        timezones: set[tzinfo] = {
            timezones_by_user_id.get(member.id)
            for member in message.channel.members
            if member.id in timezones_by_user_id
        }

        timezones.remove(user_tz)

        member_ids = [member.name for member in message.channel.members]

        time_lines = []
        for time in times:
            localized_times = [
                time.astimezone(tz).strftime("%-I:%M%p %Z") for tz in timezones
            ]
            time_line = (
                time.astimezone(user_tz).strftime("%-I:%M%p %Z")
                + ": "
                + ", ".join(localized_times)
            )
            time_lines.append(time_line)

        await message.channel.send("\n".join(time_lines))


class TimeType(Enum):
    AM = auto()
    PM = auto()
    UNKNOWN = auto()


def parse_time(possible_time: str, tz: tzinfo) -> Optional[datetime]:
    if "am" in possible_time:
        time_type = TimeType.AM
    elif "pm" in possible_time:
        time_type = TimeType.PM
    else:
        time_type = TimeType.UNKNOWN

    time = remove_all(possible_time, ["at", "ish", " ", "am", "pm"])

    time_parts = time.split(":")
    if len(time_parts) == 1:
        hour, minute = int(time_parts[0]), 0
    elif len(time_parts) == 2:
        hour, minute = int(time_parts[0]), int(time_parts[1])
    else:
        # TODO: Not like this, not like this
        raise Exception("AHHH")

    if time_type == TimeType.PM:
        hour += 12

    # TODO: Handle leap seconds
    now = datetime.now(tz=tz)
    proposed_time = now.replace(hour=hour, minute=minute).astimezone(pytz.utc)
    time_skip_hrs = 12 if time_type == TimeType.UNKNOWN else 24
    while now > proposed_time:
        # Does this work lol? yes (also no, during dst changeovers)
        proposed_time = proposed_time + timedelta(hours=time_skip_hrs)

    return proposed_time


def remove_all(src: str, strs_to_remove: Iterator[str]):
    for to_remove in strs_to_remove:
        src = src.replace(to_remove, "")
    return src


def intersects(left: tuple[int, int], right: tuple[int, int]):
    return right[0] < left[0] < right[1] or right[0] < left[1] < right[1]


client.run(os.environ["DISCORD_API_KEY"])
