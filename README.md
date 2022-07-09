# GalaxyBot
#### Video Demo:  https://youtu.be/fqEE2qg33a0
#### Description:

This is a Discord bot designed to provide custom built functionality to the Galaxy Gaming Group server.

#### File Descriptions:

###### app.py

File contains the main application logic such as:  
- Loads the configuration to provide the discord token 
- Creates discord bot object with all intents

###### db.py

File contains database logic such as:
- Loads the configuration to provide database connection string
- creates birthdays table in database with Birthday Schema (Uses SqlAlchemy)
- Maintains a sessionmaker used to access database

###### music_player.py:

File contains music player logic such as:

- MusicPlayer class that tracks current song, queue, voice client, text channel, bot, and if player is stopped

###### cogs/birthday_commands.py:

File contains the cog for birthday commmands such as:

- /add_birthday {month} {day} - Adds the month/day birthday for the current user
- /remove_birthday - Removes the birthday for the current user
- /check_birthday - Displays the birthday for the current user

###### cogs/info_commands.py:

File contains the cog for information commands such as:
- /server - Pulls information about the current server such as server name, owner name, created date, online member count, and total member count
- /info {User} - Pulls information about the user provided (or the current user if none provided) such as name, created date, joined date, roles, and status

###### cogs/music_commands.py:

File contains the cog for msuic commands such as:

- /play {query} - Looks up the url if one is provided or searches for the song name and adds it to the player
- /stop - Stops the music player
- /skip - Skips the current playing song
- /list - Lists the current song queue in the music player
- /leave - Makes the bot leave the voice channel

###### logic/birthday.py

File contains utilities to support birthday commands such as:

- daily_birthday_jobs - Task that tracks and starts daily database cleanup and birthday messages
- set_run_time - Sets the next runtime for the daily birthday jobs
- database_cleanup - searches the database for stale birthdays that belong to users no longer in the server
- birthday_message - searches for birthdays for todays date and announces them to the server

###### logic/embed.py

File contains utilities to support embed building such as:

- error_embed - Builds embed with default configuration for error messages
- embed - Builds embed with default configuration for generic messages
- music_embed - Builds embed with default configuration for music messages
