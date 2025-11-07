# Lidar Scanner 2 scans files to blender importer.

# A couple of things to know:
# This script does not have a UI as such - you enter everything into this file, and the tips will help you.
# This script will take a long time to process dots. May be longer than saving. If you have ideas on how to speed it up - suggest them.
# This script creates a very large number of materials(for the dots) because the dots are different colours,
#   and Blender does not allow you to change the colour of a single object(or i do not know how).

import json
import bpy
import math
import struct # For struct.unpack

# Specify the full path to the scans file.
Filename = r"C:\Program Files (x86)\Steam\steamapps\common\GarrysMod\garrysmod\data\lidarscanner_savedscans\fffffffffff.txt"

# Name of the collection to save dots to.
Collectionname = "Dots"

# How much the dots will be close(the higher the value, the closer they are to the world origin).
# Default value: 52.49 (most likely this is the source engine's standard unit of meters, but im not sure).
div = 52.49

# Size of dots, in meters. If you want the dots to be the same size as in the game, then divide by 52.49
# Dots SIZES ARE NOT SAVED in scans files.
dotssize = 0.019

if Collectionname in bpy.data.collections:
    Outcollection = bpy.data.collections[Collectionname]
else:
    Outcollection = bpy.data.collections.new(Collectionname)
    bpy.context.scene.collection.children.link(Outcollection)


def normal_to_angles(x,y,z):
    return (math.degrees(math.asin(-y)),math.degrees(math.atan2(x, z)),0)

def create_dot(pos,normal,colour):
    bpy.ops.mesh.primitive_plane_add(size=dotssize, location=pos,rotation = normal)
    plane = bpy.context.object
    bpy.context.collection.objects.unlink(plane)
    Outcollection.objects.link(plane)
        
    plane.data.polygons[0].use_smooth = True
    material_name = ("LIDARdot_"+str(colour['r']) + "-" + str(colour['g']) + "-" + str(colour['b']))
    if material_name in bpy.data.materials:
        mat = bpy.data.materials.get(material_name)
        plane.data.materials.append(mat)
    else:
        mat = bpy.data.materials.new(name=material_name)
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes["Principled BSDF"]
        bsdf.inputs['Base Color'].default_value = (colour['r']/255,colour['g']/255,colour['b']/255,1)
        plane.data.materials.append(mat)
    return plane

def freadlong(iFile):
    fbytes = iFile.read(4)
    if not fbytes:
        raise ValueError("EOF")
    return struct.unpack('<i', fbytes)[0]
def freadfloat(iFile):
    fbytes = iFile.read(4)
    if not fbytes:
        raise ValueError("EOF")
    return struct.unpack('<f', fbytes)[0]
def freadbyte(iFile):
    fbytes = iFile.read(1)
    if not fbytes:
        raise ValueError("EOF")
    return int.from_bytes(fbytes,"little")

with open(Filename, 'rb') as file:
    header = file.read(20)
    if header != b"LIDARSCANNERSCANFILE" and header != b"LIDARSCANNERSCANS2\0\0":
        raise ValueError("Error: Header signature non-valid(" + str(header) + ")")
    print("Reading " + Filename)
    if header == b"LIDARSCANNERSCANFILE":
        print("File type: 1")
        file.read(1) # Skip new line
        for line in file:
            data = json.loads(line)
            pos2 = data[0].replace('[',"").replace(']',"")
            normal2 = data[1].replace('[',"").replace(']',"")
            pos3 = pos2.split(' ')
            normal3 = normal2.split(' ')
            pos = (float(pos3[0])/div,float(pos3[1])/div,float(pos3[2])/div)
            normal = normal_to_angles(float(normal3[0])/div,float(normal3[1])/div,float(normal3[2])/div)
            colour = data[2]
            create_dot(pos,normal,colour)
    elif header == b"LIDARSCANNERSCANS2\0\0":
        print("File type: 2")
        len = freadlong(file)
        print("Dots number: " + str(len))
        for i in range(0,len):
            pos = (freadfloat(file)/div,freadfloat(file)/div,freadfloat(file)/div)
            normal = normal_to_angles(freadfloat(file)/div,freadfloat(file)/div,freadfloat(file)/div)
            colour = {'r': freadbyte(file),'g': freadbyte(file),'b': freadbyte(file)}
            create_dot(pos,normal,colour)

