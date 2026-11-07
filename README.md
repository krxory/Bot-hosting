# Daily Rank Guess: Rocket League Discord Bot

A Discord bot built for a seed-funded startup's community server. Every day it posts a Rocket League clip, members guess the player's rank, and the next day the bot reveals the answer and awards points. Submitted clips go through a moderator approval workflow before entering the pool. At its peak about 30 members took part daily.

> **Status:** Archived. The startup has shut down and the bot is no longer running. This repo is published with the permission of the project's admin.

## How it works

1. **Submit:** a member runs `!submit <clip link> <rank>` in the submissions channel. The bot deletes their message to keep the channel clean, validates the link and rank, rejects duplicates, and opens a **private thread** containing the submitter and all moderators.
2. **Approve:** a moderator reviews the clip in the thread and runs `!check <link> <rank> y|n`. Approved clips are added to the pool.
3. **Daily post:** at a scheduled time (10:15 PM Eastern) the bot picks a random clip from the pool and posts it with a row of rank buttons (Bronze through SSL). Members can change their vote until the reveal.
4. **Reveal:** the next day (10:13 PM Eastern) the bot reveals the clip's real rank, scores everyone's votes, and updates the leaderboard and streaks.
5. **Compete:** `!leaderboard` shows the top 10 plus the caller's rank. `!streak` shows their current streak of correct guesses. A wrong guess resets the streak.

## Features

- Moderator approval workflow using private threads and role-based permissions
- Input validation and edge-case handling: invalid URLs, invalid ranks, duplicate clips, DMs when a user's submission is rejected, closed DMs, and missing permissions
- Channel-level message cleanup, so command channels stay tidy
- Interactive rank-voting buttons (`discord.ui`) with changeable votes
- Scheduled daily post and reveal loop with Eastern-time handling (`pytz`)
- Persistent JSON storage for the clip pool, votes, leaderboard, and streaks, with the current post and reveal state saved so the bot resumes after a restart

## Tech stack

- Python
- discord.py (commands, UI components, threads)
- `asyncio` for scheduling, `pytz` for time zones, `python-dotenv` for config
- JSON files for storage

## Project structure

```
.
├── main.py                    # bot: commands, voting UI, scheduler, scoring
├── clips.json                 # approved clip pool            {"clips": []}
├── current_vote.json          # today's votes                 {"votes": []}
├── current_past_clips.json    # post/reveal state             {"to_post": [], "to_reveal": []}
├── leaderboard.json           # created automatically
├── streak.json                # created automatically
├── requirements.txt
└── .env                       # DISCORD_TOKEN=... (not committed)
```

The three data files with starter contents shown above must exist before the bot starts. `leaderboard.json` and `streak.json` are generated the first time votes are scored.

## Running it locally

1. Clone the repo and install dependencies:
   ```bash
   git clone https://github.com/krxory/[repo-name].git
   cd [repo-name]
   python -m venv venv && source venv/bin/activate
   pip install -r requirements.txt
   ```
2. Create a bot in the [Discord Developer Portal](https://discord.com/developers/applications), enable the **Message Content** and **Server Members** intents, and copy its token.
3. Create a `.env` file:
   ```
   DISCORD_TOKEN=your_token_here
   ```
4. Create the starter JSON files shown above.
5. In `main.py`, replace the hard-coded channel IDs with your own channels (submissions, leaderboard/streak, and daily-post channels), and create a `Moderator` role in your server.
6. Run it:
   ```bash
   python main.py
   ```

## Known limitations

This was built for a small community and was my first real project, if I were to change some code it would be the following:

- Channel IDs are hard-coded. They should live in a config file or environment variables.
- State is stored in JSON files, which works at this scale but isn't safe for concurrent writes. A database (SQLite) would be the next step.
- Everything is in one file. Splitting into cogs would make it easier to maintain.

## What I learned

- Shipping a bot that real users relied on daily
- Designing approval flows and handling the edge cases real users create
- Async scheduling, Discord UI components, and persisting state across restarts

## Author

Gregory Sabo ([@krxory](https://github.com/krxory))
