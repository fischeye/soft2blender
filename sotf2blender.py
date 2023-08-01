import sys
import os
import json
try:
    # This works only in a blender
    import bpy
except:
    # Script run without blender.
    # To analyse Data and stuff ...
    pass

# IMPORTANT
# =========
# ID can be found in this Directory: %userprofile%\AppData\LocalLow\Endnight\SonsOfTheForest\Saves\76561197964095990\Multiplayer
# This is the Name of the Directory where the Map is stored.
# Must be set to correct.

#saveGameID = "2066773530"
#saveGameID = "1537019340"
#saveGameID = "123456789"
#saveGameID = "1728018653"
saveGameID = "0472284868"

SOFTSettings = {
    "useSaveGameInScriptDir": False,
    "useSaveGameAbsolutePath": True,
    "saveGameAbsolutePath": "G:\Daten\Projects\soft2blender",
    "singlePlayer": True,
    "saveGameID": saveGameID
}


class SonOfTheForestToBlender:
    
    def __init__(self) -> None:
        self.mapLoaded = False
        self.blenderLoaded = False
        # check if this script run in Blender and module is loaded
        if "bpy" in sys.modules:
            self.blenderLoaded = True


    # ------------------------------------------------------------------------------
    # Public Methods


    # Initially call this Method to Load the Map Data from File
    def loadMap(self, settings):
        self.singlePlayerMode = settings["singlePlayer"]
        self.useSaveGameInScriptDir = settings["useSaveGameInScriptDir"]
        self.useSaveGameAbsolutePath = settings["useSaveGameAbsolutePath"]
        self.saveGameAbsolutePath = settings["saveGameAbsolutePath"]
        self.saveGameID = settings["saveGameID"]
        # Search for the Save Game Path
        pathSaveGame = self.__getSaveGamePath()
        if pathSaveGame == None:
            print("Savegame Path not found. Exit!")
            return False
        else:
            print("Found Savegame Path:", pathSaveGame)

        # Search for the Save Game Multiplayer Map
        mapData = self.__readSaveFile(pathSaveGame, saveGameID)
        if mapData == None:
            print("Savegame ID not found. Exit!")
            return False

        mapStructures = self.__getStructures(mapData)
        if mapStructures == None:
            print("No Data found in Savegame. Exit!")
            return False
        else:
            print(mapStructures)
        
        # store some data in class variables for later use
        self.mapData = mapData
        self.mapStructures = mapStructures
        self.saveGamePath = pathSaveGame
        # everythings loaded fine
        self.mapLoaded = True
        return True
    

    # save structures to JSON file if needed
    def extractStructes2JSON(self, fileName):
        if self.mapLoaded and not self.blenderLoaded:
            with open(fileName, 'w') as sf:
                json.dump(self.mapStructures, sf)


    # Read map Data to create a 3D Blender Map
    def createMap(self, limitObjects=0):
        # check if the map is loaded
        if self.mapLoaded:
            # Create a Blender Collection to create Objects in there
            self.__blenderCreateCollection()
            # Create all Materials
            self.__blenderCreateMaterials()
            # iterate through all structures
            createdItems = 0
            unusedItems = 0
            leaveLoop = False
            index = -1
            for itemList in self.mapStructures:
                index += 1
                subindex = -1
                if (itemList is not None and len(itemList) > 0):
                    for item in itemList:
                        subindex += 1
                        itemPos = self.__getPosition(item)
                        itemRot = self.__getRotation(item)
                        typeID = item["TypeID"]
                        if len(item['Elements']) == 0:
                            # Item without Elements ... who know's what that is?
                            unusedItems += 1
                            break
                        profileID = item['Elements'][0]['ProfileID']
                        print("Type {} - Profile {} - Pos: {:.2f},{:.2f},{:.2f}".format(typeID, profileID, itemPos['x'], itemPos['y'], itemPos['z']))
                        self.__blenderCreateObject(itemPos, itemRot, typeID, profileID, index, subindex)
                        createdItems += 1
                        if limitObjects > 0:
                            if createdItems == limitObjects:
                                leaveLoop = True
                                break
                else:
                    unusedItems += 1
                if leaveLoop:
                    break
            print("Created Items:", createdItems)
            print("Not used Items:", unusedItems)
        

    # ------------------------------------------------------------------------------
    # Private Methods

    def __getSaveGamePath(self):
        result = None
        if self.useSaveGameInScriptDir:
            # if the SaveGame is in the Script Dir
            thisFile = __file__
            if self.blenderLoaded:
                thisFile = bpy.data.filepath
            scriptDir = os.path.dirname(os.path.realpath(thisFile))
            if os.path.exists(scriptDir):
                result = scriptDir
        elif self.useSaveGameAbsolutePath:
            if os.path.exists(self.saveGameAbsolutePath):
                result = self.saveGameAbsolutePath
        else:
            # if the SaveGame is in the AppData Dir
            softDir = os.path.join(os.environ['userprofile'], "AppData", "LocalLow", "Endnight", "SonsOfTheForest", "Saves")
            if os.path.exists(softDir):
                softDirContent =  os.listdir(softDir)
                if (len(softDirContent) > 0):
                    # Pick the first Directory. I guess there is usually only one Directory
                    clientID = os.listdir(softDir)[0]
                    if self.singlePlayerMode:
                        saveGameDir = os.path.join(softDir, clientID, "SinglePlayer")
                    else:
                        saveGameDir = os.path.join(softDir, clientID, "Multiplayer")
                    if os.path.exists(saveGameDir):
                        result = saveGameDir
        return result


    def __readSaveFile(self, gamePath, mapID):
        result = None
        pathConstructions = os.path.join(gamePath, mapID, "ConstructionsSaveData.json")
        if (os.path.exists(pathConstructions)):
            with open(pathConstructions, 'r') as f:
                result = json.load(f)
        return result


    def __getStructures(self, mapData):
        dictConstructions = json.loads(mapData["Data"]["Constructions"])
        dictStructures = dictConstructions["Structures"]
        return dictStructures


    def __getPosition(self, data):
        result = {'x': 0, 'y': 0, 'z': 0}
        useElement = True
        if not useElement:
            if "Position" in data:
                x = data["Position"]["x"]
                y = data["Position"]["y"]
                z = data["Position"]["z"]
                # Scale Location down by factor 10 and cut precision {number.xx}
                result['x'] = float("{:.2f}".format(x / 10))
                result['y'] = float("{:.2f}".format(y / 10))
                result['z'] = float("{:.2f}".format(z / 10))
        else:
            if "Elements" in data:
                if len(data["Elements"]) > 0:
                    if "x" in data["Elements"][0]["Position"]:
                        result['x'] = data["Elements"][0]["Position"]["x"]
                    if "y" in data["Elements"][0]["Position"]:
                        result['y'] = data["Elements"][0]["Position"]["y"]
                    if "z" in data["Elements"][0]["Position"]:
                        result['z'] = data["Elements"][0]["Position"]["z"]
        return result


    def __getRotation(self, data):
        result = {'x': 0, 'y': 0, 'z': 0, 'w': 0.0}
        useElement = True
        if not useElement:
            if "Rotation" in data:
                if "x" in data["Rotation"]:
                    result['x'] = data["Rotation"]["x"]
                if "y" in data["Rotation"]:
                    result['y'] = data["Rotation"]["y"]
                if "z" in data["Rotation"]:
                    result['z'] = data["Rotation"]["z"]
                if "w" in data["Rotation"]:
                    result['w'] = data["Rotation"]["w"]
        else:
            if "Elements" in data:
                if len(data["Elements"]) > 0:
                    if "x" in data["Elements"][0]["Rotation"]:
                        result['x'] = data["Elements"][0]["Rotation"]["x"]
                    if "y" in data["Elements"][0]["Rotation"]:
                        result['y'] = data["Elements"][0]["Rotation"]["y"]
                    if "z" in data["Elements"][0]["Rotation"]:
                        result['z'] = data["Elements"][0]["Rotation"]["z"]
                    if "w" in data["Elements"][0]["Rotation"]:
                        result['w'] = data["Elements"][0]["Rotation"]["w"]
        return result


    # ------------------------------------------------------------------------------
    # Private Methods - Blender 3D specific


    # Create Blender Object from GameData
    def __blenderCreateObject(self, itemPos, itemRot, typeID, profileID, index, subindex):
        # Check if bpy Module is Loaded (if the Script run in Blender)
        if self.blenderLoaded:
            # Create the Object. Flip Y with Z Axis for Blender, cause its rotatet in the Game
            #bpy.ops.mesh.primitive_cube_add(location=(itemPos['x'], itemPos['y'], itemPos['z']))
            if profileID == 1:
                # Wood Log
                self.__blenderWoodLog()                
            else:
                self.__blenderUndefined()
            curObject = bpy.context.object
            # Move Object to his final Position
            bpy.ops.transform.translate(value=(itemPos['x'], itemPos['y'], itemPos['z']))
            # switch to EDIT Mode
            
            # apply new Size (length x,y,z)
            bpy.context.object.scale = (1, 1, 1)
            # apply Rotation. Flip also Y with Z
            #curObject.rotation_euler[0] = itemRot['x']
            #curObject.rotation_euler[1] = itemRot['z']
            #curObject.rotation_euler[2] = itemRot['y']
            curObject.rotation_mode = 'QUATERNION'
            curObject.rotation_quaternion = (itemRot['w'], itemRot['x'], itemRot['y'], itemRot['z'])
            # switch back to OBJECT Mode
            
            # remove Object of his Collection and put the Object into the new Collection
            for objCols in curObject.users_collection:
                objCols.objects.unlink(curObject)
            bpy.data.collections[saveGameID].objects.link(curObject)
            # rename Object
            bpy.context.object.name = "Obj-" + str(index) + "-" + str(subindex) + ".T" + str(typeID) + ".P" + str(profileID)
    
    def __blenderNewMaterial(self, name):
        # Check if bpy Module is Loaded (if the Script run in Blender)
        if self.blenderLoaded:
            bpy.data.materials.new(name)
            material = bpy.data.materials.get(name)
            material.use_nodes = True
            return material
    
    
    def __blenderCreateMaterials(self):
        # Check if bpy Module is Loaded (if the Script run in Blender)
        if self.blenderLoaded:
            newMaterial = self.__blenderNewMaterial("WoodLog")
            nodes = newMaterial.node_tree.nodes
            nodes["Principled BSDF"].inputs[0].default_value = (0.0420278, 0.00887743, 0.00520561, 1)
            newMaterial = self.__blenderNewMaterial("Undefined")
            nodes = newMaterial.node_tree.nodes
            nodes["Principled BSDF"].inputs[0].default_value = (0.634298, 0.0546605, 0.650006, 1)
    

    def __blenderWoodLog(self):
        # Check if bpy Module is Loaded (if the Script run in Blender)
        if self.blenderLoaded:
            bpy.ops.mesh.primitive_cylinder_add()
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.transform.resize(value=(0.25, 0.25, 1.1))
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.context.object.data.materials.append(bpy.data.materials.get("WoodLog"))
    
    
    def __blenderUndefined(self):
        # Check if bpy Module is Loaded (if the Script run in Blender)
        if self.blenderLoaded:
            bpy.ops.mesh.primitive_cube_add()
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.transform.resize(value=(0.125, 0.125, 0.125))
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.context.object.data.materials.append(bpy.data.materials.get("Undefined"))

    
    # Create Blender Collection with Name of SaveGameID
    def __blenderCreateCollection(self):
        # Check if bpy Module is Loaded (if the Script run in Blender)
        if self.blenderLoaded:
            if not self.saveGameID in bpy.data.collections:
                bpy.ops.collection.create(name=self.saveGameID)
                bpy.context.scene.collection.children.link(bpy.data.collections[self.saveGameID])


# ------------------------------------------------------------------------------
# Main Program


if __name__ == "__main__":
    SOFT = SonOfTheForestToBlender()
    # Load the Map
    if SOFT.loadMap(SOFTSettings):
        SOFT.extractStructes2JSON("structures.json")
        # Create the Map if its loaded successful
        SOFT.createMap(limitObjects=200)

