# To easily test this, on a command prompt do:
# "C:\Program Files\Blender Foundation\Blender 2.91\blender.exe" --python KhepriServer.py
# To test this while still allowing redefinitions do:
# "C:\Program Files\Blender Foundation\Blender 2.91\blender.exe"
# and then, in Blender's Python console
# exec(open("KhepriServer.py").read())

import FreeCAD, FreeCADGui, Mesh, Part, FreeCAD, Draft, Arch
from FreeCAD import Vector
from pivy import coin
import math, time, os.path

from typing import List, Tuple, NewType
Size = NewType('Size', int)
Length = NewType('Length', float) # This is needed to transform units
Point3d = Vector
Vector3d = Vector
Id = Size
MatId = Size
RGB = Tuple[float,float,float]
RGBA = Tuple[float,float,float,float]

def warn(msg):
    FreeCAD.Console.PrintMessage(msg)
    FreeCAD.Console.PrintMessage("\n")

doc = FreeCAD.newDocument()

shape_counter = 0
def new_id()->Id:
    global shape_counter
    shape_counter += 1
    return shape_counter, "k" + str(shape_counter)

def addObject(type, shape):
    id, name = new_id()
    # We ignore type and always use Part::Feature because, otherwise,
    # objects (e.g., spheres) do not sync their properties with the
    # geometry, they simply regenerate the geometry whenever the
    # properties change.
    #doc.addObject(type, name).Shape = shape
    doc.addObject("Part::Feature", name).Shape = shape
    return id

# materials = []
# def add_material(mat):
#     materials.append(mat)
#     return len(materials) - 1
#
# def get_material(name:str)->MatId:
#     return add_material(D.materials[name])
#
# def new_glass_material(name:str, color:RGBA, roughness:float, ior:float)->MatId:
#     return add_node_material(mat, node)
#
# def new_mirror_material(name:str, color:RGBA)->MatId:
#     return add_node_material(mat, node)
#
# def new_metal_material(name:str, color:RGBA, roughness:float, ior:float)->MatId:
#     return add_node_material(mat, node)
#
# def new_material(name:str, base_color:RGBA, metallic:float, specular:float, roughness:float,
#                  clearcoat:float, clearcoat_roughness:float, ior:float,
#                  transmission:float, transmission_roughness:float,
#                  emission:RGBA, emission_strength:float)->MatId:
# ...
#     return add_node_material(mat, node)
#
# # We should be using Ints for layers!
# # HACK!!! Missing color!!!!!
# current_collection = C.collection
# def find_or_create_collection(name:str, active:bool, color:RGBA)->str:
#     if name not in D.collections:
#         collection = D.collections.new(name)
#         collection.hide_viewport = not active
#         C.scene.collection.children.link(collection)
#     return name
#
# def get_current_collection()->str:
#     return current_collection.name
#
# def set_current_collection(name:str)->None:
#     global current_collection
#     current_collection = D.collections[name]
#
# #def all_shapes_in_collection(name:str)->List[Id]:
# def delete_all_shapes_in_collection(name:str)->None:
#     D.batch_remove(D.collections[name].objects)
#     D.orphans_purge(do_linked_ids=False)
#
def delete_all_shapes()->None:
    for obj in doc.Objects:
        doc.removeObject(obj.Name)

def delete_shape(name:Id)->None:
    doc.removeObject("k" + str(name))

def select_shape(name:Id)->None:
    FreeCADGui.Selection.addSelection(doc.getObject("k" + str(name)))

def deselect_shape(name:Id)->None:
    FreeCADGui.Selection.removeSelection(doc.getObject("k" + str(name)))

def deselect_all_shapes()->None:
    FreeCADGui.clearSelection()

def xform_from_o_vx_vy(o, x, y):
    x_local = x.normalize()
    y_local = y.normalize()
    z_local = x.cross(y).normalize()
    m = FreeCAD.Matrix()
    m.A11 = x_local.x
    m.A12 = y_local.x
    m.A13 = z_local.x
    m.A14 = o.x
    m.A21 = x_local.y
    m.A22 = y_local.y
    m.A23 = z_local.y
    m.A24 = o.y
    m.A31 = x_local.z
    m.A32 = y_local.z
    m.A33 = z_local.z
    m.A34 = o.z
    return m

def wire(ps):
    return Part.makePolygon(ps)

def closed_wire(ps):
    return Part.makePolygon(ps+[ps[0]])

def face(ps):
    return Part.Face([closed_wire(ps)])

def face_with_holes(pss):
    return Part.Face([closed_wire(ps) for ps in pss])

# def line(ps:List[Point3d], closed:bool, mat:MatId)->Id:
#     edges = [Part.Edge(Part.LineSegment(ps[i], ps[i+1])) for i in range(0, len(ps)-1)]
#     if closed:
#         edges.append(Part.Edge(Part.LineSegment(ps[len(ps)-1], ps[0])))
#     return addObject("Part::Line", Part.Wire(edges))

def line(ps:List[Point3d], closed:bool, mat:MatId)->Id:
    return addObject("Part::Line", closed_wire(ps) if closed else wire(ps))
# def nurbs(order:int, ps:List[Point3d], closed:bool, mat:MatId)->Id:
#     #print(order, ps, closed)
#     id, name = new_id()
#     kind = "NURBS"
#     curve = D.curves.new(name, "CURVE")
#     curve.dimensions = "3D"
#     obj = D.objects.new(name, curve)
#     current_collection.objects.link(obj)
#     spline = curve.splines.new(kind)
#     #spline.order_u = order
#     spline.use_cyclic_u = closed
#     n = len(ps) - (1 if closed else 0)
#     spline.points.add(n - 1)
#     for i in range(0, n):
#         p = ps[i]
#         spline.points[i].co = (p[0], p[1], p[2], 1.0)
#     append_material(obj, mat)
#     return id
#

def trig(p1:Point3d, p2:Point3d, p3:Point3d, mat:MatId)->Id:
    return face([p1, p2, p3])

def quad(p1:Point3d, p2:Point3d, p3:Point3d, p4:Point3d, mat:MatId)->Id:
    return face([p1, p2, p3, p4])

def quad_strip_faces(ps, qs):
    return [face([ps[i], ps[i+1], qs[i+1], qs[i]]) for i in range(0, len(ps)-1)]

def quad_strip_closed_faces(ps, qs):
    n = len(ps)-1
    faces = [face([ps[i], ps[i+1], qs[i+1], qs[i]]) for i in range(0, n)]
    faces.append(face([ps[n], ps[0], qs[0], qs[n]]))
    return faces

def quad_strip(ps:List[Point3d], qs:List[Point3d], smooth:bool, mat:MatId)->Id:
    return addObject("Part::Feature", Part.makeShell(quad_strip_faces(ps, qs)))

def quad_strip_closed(ps:List[Point3d], qs:List[Point3d], smooth:bool, mat:MatId)->Id:
    return addObject("Part::Feature", Part.makeShell(quad_strip_closed_faces(ps, qs)))
#
# def quad_surface(ps:List[Point3d], nu:int, nv:int, closed_u:bool, closed_v:bool, smooth:bool, mat:MatId)->Id:
#     faces = []
#     if closed_u:
#         for i in range(0, nv-1):
#             faces.extend(quad_strip_closed_faces(i*nu, nu))
#         if closed_v:
#             faces.extend([[p, p+1, q+1, q] for (p, q) in zip(range((nv-1)*nu,nv*nu-1), range(0, nu-1))])
#             faces.append([nv*nu-1, (nv-1)*nu, 0, nu-1])
#     else:
#         for i in range(0, nv-1):
#             faces.extend(quad_strip_faces(i*nu, nu))
#         if closed_v:
#             faces.extend([[p, p+1, q+1, q] for (p, q) in zip(range((nv-1)*nu,nv*nu), range(0, nu))])
#     return objmesh(ps, [], faces, smooth, mat)
#
def ngon(ps:List[Point3d], pivot:Point3d, smooth:bool, mat:MatId)->Id:
    n = len(ps)-1
    faces = [face([ps[i], ps[i+1], pivot]) for i in range(0, n)]
    faces.append(face([ps[n], ps[0], pivot]))
    return addObject("Part::Feature", Part.makeShell(faces))

def polygon(ps:List[Point3d], mat:MatId)->Id:
    return addObject("Part::Face", face(ps))

def polygon_with_holes(pss:List[List[Point3d]], mat:MatId)->Id:
    return addObject("Part::Face", face_with_holes(pss))

def circle(c:Point3d, v:Vector3d, r:Length, mat:MatId)->Id:
    return addObject("Part::Circle", Part.makeCircle(r, c, v))

def cuboid(verts:List[Point3d], mat:MatId)->Id:
    return addObject("Part::Feature",
        Part.makeSolid(
            Part.makeShell(
                [face([verts[i] for i in idx])
                 for idx in [(0,1,2,3), (4,5,6,7), (0,1,5,4), (1,2,6,5), (2,3,7,6), (3,0,4,7)]])))

def pyramid_frustum(bs:List[Point3d], ts:List[Point3d], smooth:bool, bmat:MatId, tmat:MatId, smat:MatId)->Id:
    faces = [face(bs[::-1]), face(ts)]
    faces.extend(quad_strip_closed_faces(bs, ts))
    return addObject("Part::Feature", Part.makeSolid(Part.makeShell(faces)))

def sphere(center:Point3d, radius:Length, mat:MatId)->Id:
    return addObject("Part::Sphere", Part.makeSphere(radius, center))

def cone_frustum(b:Point3d, br:Length, t:Point3d, tr:Length, bmat:MatId, tmat:MatId, smat:MatId)->Id:
    vec = t - b
    # FreeCAD does not allow cones to have identical top and bottom radius
    if br == tr:
        return addObject("Part::Cylinder", Part.makeCylinder(br, vec.Length, b, vec))
    else:
        return addObject("Part::Cone", Part.makeCone(br, tr, vec.Length, b, vec))

def box(p:Point3d, vx:Vector3d, vy:Vector3d, dx:Length, dy:Length, dz:Length, mat:MatId)->Id:
    b = Part.makeBox(dx, dy, dz)
    b.Matrix = xform_from_o_vx_vy(p, vx, vy)
    return addObject("Part::Box", b)

def torus(c:Point3d, v:Vector3d, r1:Length, r2:Length, mat:MatId):
    return addObject("Part::Torus", Part.makeTorus(r1, r2, c, v))

# def text(txt:str, p:Point3d, vx:Vector3d, vy:Vector3d, size:float)->Id:
#     id, name = new_id()
#     rot = quaternion_from_vx_vy(vx, vy)
#     text_data = D.curves.new(name=name, type='FONT')
#     text_data.body = txt
#     #text_data.align_x = align_x
#     #text_data.align_y = align_y
#     text_data.size = size
#     text_data.font = D.fonts["Bfont"]
#     #text_data.space_line = space_line
#     #text_data.extrude = extrude
#     obj = D.objects.new(name, text_data)
#     obj.location = p
#     obj.rotation_euler = rot.to_euler()
#     current_collection.objects.link(obj)
#     return id
#
# # Lights
# def area_light(p:Point3d, v:Vector3d, size:float, color:RGBA, energy:float)->Id:
#     id, name = new_id()
#     rot = Vector((0, 0, 1)).rotation_difference(v)  # Rotation from Z axis
#     light_data = D.lights.new(name, 'AREA')
#     light_data.energy = energy
#     light_data.size = size
#     light_data.use_nodes = True
#     light_data.node_tree.nodes["Emission"].inputs["Color"].default_value = color
#     light = D.objects.new(name, light_data)
#     light.location=location
#     light.rotation=rotation
#     return id
#
# def sun_light(p:Point3d, v:Vector3d)->Id:
#     id, name = new_id()
#     rot = Vector((0, 0, 1)).rotation_difference(v)  # Rotation from Z axis
#     bpy.ops.object.light_add(name=name, type='SUN', location=p, rotation=rot)
#     return id
#
# def light(p:Point3d, type:str)->Id:
#     id, name = new_id()
#     light_data = D.lights.new(name, type)
#     light = D.objects.new(name, light_data)
#     light.location = p
#     current_collection.objects.link(light)
#
# def khepri_sun():
#     name = 'KhepriSun'
#     name = 'Sun'
#     if D.objects.find(name) == -1:
#         bpy.ops.object.light_add(type='SUN')
#     return D.objects[name]
#
# def set_sun(latitude:float, longitude:float, elevation:float,
#             year:int, month:int, day:int, time:float,
#             UTC_zone:float, use_daylight_savings:bool)->None:
#     sun_props = C.scene.sun_pos_properties #sunposition.sun_calc.sun
#     sun_props.usage_mode = 'NORMAL'
#     sun_props.use_daylight_savings = False
#     sun_props.use_refraction = True
#     sun_props.latitude = latitude
#     sun_props.longitude = longitude
#     sun_props.month = month
#     sun_props.day = day
#     sun_props.year = year
#     sun_props.use_day_of_year = False
#     sun_props.UTC_zone = UTC_zone
#     sun_props.time = time
#     sun_props.sun_distance = 100
#     sun_props.use_daylight_savings = use_daylight_savings
#     # Using Sky Texture => It creates its own sun.
#     #sun_props.sun_object = khepri_sun()
#     sunposition.sun_calc.update_time(C)
#     sunposition.sun_calc.move_sun(C)
#
# def find_or_create_node(node_tree, search_type, create_type):
#     for node in node_tree.nodes:
#         if node.type == search_type:
#             return node
#     return node_tree.nodes.new(type=create_type)
#
# def find_or_create_world(name):
#     for world in D.worlds:
#         if world.name == name:
#             return world
#     return D.worlds.new(name)
#
# def set_sky(turbidity:float)->None:
#     C.scene.render.engine = 'CYCLES'
#     world = find_or_create_world("World")
#     world.use_nodes = True
#     bg = find_or_create_node(world.node_tree, "BACKGROUND", "")
#     sky = find_or_create_node(world.node_tree, "TEX_SKY", "ShaderNodeTexSky")
#     #sky.sky_type = "HOSEK_WILKIE"
#     sky.sky_type = "NISHITA"
#     sky.turbidity = turbidity
#     sky.dust_density = turbidity
#     #Sun Direction
#     #Sun direction vector.
#     #
#     #Ground Albedo
#     #Amount of light reflected from the planet surface back into the atmosphere.
#     #
#     #Sun Disc
#     #Enable/Disable sun disc lighting.
#     #
#     #Sun Size
#     #Angular diameter of the sun disc (in degrees).
#     #
#     #Sun Intensity
#     #Multiplier for sun disc lighting.
#     #
#     #Sun Elevation
#     #Rotation of the sun from the horizon (in degrees).
#     #
#     #Sun Rotation
#     #Rotation of the sun around the zenith (in degrees).
#     #
#     #Altitude
#     #The distance from sea level to the location of the camera. For example, if the camera is placed on a beach then a value of 0 should be used. However, if the camera is in the cockpit of a flying airplane then a value of 10 km will be more suitable. Note, this is limited to 60 km because the mathematical model only accounts for the first two layers of the earth’s atmosphere (which ends around 60 km).
#     #
#     #Air
#     #Density of air molecules.
#     #0 no air
#     #1 clear day atmosphere
#     #2 highly polluted day
#     #
#     #Dust
#     #Density of dust and water droplets.
#     #0 no dust
#     #1 clear day atmosphere
#     #5 city like atmosphere
#     #10 hazy day
#     #
#     #Ozone
#     #Density of ozone molecules; useful to make the sky appear bluer.
#     #0 no ozone
#     #1 clear day atmosphere
#     #2 city like atmosphere
#     world.node_tree.links.new(bg.inputs[0], sky.outputs[0])
#
# def current_space():
#     area = next(area for area in C.screen.areas if area.type == 'VIEW_3D')
#     space = next(space for space in area.spaces if space.type == 'VIEW_3D')
#     return space

def set_view(camera:Point3d, target:Point3d, lens:float)->None:
    view = FreeCADGui.ActiveDocument.ActiveView
    view.setCameraType("Perspective")
    cam = view.getCameraNode()
    cam.position.setValue(camera)
    dir = target-camera
    cam.focalDistance.setValue(dir.Length)
    cam.pointAt(coin.SbVec3f(dir),coin.SbVec3f(0,0,1))
    cam.heightAngle.setValue(2*math.atan(10/lens))

def get_view()->Tuple[Point3d, Point3d, float]:
    view = FreeCADGui.ActiveDocument.ActiveView
    cam = view.getCameraNode()
    camera = Vector(cam.position.getValue())
    target = camera + view.getViewDirection()*cam.focalDistance.getValue()
    return (camera, target, 10/math.tan(cam.heightAngle.getValue()/2))
#
# def set_render_size(width:int, height:int)->None:
#     C.scene.render.resolution_x = width
#     C.scene.render.resolution_y = height
#     C.scene.render.resolution_percentage = 100
#     #C.scene.render.resolution_percentage = 50
#     #C.scene.render.pixel_aspect_x = 1.0
#     #C.scene.render.pixel_aspect_y = 1.0
#FreeCAD.Gui.activeDocument().activeView().saveImage("foo.png", XSIZE,YSIZE,"White")
# def set_render_path(filepath:str)->None:
#     C.scene.render.image_settings.file_format = 'PNG'
#     C.scene.render.filepath = filepath
#
# def default_renderer()->None:
#     bpy.ops.render.render(use_viewport = True, write_still=True)
#
# # Last resort

def freecad_cmd(expr:str)->None:
    eval(expr)

def recompute()->None:
    doc.recompute()

# BIM

def wall(ps:List[Point3d], height:Length, align:str, mat:MatId)->Id:
    id, name = new_id()
    matA = Arch.makeMaterial()
    matB = Arch.makeMaterial()
    matMulti = Arch.makeMultiMaterial()
    matMulti.Materials = [matA, matB]
    matMulti.Thicknesses = [100, 200]
    wire = Draft.makeWire(ps)
    wallWire = Arch.makeWall(wire, height=height, align=align, name=name)
    wallWire.Material = matMulti
    return id

#######################################
# Communication
#Python provides sendall but not recvall
def recvall(sock, count):
    buf = b''
    while count:
        newbuf = sock.recv(count)
        if not newbuf: return None
        buf += newbuf
        count -= len(newbuf)
    return buf

"""
class _Point3dArray(object):
    def write(self, conn, ps):
        Int.write(conn, len(ps))
        for p in ps:
            Point3d.write(conn, p)
    def read(self, conn):
        n = Int.read(conn)
        if n == -1:
            raise RuntimeError(String.read(conn))
        else:
            pts = []
            for i in range(n):
                pts.append(Point3d.read(conn))
            return pts

Point3dArray = _Point3dArray()

class _Frame3d(object):
    def write(self, conn, ps):
        raise Error("Bum")
    def read(self, conn):
        return u0(cs_from_o_vx_vy_vz(Point3d.read(conn),
                                     Vector3d.read(conn),
                                     Vector3d.read(conn),
                                     Vector3d.read(conn)))

Frame3d = _Frame3d()


fast_mode = False

class _ObjectId(Packer):
    def __init__(self):
        super().__init__('1i')
    def read(self, conn):
        if fast_mode:
            return incr_id_counter()
        else:
            _id = super().read(conn)
            if _id == -1:
                raise RuntimeError(String.read(conn))
            else:
                return _id

ObjectId = _ObjectId()
Entity = _ObjectId()
ElementId = _ObjectId()

class _ObjectIdArray(object):
    def write(self, conn, ids):
        Int.write(conn, len(ids))
        for _id in ids:
            ObjectId.write(conn, _id)
    def read(self, conn):
        n = Int.read(conn)
        if n == -1:
            raise RuntimeError(String.read(conn))
        else:
            ids = []
            for i in range(n):
                ids.append(ObjectId.read(conn))
            return ids

ObjectIdArray = _ObjectIdArray()
"""

import struct
from functools import partial

def dump_exception(ex, conn):
    warn('Dumping exception!!!')
    warn("".join(traceback.TracebackException.from_exception(ex).format()))
    w_str("".join(traceback.TracebackException.from_exception(ex).format()), conn)

def r_struct(s, conn):
    return s.unpack(recvall(conn, s.size))[0]

def w_struct(s, e, conn):
    conn.sendall(s.pack(e))

def e_struct(s, e, ex, conn):
    w_struct(s, e, conn)
    dump_exception(ex, conn)

def r_tuple_struct(s, conn):
    return s.unpack(recvall(conn, s.size))

def w_tuple_struct(s, e, conn):
    conn.sendall(s.pack(*e))

def e_tuple_struct(s, e, ex, conn):
    w_tuple_struct(s, e, conn)
    dump_exception(ex, conn)

def r_list_struct(s, conn):
    n = r_int(conn)
    es = []
    for i in range(n):
        es.append(r_struct(s, conn))
    return es

def w_list_struct(s, es, conn):
    w_int(len(es), conn)
    for e in es:
        w_struct(s, e, conn)

def e_list(ex, conn):
    w_int(-1, conn)
    dump_exception(ex, conn)

int_struct = struct.Struct('i')
float_struct = struct.Struct('d')
byte_struct = struct.Struct('1B')

def w_None(e, conn)->None:
    w_struct(byte_struct, 0, conn)

e_None = partial(e_struct, byte_struct, 127)

def r_bool(conn)->bool:
    return r_struct(byte_struct, conn) == 1
def w_bool(b:bool, conn)->None:
    w_struct(byte_struct, 1 if b else 0, conn)

e_bool = partial(e_struct, byte_struct, 127)

r_int = partial(r_struct, int_struct)
w_int = partial(w_struct, int_struct)
e_int = partial(e_struct, int_struct, -12345678)

r_float = partial(r_struct, float_struct)
w_float = partial(w_struct, float_struct)
e_float = partial(w_struct, float_struct, math.nan)

r_Size = partial(r_struct, int_struct)
w_Size = partial(w_struct, int_struct)
e_Size = partial(e_struct, int_struct, -1)

def r_Length(conn)->Length:
    return r_float(conn)*1000.0
def w_Length(l:Length, conn)->None:
    w_float(l/1000.0, conn)

def r_str(conn)->str:
    size = 0
    shift = 0
    byte = 0x80
    while byte & 0x80:
        try:
            byte = ord(conn.recv(1))
        except TypeError:
            raise IOError('Buffer empty')
        size |= (byte & 0x7f) << shift
        shift += 7
    return recvall(conn, size).decode('utf-8')

def w_str(s:str, conn):
    size = len(s)
    array = bytearray()
    while True:
        byte = size & 0x7f
        size >>= 7
        if size:
            array.append(byte | 0x80)
        else:
            array.append(byte)
            break
    conn.send(array)
    conn.sendall(s.encode('utf-8'))

def e_str(ex, conn)->None:
    w_str("This an error!", conn)
    dump_exception(ex, conn)

float3_struct = struct.Struct('3d')
def r_Vector(conn)->Vector:
    s = float3_struct
    return Vector(*s.unpack(recvall(conn, s.size)))*1000.0

def w_Vector(e:Vector, conn)->None:
    s = float3_struct
    conn.sendall(s.pack(e.x/1000.0, e.y/1000.0, e.z/1000.0))

e_Vector = e_float

def r_List(f, conn):
    n = r_int(conn)
    es = []
    for i in range(n):
        es.append(f(conn))
    return es

def w_List(f, es, conn):
    w_int(len(es), conn)
    for e in es:
        f(e, conn)

e_List = e_list

r_List_int = partial(r_List, r_int)
w_List_int = partial(w_List, w_int)
e_List_int = e_List

r_List_float = partial(r_List, r_float)
w_List_float = partial(w_List, w_float)
e_List_float = e_List

r_List_List_int = partial(r_List, r_List_int)
w_List_List_int = partial(w_List, w_List_int)
e_List_List_int = e_List

r_List_Vector = partial(r_List, r_Vector)
w_List_Vector = partial(w_List, w_Vector)
e_List_Vector = e_List

r_List_List_Vector = partial(r_List, r_List_Vector)
w_List_List_Vector = partial(w_List, w_List_Vector)
e_List_List_Vector = e_List

int_int_struct = struct.Struct('2i')
r_Tint_intT = partial(r_tuple_struct, int_int_struct)
w_Tint_intT = partial(w_tuple_struct, int_int_struct)

r_List_Tint_intT = partial(r_List, r_Tint_intT)
w_List_Tint_intT = partial(w_List, w_Tint_intT)
e_List_Tint_intT = e_List

##############################################################
# For automatic generation of serialize/deserialize code
import inspect

def is_tuple_type(t)->bool:
    return hasattr(t, '__origin__') and t.__origin__ is tuple

def tuple_elements_type(t):
    return t.__args__

def is_list_type(t)->bool:
    return hasattr(t, '__origin__') and t.__origin__ is list

def list_element_type(t):
    return t.__args__[0]

def method_name_from_type(t)->str:
    if is_list_type(t):
        return "List_" + method_name_from_type(list_element_type(t))
    elif is_tuple_type(t):
        return "T" + '_'.join([method_name_from_type(pt) for pt in tuple_elements_type(t)]) + 'T'
    elif t is None:
        return "None"
    else:
        return t.__name__

def deserialize_parameter(c:str, t)->str:
    if is_tuple_type(t):
        return '(' + ','.join([deserialize_parameter(c, pt) for pt in tuple_elements_type(t)]) + ',)'
    else:
        return f"r_{method_name_from_type(t)}({c})"

def serialize_return(c:str, t, e:str)->str:
    if is_tuple_type(t):
        return f"__r = {e}; " + '; '.join([serialize_return(c, pt, f"__r[{i}]")
                                           for i, pt in enumerate(tuple_elements_type(t))])
    else:
        return f"w_{method_name_from_type(t)}({e}, {c})"

def serialize_error(c:str, t, e:str)->str:
    if is_tuple_type(t):
        return serialize_error(c, tuple_elements_type(t)[0], e)
    else:
        return f"e_{method_name_from_type(t)}({e}, {c})"

def try_serialize(c:str, t, e:str)->str:
    return f"""
    try:
        {e}
    except Exception as __ex:
        warn('RMI Error!!!!')
        warn("".join(traceback.TracebackException.from_exception(__ex).format()))
        warn('End of RMI Error.  I will attempt to serialize it.')
        {serialize_error(c, t, "__ex")}"""

def generate_rmi(f):
    c = 'c'
    name = f.__name__
    sig = inspect.signature(f)
    rt = sig.return_annotation
    pts = [p.annotation for p in sig.parameters.values()]
    des_pts = ','.join([deserialize_parameter(c, p) for p in pts])
    body = try_serialize(c, rt, serialize_return(c, rt, f"{name}({des_pts})"))
    dict = globals()
    rmi_name = f"rmi_{name}"
    rmi_f = f"def {rmi_name}({c}):{body}"
    warn(rmi_f)
    exec(rmi_f, dict)
    return dict[rmi_name]

##############################################################
# Socket server
import socket

socket_server = None
connection = None
current_action = None
min_wait_time = 0.1
max_wait_time = 0.2
max_repeated = 1000

def set_max_repeated(n:int)->int:
    global max_repeated
    prev = max_repeated
    max_repeated = n
    return prev

def read_operation(conn):
    return r_int(conn)

def try_read_operation(conn):
    conn.settimeout(min_wait_time)
    try:
        return read_operation(conn)
    except socket.timeout:
        return -2
    finally:
        conn.settimeout(None)

def execute_read_and_repeat(op, conn):
    count = 0
    while True:
        if op == -1:
            return False
        execute(op, conn)
        count =+ 1
        if count > max_repeated:
            return False
        conn.settimeout(max_wait_time)
        try:
            op = read_operation(conn)
        except socket.timeout:
            break
        finally:
            conn.settimeout(None)
    doc.recompute()
    return True;


operations = []

def provide_operation(name:str)->int:
    warn(f"Requested operation |{name}| -> {globals()[name]}")
    operations.append(generate_rmi(globals()[name]))
    return len(operations) - 1

# The first operation is the operation that makes operations available
operations.append(generate_rmi(provide_operation))


def execute(op, conn):
    operations[op](conn)

def wait_for_connection():
    global current_action
    warn('Waiting for connection...')
    current_action = accept_client

def start_server():
    global socket_server
    socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    socket_server.bind(('localhost', 11004))
    socket_server.settimeout(max_wait_time)
    socket_server.listen(5)
    wait_for_connection()

counter_accept_attempts = 1
def accept_client():
    global counter_accept_attempts
    global connection
    global current_action
    try:
        #warn(f"Is anybody out there? (attempt {counter_accept_attempts})")
        connection, client_address = socket_server.accept()
        warn('Connection established.')
        current_action = handle_client
    except socket.timeout:
        counter_accept_attempts += 1
        #warn('It does not seem that there is.')
        # keep trying
        pass
    except Exception as ex:
        warn('Something bad happened!')
        traceback.print_exc()
        #warn('Resetting socket server.')


def handle_client():
    conn = connection
    op = try_read_operation(conn)
    if op == -1:
        warn("Connection terminated.")
        wait_for_connection()
    elif op == -2:
        # timeout
        pass
    else:
        execute_read_and_repeat(op, conn)

current_action = start_server

import traceback

def execute_current_action():
    #warn(f"Execute {current_action}")
    try:
        current_action()
    except Exception as ex:
        traceback.print_exc()
        #warn('Resetting socket server.')
        warn('Killing socket server.')
        if connection:
            connection.close()
        wait_for_connection()
        # AML Remove when corrected
        #bpy.app.timers.unregister(execute_current_action)
    finally:
        return max_wait_time # timer

from PySide import QtCore
khepri_timer = QtCore.QTimer()
khepri_timer.timeout.connect(execute_current_action)
khepri_timer.start(10)
