# gad-tools
Selections from my personal collection of tools I've cobbled together over the years.

# Selected descriptions

Tool name: gad-scummvm-deploy

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

