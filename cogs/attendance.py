import discord
from discord.ext import commands, tasks
from discord import app_commands
from datetime import datetime, timedelta

class Attendance(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.linked_channels = {}
        self.linked_vcs = set()
        self.attendance_times = {}
        self.cool_times = {}
        self.join_times = {}
        self.pinged = set()

    @app_commands.command(name="add_channel", description="Link a text channel to send attendance messages")
    async def add_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        self.linked_channels[interaction.guild_id] = channel.id
        await interaction.response.send_message(f"Attendance messages will be sent in {channel.mention}", ephemeral=True)

    @app_commands.command(name="link_vc", description="Link a VC to enable attendance tracking")
    async def link_vc(self, interaction: discord.Interaction, vc: discord.VoiceChannel):
        self.linked_vcs.add(vc.id)
        await interaction.response.send_message(f"Voice channel {vc.name} linked for attendance", ephemeral=True)

    @app_commands.command(name="set_attendance_time", description="Set how long a user can stay before being pinged for attendance")
    async def set_attendance_time(self, interaction: discord.Interaction, minutes: int):
        self.attendance_times[interaction.guild_id] = timedelta(minutes=minutes)
        await interaction.response.send_message(f"Attendance time set to {minutes} minutes", ephemeral=True)

    @app_commands.command(name="set_cooltime", description="Set how long to wait after ping before disconnecting")
    async def set_cooltime(self, interaction: discord.Interaction, minutes: int):
        self.cool_times[interaction.guild_id] = timedelta(minutes=minutes)
        await interaction.response.send_message(f"Cool time set to {minutes} minutes", ephemeral=True)

    @app_commands.command(name="present", description="Mark yourself present")
    async def present(self, interaction: discord.Interaction):
        user = interaction.user
        self.join_times[user.id] = datetime.utcnow()
        self.pinged.discard(user.id)
        await interaction.response.send_message("✅ Thank you for marking your attendance!", ephemeral=True)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if after.channel and after.channel.id in self.linked_vcs:
            self.join_times[member.id] = datetime.utcnow()
            guild_channel_id = self.linked_channels.get(member.guild.id)
            if guild_channel_id:
                channel = member.guild.get_channel(guild_channel_id)
                await channel.send(f"{member.mention} has joined VC. Please mark your attendance within the set time using `/present`.")

    @tasks.loop(seconds=30)
    async def check_attendance(self):
        now = datetime.utcnow()
        for user_id, join_time in list(self.join_times.items()):
            for guild in self.bot.guilds:
                guild_channel_id = self.linked_channels.get(guild.id)
                if guild_channel_id:
                    member = guild.get_member(user_id)
                    if member and member.voice and member.voice.channel and member.voice.channel.id in self.linked_vcs:
                        delta = now - join_time
                        att_time = self.attendance_times.get(guild.id, timedelta(minutes=120))
                        cool_time = self.cool_times.get(guild.id, timedelta(minutes=5))
                        if delta > att_time and user_id not in self.pinged:
                            self.pinged.add(user_id)
                            await guild.get_channel(guild_channel_id).send(f"{member.mention}, please mark your attendance using `/present`.")
                            self.join_times[user_id] = now - att_time + cool_time
                        elif delta > att_time + cool_time:
                            await member.move_to(None)
                            await guild.get_channel(guild_channel_id).send(f"{member.mention} was disconnected due to no attendance.")

    @commands.Cog.listener()
    async def on_ready(self):
        self.check_attendance.start()

async def setup(bot):
    await bot.add_cog(Attendance(bot))
