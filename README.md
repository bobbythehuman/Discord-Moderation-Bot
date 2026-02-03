# Discord Moderation Bot 🔧

**An Advance Discord moderation bot** built with discord.py and discord-py-slash-command. It provides automatic profanity detection, warnings, temporary mutes, and configurable server settings stored in an SQLite database.

---

## 🚀 Features

- Automatic bad-word detection (configurable word lists, letter substitutions, and separators)
- Warning system with time-based checks
- Automatic temporary mutes after configurable warning threshold
- Manual mute command (`/Temp_Mute`)
- Add/remove report channels, admin roles, blocked words, letters, and separators
- Slash commands for all actions
- Stores server data and history in `guild_data.db` (SQLite)


## ⚙️ Requirements

- Python 3.8+
- `discord.py == 1.7.3`
- `discord-py-slash-command == 3.0.3`


## Configuration

Edit `Main.py` before running:

- Set your bot token any way you prefer:

```py
TOKEN = 'YOUR_BOT_TOKEN_HERE'
```

- (Optional) Limit slash command registration to specific guilds during testing by adding their IDs to `PRIVATE_GUILD_IDS`:

```py
PRIVATE_GUILD_IDS: List[int] = [123456789012345678]
```

Permissions the bot should have in server (recommended):
- Manage Roles (to create/apply the `Muted` role)
- Manage Channels (to set channel overwrites if needed)
- Send Messages, Read Messages/View Channels, Read Message History, Embed Links

---

## Detection Logic
The bot detects bad words in messages by searching for them based on configured letter substitutions and separators. 

An example, for the word 'cat':

Substitutions:
``` py
self.letters = {
            "c": ["c", "C", "(", "k"],
            "a": ["a", "A", "&", "@"],
            "t": ["t", "T", "7"]
}
```

Separators:
``` py
self.seperate: = [".", ","]
```

It will use regular expressions to match variations of the word with substitutions and separators interspersed.

``` py
[.,]*[cC(]+[.,]*[aA&@]+[.,]*[tT7]+[.,]*
```

This will match messages like:
- c.a.t
- C@T
- (a,t
- c,a.t
- c@.t

There will be false positives/negatives depending on the substitutions and separators configured. 
It will detect situations where the word is in another word (e.g. "catalog").<br>
In practice, it works reasonably well for common obfuscations. 

## Database

The database is created seperately to the main program. Creating the database involves running `create.py` and ensuring the `guild_data.db` file is in the same directory as `Main.py`.

The bot uses `guild_data.db` to persist settings and warnings. Major tables (used in code):

- `server` — per-server configuration
- `word_list` — banned words
- `letters_list` — character substitutions
- `separator_list` — punctuation used as separators
- `user_list` — tracked users
- `warning_list` — individual warnings

The DB file is created automatically on first run.

---

## Commands Reference

| Command | Description | Options |
|---|---:|---|
| `/ping` | Display bot latency | — |
| `/server` | Show server info | — |
| `/Sync_Commands` | Sync slash commands | — |
| `/Help` | Show help menu | — |
| `/Warn` | Warn a user | `user` (required), `reason` (optional) |
| `/Warnings` | Show a user's warnings | `user` (optional) |
| `/Report_Channel` | Add/remove report channel | `option` (add/remove), `channel` |
| `/Display_Channels` | List report channels | — |
| `/Required_Role` | Add/remove admin role | `option`, `role` |
| `/Display_Roles` | List admin roles | — |
| `/New_Word` | Add/remove blocked word | `option`, `word` |
| `/Display_Words` | Show blocked words | — |
| `/New_Letter` | Add/remove letter substitution | `option`, `letter`, `char` |
| `/Display_Letters` | Show substitutions | `letter` (optional) |
| `/New_Seperator` | Add/remove separators | `option`, `seperator` |
| `/Display_Seperators` | List separators | — |
| `/Mute_Info` | Info about muting settings | — |
| `/Default_Mute` | Set default mute duration | `time` (eg. `30m20s`) |
| `/Warning_Count` | Set number of warnings before mute | `count` |
| `/Time_Frame` | Set timeframe for warning check | `time` (eg. `30m20s`) |
| `/Temp_Mute` | Temporarily mute a member | `member`, `duration`, `reason` (optional) |

> Example: `/Warn user:@someone reason:Spam`

---

## ⏱ Time Format

Times are parsed by the bot using suffixes: `w` (weeks), `d` (days), `h` (hours), `m` (minutes), `s` (seconds). e.g. `30m20s`.

---

## 🧰 Implementation Notes

- The bot auto-creates a `Muted` role if it doesn't exist and updates channel permissions to prevent sending messages.
- Warning checks compare timestamps to decide if a user should be muted automatically according to server settings.

---

## Contributing

Contributions are welcome. Please open issues or PRs to discuss changes. Note this project is not actively maintained.

---

## License

This project is licensed under the GNU Affero General Public License v3.0 (AGPLv3). See the `LICENSE` file for full terms.

---

<!-- ## Contact

For questions or copyright inquiries, contact: https://github.com/bobbythehuman  -->

<!-- --- -->
