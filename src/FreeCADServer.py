# To easily test this, on a command prompt do:
# "C:\Program Files\Blender Foundation\Blender 2.91\blender.exe" --python KhepriServer.py
# To test this while still allowing redefinitions do:
# "C:\Program Files\Blender Foundation\Blender 2.91\blender.exe"
# and then, in Blender's Python console
# exec(open("KhepriServer.py").read())

# This loads the shared part of the Khepri server
# PS: Don't even try to load that as a module. You will get separate namespaces.
import os
exec(open(os.path.join(os.path.dirname(__file__), "KhepriServer.py")).read())

# Now comes the FreeCAD-specific server

import FreeCAD, FreeCADGui, Mesh, Part, FreeCAD, Draft, Arch
from FreeCAD import Vector
from pivy import coin
import math, time, os.path
Length = NewType('Length', float) # This is needed to transform units
Point3d = Vector
Vector3d = Vector

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


import struct
from functools import partial

def r_Length(conn)->Length:
    return r_float(conn)*1000.0
def w_Length(l:Length, conn)->None:
    w_float(l/1000.0, conn)

def r_Vector(conn)->Vector:
    s = float3_struct
    return Vector(*s.unpack(recvall(conn, s.size)))*1000.0

def w_Vector(e:Vector, conn)->None:
    s = float3_struct
    conn.sendall(s.pack(e.x/1000.0, e.y/1000.0, e.z/1000.0))

e_Vector = e_float

r_List_Vector = partial(r_List, r_Vector)
w_List_Vector = partial(w_List, w_Vector)
e_List_Vector = e_List

r_List_List_Vector = partial(r_List, r_List_Vector)
w_List_List_Vector = partial(w_List, w_List_Vector)
e_List_List_Vector = e_List


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

set_backend_port(11004)

from PySide import QtCore
khepri_timer = QtCore.QTimer()
khepri_timer.timeout.connect(execute_current_action)
khepri_timer.start(10)
