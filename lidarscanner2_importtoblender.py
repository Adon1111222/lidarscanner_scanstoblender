# Lidar Scanner 2 scan files to blender importer.


import json
import bpy
import math

# path to the saved scans file (in Windows you can copy it by right-clicking path: Copy address as text).
filename = "C:/base/gm_construct_strippednfscan_1041762-400-3000.txt"
# how much the dots will be close(the higher the value, the closer they are to the world origin). if you put less than 1 then it will be multiplied. default value: 52.49  (most likely this is the source engine's standard unit of meters, but im not sure).
div = 52.49
# size of dots, in meters. if you want the dots to be the same size as in the game, then divide by 52.49
# dots SIZES ARE NOT SAVED in scan files
dotssize = 0.019

# yes, this script will take a long time to process dots. may be longer than saving.
# if you have ideas on how to speed it up, suggest them, do not just criticize.

def normal_to_angles(x,y,z):
    return (math.degrees(math.asin(-y)),math.degrees(math.atan2(x, z)),0)

with open(filename, 'r') as file:
    header = file.readline().strip()
    mat_count = 0
    if header != "LIDARSCANNERSCANFILE":
        raise ValueError("ERROR: NOT VALID HEADER")
    for line in file:
        data = json.loads(line)
        pos2 = data[0].replace('[',"").replace(']',"")
        normal2 = data[1].replace('[',"").replace(']',"")
        pos3 = pos2.split(' ')
        normal3 = normal2.split(' ')
        pos = (float(pos3[0])/div,float(pos3[1])/div,float(pos3[2])/div)
        normal = normal_to_angles(float(normal3[0])/div,float(normal3[1])/div,float(normal3[2])/div)
        colour = data[2]
        mat_count = mat_count + 1
        
        bpy.ops.mesh.primitive_plane_add(size=dotssize, location=pos,rotation = normal)
        plane = bpy.context.object
        
        plane.data.polygons[0].use_smooth = True
        
        mat = bpy.data.materials.new(name="DotMaterial_"+str(mat_count))
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes["Principled BSDF"]
        bsdf.inputs['Base Color'].default_value = (colour['r']/255,colour['g']/255,colour['b']/255,1)
        plane.data.materials.append(mat)