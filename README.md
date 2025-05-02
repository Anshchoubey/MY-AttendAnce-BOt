# AB Attendance Bot

## Setup Instructions

1. Install dependencies:
```bash
pip install discord.py python-dotenv
```

2. Create a `.env` file in the root directory and add your bot token:
```
DISCORD_TOKEN=your_token_here
```

3. Run the bot:
```bash
python main.py
```

4. Use the following commands inside Discord after inviting the bot:
- `/add_channel` to set the text channel for attendance messages.
- `/link_vc` to link a VC for attendance tracking.
- `/set_attendance_time` to set how long someone can be in VC before needing to check-in.
- `/set_cooltime` to set how long after ping a user has to mark attendance before being disconnected.
- `/present` to mark attendance manually.
