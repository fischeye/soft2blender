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

# This Path is were this Python Script, JSON, FBX Files are. <--- IMPORTANT to create the Map
SOFTConverterSourcePath = r"G:\Daten\Projects\soft2blender"

# ------------------------------------------------------------------------------
# Blender Helper Class

class SOFTGameReader:

    def __init__(self):
        self.mapLoaded = False
    

    # save structures to JSON file if needed
    def extractStructes2JSON(self, fileName):
        if self.mapLoaded:
            with open(fileName, 'w') as sf:
                json.dump(self.mapStructures, sf)
    

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

    def __init__(self, gameID, gameDefinitions, sourcePath):
        self.gameID = gameID
        self.blenderLoaded = False
        self.sourcePath = sourcePath
        # check if this script run in Blender and module is loaded
        # script will run in plain python as well, without creating blender objects
        if "bpy" in sys.modules:
            self.blenderLoaded = True
            #gameDefinitions = json.load(open("soft2blender.json", "r"))
            self.objectDefs = gameDefinitions["ObjectDefinition"]
            self.materialDefs = gameDefinitions["ObjectMaterials"]
    
    def firstSteps(self):
        if self.blenderLoaded:
            # Select everything
            bpy.ops.object.select_all(action='SELECT')
            # Delete everything
            bpy.ops.object.delete(use_global=False)
    
    def finalSteps(self):
        if self.blenderLoaded:
            # Select everything
            bpy.ops.object.select_all(action='SELECT')
            # Set Pivot Transform to CURSOR
            bpy.context.scene.tool_settings.transform_pivot_point = 'CURSOR'
            # Scale it down to become more handy
            bpy.ops.transform.resize(value=(0.1, 0.1, 0.1))
            # TODO: Pivot Point Scale does not work. 
            bpy.ops.transform.translate(value=(305, 0, -725), orient_axis_ortho='X', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', mirror=False, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False, snap=False, snap_elements={'INCREMENT'}, use_snap_project=False, snap_target='CLOSEST', use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True, use_snap_selectable=False)
            # Rotate everything
            bpy.ops.transform.rotate(value=1.5708, orient_axis='X', orient_type='GLOBAL')
            # Mirror
            bpy.ops.transform.mirror(orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(False, False, True))


    def importFBX(self, fbxpath):
        if self.blenderLoaded:
            result = None
            objectsBefore = set(bpy.context.scene.objects)
            bpy.ops.import_scene.fbx(filepath = fbxpath)
            objectsNew = set(bpy.context.scene.objects) - objectsBefore
            bpy.ops.object.select_all(action='DESELECT')
            for newObj in objectsNew:
                newObj.select_set(True)
                result = bpy.data.objects.get(newObj.name)
                break
            return result

    
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

    def createObject(self, name, profileID, position, rotation, lenghtScale):
        if self.blenderLoaded:
            isFBX = False
            if str(profileID) in self.objectDefs:
                thisDef = self.objectDefs[str(profileID)]
            else:
                # Undefined Object
                thisDef = self.objectDefs["0"]
            print("Blender: Create Object")
            if thisDef["type"] == "cube":
                bpy.ops.mesh.primitive_cube_add()
            elif thisDef["type"] == "cylinder":
                bpy.ops.mesh.primitive_cylinder_add()
            elif thisDef["type"] == "sphere":
                bpy.ops.mesh.primitive_ico_sphere_add()
            elif thisDef["type"] == "fbx":
                isFBX = True
                newObject = self.importFBX(os.path.join(self.sourcePath, thisDef["file"]))
                #return "PROBLEM HERE"
            
            if not isFBX:
                # Rename Object
                bpy.context.object.name = name
                curObject = bpy.data.objects[name]
            else:
                newObject.name = name
                curObject = newObject
            
            # Transformations
            bpy.ops.object.mode_set(mode='EDIT')
            print(profileID)
            print(thisDef["transform"])
            bpy.ops.transform.resize(value=thisDef["transform"])
            if "rotate" in thisDef:
                bpy.ops.transform.rotate(value=thisDef["rotate"]["value"], orient_axis=thisDef["rotate"]["axis"], orient_type=thisDef["rotate"]["type"])
            # Bevel
            if "bevel" in thisDef:
                bpy.ops.mesh.bevel(offset=thisDef["bevel"], offset_pct=0, affect='EDGES')
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
            # LengthScale
            if not lenghtScale == 1:
                bpy.ops.transform.resize(value=(1, 1, lenghtScale), orient_type='LOCAL')
            # Assign the Material
            curObject.data.materials.append(bpy.data.materials.get(thisDef["material"]))
            # Remove Object of his Collection and put the Object into the new Collection
            for objCols in bpy.context.object.users_collection:
                objCols.objects.unlink(bpy.context.object)
            bpy.data.collections[self.gameID].objects.link(curObject)



# v2 - Splited Classes
def startMain():

    # Initialize Classes
    SOFTReader = SOFTGameReader()
    SOFTBlender = SOFTGameBlender(saveGameID, gameDefinitions, SOFTConverterSourcePath)

    # FischEye's Path at Work
    gamePath = r"C:\DATA\GIT\soft2blender"
    # FischEye's Path at Home
    gamePath = r"G:\Daten\Projects\soft2blender"
    
    # Load the SaveGame
    #if SOFTReader.loadSaveGame(saveGameID, customPath=gamePath):
    if SOFTReader.loadSaveGame(saveGameID, singlePlayer=True):

        if not SOFTBlender.blenderLoaded:
            SOFTReader.extractStructes2JSON(os.path.join(gamePath, "structures.json"))

        # Get all Object Categories
        catIDs = SOFTReader.getConstructionCategories()
        SOFTBlender.firstSteps()
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
                        name = "Obj-" + str(profileID) + "-" + str(catID) + "-" + str(structID) + "-" + str(elementID)
                        # Create Element in BLender
                        SOFTBlender.createObject(name, profileID, position, rotation, lenghtScale)
        
        # Import SOFTMap
        SOFTBlender.importFBX(os.path.join(SOFTConverterSourcePath, "softmap.fbx"))
        # Need to move the map, but cant select the Object :-(
        #bpy.ops.transform.translate(value=(0, 0, 1.42108), orient_axis_ortho='X', orient_type='GLOBAL')

        # Final Steps
        SOFTBlender.finalSteps()


# ------------------------------------------------------------------------------
# Main Program

gameDefinitions = json.load(open(os.path.join(SOFTConverterSourcePath, "softobjects.json"), 'r'))

if __name__ == "__main__":
    startMain()
