
# Sons of the Forest to Blender Script

## WORK IN PROGRESS

## General

This is mainly a python Script with can be used in Blender to load a SOFT Savegame and create Objects in Blender.

### Usage

Copy Paste the Script into a Blender Scripting File and run it.

IMPORTANT

Adjust Settings before you run!

Variable saveGameID need to be the Directory Name of the SaveGame in Single/Multiplayer Directory. 

Check here: %userprofile%\AppData\LocalLow\Endnight\SonsOfTheForest\Saves

Variable SOFTConverterSourcePath need to be the Path from this Project. (JSON, FBX Files are needed)

Check this Line:
SOFTReader.loadSaveGame() -> You can adjust this for Single/Multiplayer or different Path.

### Background Info

The Script consists of two classes. The Script is also designed to work without Blender. Just if you want to read the GameFiles for some statistics or something.

#### SOFTGameReader Class

This Class is just to find the game files and read the files.

#### SOFTGameBlender Class

This Class take the data of the Game files and create Blender Objects. Only if the Script run in Blender.