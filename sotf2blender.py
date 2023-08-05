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


# ------------------------------------------------------------------------------
# Blender Helper Class

class SOFTGameReader:

    def __init__(self):
        self.mapLoaded = False

    def loadSaveGame(self, saveGameID, singlePlayer=False, customPath=None):
        result = False
        # Find the SaveGamePath
        saveGamePath = self.__getSaveGamePath(saveGameID, singlePlayer, customPath)
        if not saveGamePath == None:
            # Read the JSON
            mapData = self.__readSaveFile(saveGamePath)
            if not mapData == None:
                self.mapStructures = self.__getStructures(mapData)
                self.mapLoaded = True
                result = True
        return result
    

    def getConstructionCategories(self):
        result = None
        if self.mapLoaded:
            result = []
            for index in range(len(self.mapStructures)):
                if not self.mapStructures[index] == None:
                    if len(self.mapStructures[index]) > 0:
                        result.append(index)
        return result


    def getConstructionCategoryByID(self, ID):
        return self.mapStructures[ID]
    

    def getStructure(self, structureData):
        result = None
        if len(structureData["Elements"]) > 0:
            print("Reader: Process Structure")
            typeID = structureData["TypeID"]
            positionGlobal = structureData["Position"]
            rotationGlobal = structureData["Rotation"]
            elements = structureData["Elements"]
            result = [typeID, positionGlobal, rotationGlobal, elements]
        return result


    def getElement(self, elementData):
        print("Reader: Process Element")
        profileID = elementData["ProfileID"]
        position = elementData["Position"]
        rotation = elementData["Rotation"]
        lengthScale = elementData["LengthScale"]
        return [profileID, position, rotation, lengthScale]


    # ------------------------------------------------------------------------------
    # Private Methods


    # Read and return the JSON File
    def __readSaveFile(self, path):
        result = None
        pathConstructions = os.path.join(path, "ConstructionsSaveData.json")
        print("Use JSON:", pathConstructions)
        if (os.path.exists(pathConstructions)):
            with open(pathConstructions, 'r') as f:
                result = json.load(f)
        return result
    

    # Extract and return Structures form the MapData
    def __getStructures(self, mapData):
        dictConstructions = json.loads(mapData["Data"]["Constructions"])
        dictStructures = dictConstructions["Structures"]
        return dictStructures
    

    # Find and return the SaveGame Directory
    def __getSaveGamePath(self, saveGameID, singlePlayer=False, customPath=None):
        result = None
        playerMode = "Multiplayer"
        if singlePlayer:
            playerMode = "SinglePlayer"
        if customPath == None:
            # Look in the standard Game Directory in the Userprofile
            softDir = os.path.join(os.environ['userprofile'], "AppData", "LocalLow", "Endnight", "SonsOfTheForest", "Saves")
            if os.path.exists(softDir):
                softDirContent =  os.listdir(softDir)
                if (len(softDirContent) > 0):
                    # Pick the first Directory. I guess there is usually only one Directory
                    clientID = os.listdir(softDir)[0]
                    saveGameDir = os.path.join(softDir, clientID, playerMode, saveGameID)
                    if os.path.exists(saveGameDir):
                        result = saveGameDir
        else:
            # Use a CustomPath for the GameFiles
            if os.path.exists(customPath):
                saveGameDir = os.path.join(customPath, saveGameID)
                if os.path.exists(saveGameDir):
                    result = saveGameDir
        return result



# ------------------------------------------------------------------------------
# Blender Helper Class

class SOFTGameBlender:

    def __init__(self, gameID, gameDefinitions):
        self.gameID = gameID
        self.blenderLoaded = False
        # check if this script run in Blender and module is loaded
        # script will run in plain python as well, without creating blender objects
        if "bpy" in sys.modules:
            self.blenderLoaded = True
            #gameDefinitions = json.load(open("soft2blender.json", "r"))
            self.objectDefs = gameDefinitions["ObjectDefinition"]
            self.materialDefs = gameDefinitions["ObjectMaterials"]
    
    def createCollection(self):
        if self.blenderLoaded:
            print("Blender: Create Collection")
            if not self.gameID in bpy.data.collections:
                bpy.ops.collection.create(name=self.gameID)
                bpy.context.scene.collection.children.link(bpy.data.collections[self.gameID])
        
    def createMaterials(self):
        if self.blenderLoaded:
            print("Blender: Create Material")
            for materialName in self.materialDefs:
                bpy.data.materials.new(materialName)
                bpy.data.materials.get(materialName).use_nodes = True
                nodes = bpy.data.materials.get(materialName).node_tree.nodes
                nodes["Principled BSDF"].inputs[0].default_value = self.materialDefs[materialName]

    def createObject(self, name, profileID, position, rotation):
        if self.blenderLoaded:
            if str(profileID) in self.objectDefs:
                thisDef = self.objectDefs[str(profileID)]
                print("Blender: Create Object")
                if thisDef["type"] == "cube":
                    bpy.ops.mesh.primitive_cube_add()
                elif thisDef["type"] == "cylinder":
                    bpy.ops.mesh.primitive_cylinder_add()
                
                # rename Object
                bpy.context.object.name = name
                curObject = bpy.data.objects[name]

                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.transform.resize(value=thisDef["transform"])
                if "rotate" in thisDef:
                    bpy.ops.transform.rotate(value=thisDef["rotate"]["value"], orient_axis=thisDef["rotate"]["axis"], orient_type=thisDef["rotate"]["type"])
                bpy.ops.object.mode_set(mode='OBJECT')
                # Get the Position and Rotation
                bpy.ops.transform.translate(value=(position['x'], position['y'], position['z']))
                bpy.context.object.rotation_mode = 'QUATERNION'
                for rot in rotation:
                    print(rot)
                    if rot == "x":
                        bpy.context.object.rotation_quaternion.x = rotation['x']
                    if rot == "y":
                        bpy.context.object.rotation_quaternion.y = rotation['y']
                    if rot == "z":
                        bpy.context.object.rotation_quaternion.z = rotation['z']
                    if rot == "w":
                        bpy.context.object.rotation_quaternion.w = rotation['w']
                # Assign the Material
                #bpy.context.object.data.materials.append(bpy.data.materials.get(thisDef["material"]))
                curObject.data.materials.append(bpy.data.materials.get(thisDef["material"]))
                # remove Object of his Collection and put the Object into the new Collection
                for objCols in bpy.context.object.users_collection:
                    objCols.objects.unlink(bpy.context.object)
                bpy.data.collections[self.gameID].objects.link(curObject)



# v2 - Splited Classes
def startMain():

    # Initialize Classes
    SOFTReader = SOFTGameReader()
    SOFTBlender = SOFTGameBlender(saveGameID, gameDefinitions)

    # FischEye's Path at Work
    gamePath = r"C:\DATA\GIT\soft2blender"
    # FischEye's Path at Home
    gamePath = r"G:\Daten\Projects\soft2blender"
    
    # Load the SaveGame
    if SOFTReader.loadSaveGame(saveGameID, customPath=gamePath):

        # Get all Object Categories
        catIDs = SOFTReader.getConstructionCategories()
        SOFTBlender.createCollection()
        SOFTBlender.createMaterials()
        
        # Iterate all Categories
        for catID in catIDs:
            structID = -1
            # Iterate all Structures
            for structure in SOFTReader.getConstructionCategoryByID(catID):
                structID += 1
                structureData = SOFTReader.getStructure(structure)
                if structureData != None:
                    typeID, position, rotation, elements = structureData
                    print("Process Structure:", typeID)
                    # Iterate all Elements
                    for elementID in range(len(elements)):
                        element = elements[elementID]
                        profileID, position, rotation, lenghtScale = SOFTReader.getElement(element)
                        name = "Obj-" + str(catID) + "-" + str(structID) + "-" + str(elementID)
                        # Create Element in BLender
                        SOFTBlender.createObject(name, profileID, position, rotation)


# ------------------------------------------------------------------------------
# Main Program


gameDefinitions = {
    "ObjectMaterials": {
        "WoodLog": [0.0420278, 0.00887743, 0.00520561, 1],
        "Stone": [0.0420277, 0.0420277, 0.0420277, 1],
        "Undefined": [0.634298, 0.0546605, 0.650006, 1]
    },
    "ObjectDefinition": {
        "0": {
                "type": "cube",
                "transform": [0.125, 0.125, 0.125],
                "material": "Undefinded"
            },
        "1": {
                "type": "cylinder",
                "transform": [0.25, 0.25, 1.1],
                "material": "WoodLog"
            },
        "2": {
                "type": "cylinder",
                "transform": [0.25, 0.25, 1.1],
                "material": "WoodLog"
            },
        "12": {
                "type": "cylinder",
                "transform": [0.1, 0.1, 0.6],
                "rotate": { "value": 1.5708, "axis": "X", "type": "LOCAL" },
                "material": "WoodLog"
            },
        "213": {
                "type": "cube",
                "transform": [0.2, 0.2, 0.2],
                "material": "Stone"
            },
        "224": {
                "type": "cube",
                "transform": [0.2, 0.2, 0.2],
                "material": "Stone"
            }
        }
}


if __name__ == "__main__":
    startMain()
