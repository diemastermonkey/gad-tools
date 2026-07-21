# gad-tools
Selections from my personal collection of tools I've cobbled together over the years.

# Selected descriptions

# gad-scummvm-deploy

Arguments:
  Arg 1: Game Title (mandatory)
  Arg 2: Manual game name for .scummvm file (optional)

What:

User provides a game 'title' in the form (for example): Codename Iceman

Why:

The point-and-click adventure engine "ScummVM" requires certain meta files and other conformance to properly handle ScummVM games, and it's very specific to each game. The details are esoteric, and stored in a lookup file. So this script helps, by:

1. Accepts the title of a compressed game to be found in a local .zip, .rar, or .7z file (as typically shipped in the community)
2. Locates the game in the 'meta data' file 'GAD_RetroBat_ScummVM_Tag_List.csv'. If there are multiple matches, it prompts the user to select.
3. Creates the appropriately named directory and meta data file (.scummvm)

This really helps front-ends like "RetroBat" as well, which need to know how to list the game title.
It also performs various sanity checks, normalizing directory depth, fuzzy title matching, etc.

Example run: 

$ python3 gad-scummvm-deploy.py 'Last Crusade'
--- Deploying: Last Crusade ---

Multiple file matches found:
1. Indiana Jones and the Last Crusade (Floppy DOS VGA).zip
2. Indiana Jones and the Last Crusade.rar
3. Exit

Select a file (1-3): 2

Multiple tag matches found:
1. Games, Games, Games: Maniac Mansion + Zak McKracken + Indiana Jones and the last Crusade -> scumm:indyzak
2. Indiana Jones and the Last Crusade & Loom -> scumm:indyloom
3. Indiana Jones and the Last Crusade: The Graphic Adventure -> scumm:indy3
4. Passport to Adventure (Indiana Jones and the Last Crusade, The Secret of Monkey Island, Loom) -> scumm:pass
5. Exit

Select a tag (1-5): 3

--- Planned Actions ---
- CREATE DIRECTORY: Last Crusade
- EXTRACT: Indiana Jones and the Last Crusade.rar -> Last Crusade
- CREATE FILE: Last Crusade/Last Crusade.scummvm (Content: "scumm:indy3")

Proceed with deployment? [Y/n]: y

Executing...

Extracting from /mnt/d/Emulation_Roms/ScummVM/Indiana Jones and the Last Crusade.rar
(...)
All OK

--- Deployment Complete ---
New directory created: Last Crusade

# Other Tools...
