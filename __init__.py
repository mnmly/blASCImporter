# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITN ESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

# TODO: Investigate the y direction

bl_info = {
    "name" : "blASCImporter",
    "author" : "Hiroaki Yamane",
    "description" : "",
    "blender" : (2, 80, 0),
    "version" : (0, 0, 1),
    "location" : "",
    "warning" : "",
    "category" : "Generic"
}

import os
import re
import bpy
import enum
from bpy_extras.io_utils import ImportHelper
from bpy.types import Operator, OperatorFileListElement

from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       CollectionProperty,
                       FloatVectorProperty,
                       EnumProperty,
                       PointerProperty,
                       )
from . import auto_load

class MNML_OT_ASCImporter(bpy.types.Operator, ImportHelper):
    
    """ASC Importer"""       # Use this as a tooltip for menu items and buttons.
    bl_idname = "mnml.asc"        # Unique identifier for buttons and menu items to reference.
    bl_label = "Import ASC as mesh"   # Display name in the interface.

    filename_ext = ".asc"
    files = CollectionProperty(name="ASC Files", type=OperatorFileListElement) 
    directory = StringProperty(subtype='DIR_PATH')
    filter_glob : StringProperty( default = "*.asc", options = { 'HIDDEN' })

    def execute(self, context):
        for file in [os.path.join(self.directory,file.name) for file in self.files]:
            asc_definition = {
                "ncols": -1,
                "nrows": -1,
                "xllcorner": 0,
                "yllcorner": 0,
                "NODATA_value": 0,
                "byteorder":"LSBFIRST"
            }
            ncols = -1
            nrows = -1
            verts = []
            with open(file, 'r') as f:
                y = 0
                mesh = bpy.data.meshes.new(name='created mesh')
                obj = bpy.data.objects.new("MyObject", mesh)  
                for line in f:
                    component = line.split(' ')
                    if len(component) == 2:
                        (name, value) = component
                        asc_definition[name] = int(value)
                    else:
                        for (x, z) in enumerate(component):
                            vert = (float(x * asc_definition['cellsize']), float(y * asc_definition['cellsize']), float(z))
                            verts.append(vert)
                        y += 1
                count = 0
                ncols = asc_definition['ncols']
                nrows = asc_definition['nrows']
                faces = []
                for i in range (0, nrows * (ncols - 1)):
                    if count < nrows - 1:
                        A = i
                        B = i + 1
                        C = (i + nrows)+1
                        D = (i + nrows)
                
                        face = (A,B,C,D)
                        faces.append(face)
                        count = count + 1
                    else:
                        count = 0
                mesh.from_pydata(verts,[], faces)
                mesh.update(calc_edges=True)
                mesh.validate()
                obj = bpy.data.objects.new('created object', mesh)
                x = float(asc_definition['xllcorner'])
                y = float(asc_definition['yllcorner'])
                obj.location = (x, -y, 0)
                scene = bpy.context.scene
                scene.collection.objects.link(obj)
        return {"FINISHED"}

auto_load.init()
   
# Only needed if you want to add into a dynamic menu
def menu_func_import(self, context):
    self.layout.operator(MNML_OT_ASCImporter.bl_idname, text="ASC (.asc)")
#
# classes to register
#
class_list = (
    MNML_OT_ASCImporter,
)

def register():
    auto_load.register()
    for c in class_list:
        bpy.utils.register_class(c)
    if hasattr(bpy.types, 'TOPBAR_MT_file_import'):
        #2.8+
        bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    else:
        bpy.types.INFO_MT_file_import.append(menu_func_import)

def unregister():
    auto_load.unregister()
    for c in class_list:
        bpy.utils.unregister_class(c)

    if hasattr(bpy.types, 'TOPBAR_MT_file_import'):
        #2.8+
        bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    else:
        bpy.types.INFO_MT_file_import.remove(menu_func_import)