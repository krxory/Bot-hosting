# <editor-fold desc="Plugins">
import random
import discord
from discord import Member
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
from datetime import datetime, time, timedelta
import asyncio
from discord.ui import View, Button
import json
import pytz
from urllib.parse import urlparse
# </editor-fold>


# <editor-fold desc="Things">

with open("clips.json", "r") as f:
    data = json.load(f)

with open("current_vote.json","r") as v:
    dataVote=json.load(v)

################# --- Modules
timezone = pytz.timezone("US/Eastern")

load_dotenv()
token=os.getenv('DISCORD_TOKEN')
channel_id=1418726969092346031

################

handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
intents= discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)
# </editor-fold>

# <editor-fold desc="Helping Things">
ranks = ["bronze", 'silver', 'gold', 'plat', 'platinum', 'diamond', 'champ', 'champion', 'gc', 'grandchamp',
         'grandchampion', 'ssl', 'supersoniclegend']
RANK_VALUES = {
    "ssl": 8, "gc": 7, "champ": 6, "diamond": 5,
    "plat": 4, "gold": 3, "silver": 2, "bronze": 1
}
top_10 = "N/A"

class ManageClips:  #load clips, save clips, get next clip, add clip, approve clip, decline clip
    def __init__(self):
        self.clips_file = "clips.json"  # fixed
        try:
            with open(self.clips_file, "r") as f:
                data = json.load(f)
                self.clips = data.get("clips", [])
        except FileNotFoundError:
            self.clips = []

    def check_clip(self,link,rank):

        if rank not in ranks:
            return True
        for clip in self.clips:
            if clip["clip"] == link:
                return True
            else:
                pass


clip_manager =ManageClips()

def is_valid_url(url):
    link_check = "https://"
    if link_check not in url:
        return False
    return True


def calculate_votes(reveal_rank):
    global top_10

    # --- Load leaderboard ---
    if os.path.exists("leaderboard.json"):
        with open("leaderboard.json", "r") as f:
            try:
                data_leader = json.load(f)
                leader_list = data_leader.get("leaderboard", [])
            except json.JSONDecodeError:
                leader_list = []
    else:
        leader_list = []

    # --- Load streaks ---
    if os.path.exists("streak.json"):
        with open("streak.json", "r") as f:
            try:
                data_streak = json.load(f)
                streak_list = data_streak.get("streaks", [])
            except json.JSONDecodeError:
                streak_list = []
    else:
        streak_list = []

    # --- Validate rank ---
    reveal_rank_value = RANK_VALUES.get(reveal_rank, None)
    if reveal_rank_value is None:
        print("Not a valid rank score")
        return

    voted_names = set()
    # --- Process votes ---
    for vote in dataVote["votes"]:
        name = vote["name"]
        voted_names.add(name)

        if vote["vote"] == reveal_rank_value:
            # ✅ Correct guess
            for entry in streak_list:
                if entry["name"] == name:
                    entry["streak"] += 1
                    break
            else:
                streak_list.append({"name": name, "streak": 1})

            for entry in leader_list:
                if entry["name"] == name:
                    entry["points"] += 1
                    break
            else:
                leader_list.append({"name": name, "points": 1})
        else:
            # ❌ Wrong guess → remove streak completely
            streak_list = [entry for entry in streak_list if entry["name"] != name]

    # --- Handle no-vote users (remove their streaks) ---
    streak_list = [entry for entry in streak_list if entry["name"] in voted_names]

    # --- Sort leaderboard ---
    sorted_leaderboard = sorted(
        leader_list,
        key=lambda x: x["points"],
        reverse=True
    )

    # --- Wrap for saving ---
    streak_list = {"streaks": streak_list}
    leader_list = {"leaderboard": sorted_leaderboard}

    # --- Save back to files ---
    with open("leaderboard.json", "w") as f:
        json.dump(leader_list, f, indent=2)

    with open("streak.json", "w") as t:
        json.dump(streak_list, t, indent=2)


def get_streak(name):
    if os.path.exists("streak.json"):
        with open("streak.json", "r") as f:
            try:
                data_streak = json.load(f)
                streak_list = data_streak["streaks"]
            except json.JSONDecodeError:
                streak_list = []  # reset if file corrupted
    else:
        streak_list = []
    for entry in streak_list:
        if entry["name"] == name:
            user_streak = f"Your streak is {entry['streak']}"
        else:
            user_streak="Your streak is 0"
        return user_streak


@bot.command()
async def leaderboard(ctx):
    if ctx.channel.id == 1418753429693661234:
        name = str(ctx.author.name)  # user's name as string

        if not os.path.exists("leaderboard.json"):
            await ctx.send("No leaderboard yet.")
            return

    with open("leaderboard.json", "r") as f:
        try:
            data = json.load(f)
            full_leaderboard = data.get("leaderboard", [])
        except json.JSONDecodeError:
            await ctx.send("Leaderboard file is corrupted.")
            return

    if not full_leaderboard:
        await ctx.send("No leaderboard yet.")
        return

    # Sort full leaderboard by points descending
    full_leaderboard_sorted = sorted(full_leaderboard, key=lambda x: x["points"], reverse=True)

    # Build top 10 message
    top_10 = full_leaderboard_sorted[:10]
    msg = "\n".join([f"{i+1}. {entry['name']} - {entry['points']} points"
                     for i, entry in enumerate(top_10)])

    # Find user's rank and points
    user_rank = next((i+1 for i, entry in enumerate(full_leaderboard_sorted) if entry["name"] == name), None)
    if user_rank:
        user_points = next(entry["points"] for entry in full_leaderboard_sorted if entry["name"] == name)
        # Append user's rank
        msg += f"\n\nYour rank: #{user_rank} - {name} - {user_points} points"
    else:
        msg += f"\n\nYou are not on the leaderboard yet."

    await ctx.send("**Top 10 Leaderboard:**\n" + msg, )


@bot.command()
async def streak(ctx):
    if ctx.channel.id == 1418753429693661234:
        name = ctx.author.name
        user_streak=str(get_streak(name))
        print("yes")
        await ctx.send(user_streak)
    else:
        print("No")


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.command()
async def submit(ctx, link: str, *, rank: str):
    # delete user's message to keep channel clean
    if ctx.channel.id == 1418753537176899606:
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass

        rank = rank.lower().replace(" ", "")
        valid_url = is_valid_url(link)
        if any(clip["clip"] == link for clip in data["clips"]):
            await ctx.author.send("Clip already in database")
            return
        if rank not in ranks:
            await ctx.author.send("Not a valid rank")
            return
        if valid_url:
            clip_manager.check_clip(link, rank)
            user = ctx.author

            # create a private thread in this channel
            thread = await ctx.channel.create_thread(
                name=f"{user}'s clip verification | Rank = {rank}",
                type=discord.ChannelType.private_thread,
                auto_archive_duration=60,
                invitable=False
            )

            # add the submitter to the thread
            await thread.add_user(user)

            # add all users with the Moderator role
            moderator_role = discord.utils.get(ctx.guild.roles, name="moderator")

            if moderator_role is not None:
                # loop through all members in the guild and check role
                for member in ctx.guild.members:
                    if moderator_role in member.roles:
                        await thread.add_user(member)

            # send the submission in the private thread
            await thread.send(f"{user}'s clip verification | Clip = {link} | Rank = {rank}")

            print("Complete")
        else:
            # notify the user privately if the link is invalid
            try:
                await ctx.author.send(" Not a valid link")
            except discord.Forbidden:
                await ctx.send(" Not a valid link", delete_after=5)

@bot.event
async def on_message(message):
    # ignore bot messages
    if message.author.bot:
        return

    # only watch the target channel
    if message.channel.id == 1418753537176899606:
        # check if the message starts with your command prefix
        if message.content.startswith("!submit") and len(message.content)>=8:
            # let the command system handle it
            await bot.process_commands(message)
        else:
            # delete everything else
            try:
                await message.delete()
            except discord.Forbidden:
                pass
        return
    if message.channel.id == 1418753429693661234:
        if message.content.startswith("!submit"):
            try:
                await message.delete()
            except discord.Forbidden:
                pass
    if message.channel.id == 1418726969092346031:
            try:
                await message.delete()
            except discord.Forbidden:
                pass

    # for other channels, normal behavior
    await bot.process_commands(message)



#Command to Approve or decline clip
@bot.command()
@commands.has_role("Moderator")
async def check(ctx, link:str, rank:str, * ,decision:str):
    username = ctx.author.name
    rank = rank.lower().replace(" ", "")

    decision=decision.lower().strip().replace(" ","")
    valid_url = is_valid_url(link)
    if not valid_url:
        await ctx.send("Not a valid URL")
    if rank not in ranks:
        await ctx.send("Not a valid rank! Please input a rank from Bronze-SSL, no numbers.")
        return
    if decision not in ("y",'n'):
        await ctx.send("Please include either y or n at the end of your message to complete this command.")
        return
    if decision == 'y':
        await ctx.send("Approved")
        new_clip = {
            "name": username,
            "clip": link,
            "rank": rank
        }
        if not any(clip["clip"] == new_clip["clip"] for clip in data["clips"]):
            data["clips"].append(new_clip)
        else:
            await ctx.send("Clip already in database")
            print(data["clips"])

        with open("clips.json",'w') as f:
            json.dump(data,f,indent=4)
    elif decision == 'n':
        await ctx.send("Declined")

#sets the timer if conditions are met




async def clip_timer():
    await bot.wait_until_ready()
    channel = bot.get_channel(channel_id)
    if not channel:
        print("Channel not found")
        return
    while not bot.is_closed():
        with open("current_past_clips.json", "r") as f:
            cp_clips = json.load(f)
        if data.get("clips"):  # Use the top-level data
            if cp_clips["to_post"] == []:
                index = random.randint(0, len(data["clips"]) - 1)
                clip_dict = data["clips"][index]
                clip_url = clip_dict["clip"]
                clip_rank = clip_dict["rank"]
                clip_to_post = {"post_link": clip_url, "post_rank": clip_rank}
                clip_to_reveal = {"reveal_link": clip_url, "reveal_rank": clip_rank}
                # Remove from top-level data
                del data["clips"][index]
                print("deleted")
                # Write back to clips.json immediately
                with open("clips.json", "w") as f:
                    json.dump(data, f, indent=2)
                cp_clips["to_post"].append(clip_to_post)
                print("append to post")
                with open("current_past_clips.json","w") as f:
                    json.dump(cp_clips,f,indent=2)
            else:
                print("Skipped the clip appending and deletion, good if clips in cp clips")
                clip_url = cp_clips["to_post"][0]["post_link"]
                clip_rank = cp_clips["to_post"][0]["post_rank"]
                clip_to_post = {"post_link": clip_url, "post_rank": clip_rank}
                clip_to_reveal = {"reveal_link": clip_url, "reveal_rank": clip_rank}
                pass
        now=datetime.now(timezone)
        vote_target = now.replace(hour=22, minute=15, second=0, microsecond=0)
        reveal_target = now.replace(hour=22, minute=13, second=0, microsecond=0)
        if now >= reveal_target or not cp_clips["to_reveal"]:
            reveal_target+= timedelta(days=1)
        if now >= vote_target:
            vote_target+= timedelta(days=1)
        vote_seconds = (vote_target - now).total_seconds()
        reveal_seconds = (reveal_target - now).total_seconds()
        if cp_clips.get("to_reveal"):
            print("Thinks that cp_clips to reveal has data")
            reveal_link = cp_clips["to_reveal"][0]["reveal_link"]
            reveal_rank = cp_clips["to_reveal"][0]["reveal_rank"]
            await asyncio.sleep(reveal_seconds)
            await reveal(reveal_rank,reveal_link,cp_clips)
            await asyncio.sleep(vote_seconds)
            await vote(cp_clips,clip_url,clip_to_reveal,clip_to_post)
        else:
            await asyncio.sleep(vote_seconds)
            await vote(cp_clips,clip_url,clip_to_reveal,clip_to_post)

#starts the timer
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    bot.loop.create_task(clip_timer())

class VideoVote(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        for label, value in RANK_VALUES.items():
            self.add_item(RankButton(label, value))

class RankButton(discord.ui.Button):
    def __init__(self, label, value):
        super().__init__(label=label, style=discord.ButtonStyle.primary)
        self.value = value

    async def callback(self, interaction: discord.Interaction):
        user_vote = {"name": interaction.user.name, "vote": self.value}
        updated = FindName(interaction.user.name, self.value)

        if not updated:
            dataVote["votes"].append(user_vote)
            with open("current_vote.json", "w") as fv:
                json.dump(dataVote, fv, indent=4)

        await interaction.response.send_message(
            f"You picked {self.label}", ephemeral=True
        )


async def reveal(reveal_rank,reveal_link,cp_clips):
    channel = bot.get_channel(channel_id)
    calculate_votes(reveal_rank)
    await channel.send(f"{reveal_link} The correct rank for yesterdays clip was {reveal_rank}")
    cp_clips["to_reveal"].clear()
    dataVote["votes"].clear()
    with open("current_vote.json","w") as wf:
        json.dump(dataVote,wf,indent=2)
    with open("current_past_clips.json", "w") as wp:
        json.dump(cp_clips,wp,indent=2)

async def vote(cp_clips,clip_url,clip_to_reveal,clip_to_post):
    channel = bot.get_channel(channel_id)
    print("At vote")
    await channel.send(clip_url, view=VideoVote())
    cp_clips["to_reveal"].append(clip_to_reveal)
    cp_clips["to_post"].remove(clip_to_post)
    with open("current_past_clips.json","w") as cp:
        json.dump(cp_clips, cp, indent=2)


# </editor-fold>

def FindName(voterusername,userpick):
    for entry in dataVote["votes"]:
        if entry["name"] == voterusername:
            entry["vote"] = userpick
            with open("current_vote.json", 'w') as fv:
                json.dump(dataVote, fv, indent=4)
            return True
    return False




bot.run(token,log_handler=handler,log_level=logging.DEBUG)