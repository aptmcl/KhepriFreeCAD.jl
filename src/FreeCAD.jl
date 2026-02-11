# Blender
export freecad

#=

To dribble Blender, do:

freecad_exe_path = raw"C:\Program Files\Blender Foundation\Blender 2.91\freecad.exe"
using OutputCollectors
oc = OutputCollector(`$freecad_exe_path $["--python", joinpath(@__DIR__, "KhepriServer.py")]`, verbose=true)
=#

#=
=#

# FRC is a subtype of Python
parse_signature(::Val{:FRCAD}, sig::T) where {T} = parse_signature(Val(:PY), sig)
encode(::Val{:FRCAD}, t::Val{T}, c::IO, v) where {T} = encode(Val(:PY), t, c, v)
decode(::Val{:FRCAD}, t::Val{T}, c::IO) where {T} = decode(Val(:PY), t, c)
encode(ns::Val{:FRCAD}, t::Tuple{T1,T2,T3}, c::IO, v) where {T1,T2,T3} =
  begin
    encode(ns, T1(), c, v[1])
    encode(ns, T2(), c, v[2])
    encode(ns, T3(), c, v[3])
  end
decode(ns::Val{:FRCAD}, t::Tuple{T1,T2,T3}, c::IO) where {T1,T2,T3} =
  (decode(ns, T1(), c),
   decode(ns, T2(), c),
   decode(ns, T3(), c))

@encode_decode_as(:FRCAD, Val{:Id}, Val{:size})
@encode_decode_as(:FRCAD, Val{:MatId}, Val{:size})
@encode_decode_as(:FRCAD, Val{:Length}, Val{:float})

encode(::Val{:FRCAD}, t::Union{Val{:Point3d},Val{:Vector3d}}, c::IO, p) =
  encode(Val(:PY), Val(:float3), c, raw_point(p))
decode(::Val{:FRCAD}, t::Val{:Point3d}, c::IO) =
  xyz(decode(Val(:PY), Val(:float3), c)..., world_cs)
decode(::Val{:FRCAD}, t::Val{:Vector3d}, c::IO) =
  vxyz(decode(Val(:PY), Val(:float3), c)..., world_cs)

encode(ns::Val{:FRCAD}, t::Val{:Frame3d}, c::IO, v) = begin
  encode(ns, Val(:Point3d), c, v)
  t = v.cs.transform
  encode(Val(:PY), Val(:float3), c, (t[1,1], t[2,1], t[3,1]))
  encode(Val(:PY), Val(:float3), c, (t[1,2], t[2,2], t[3,2]))
  encode(Val(:PY), Val(:float3), c, (t[1,3], t[2,3], t[3,3]))
end

decode(ns::Val{:FRCAD}, t::Val{:Frame3d}, c::IO) =
  u0(cs_from_o_vx_vy_vz(
      decode(ns, Val(:Point3d), c),
      decode(ns, Val(:Vector3d), c),
      decode(ns, Val(:Vector3d), c),
      decode(ns, Val(:Vector3d), c)))

freecad_api = @remote_api :FRCAD """
def find_or_create_collection(name:str, active:bool, color:RGBA)->str:
def get_current_collection()->str:
def set_current_collection(name:str)->None:
def delete_all_shapes_in_collection(name:str)->None:
def delete_all_shapes()->None:
def delete_shape(name:Id)->None:
def select_shape(name:Id)->None:
def deselect_shape(name:Id)->None:
def deselect_all_shapes()->None:
def get_material(name:str)->MatId:
def get_freecadkit_material(ref:str)->MatId:
def new_material(name:str, diffuse_color:RGBA, metallic:float, specular:float, roughness:float, clearcoat:float, clearcoat_roughness:float, ior:float, transmission:float, transmission_roughness:float, emission:RGBA, emission_strength:float)->MatId:
def new_metal_material(name:str, color:RGBA, roughness:float, ior:float)->MatId:
def new_glass_material(name:str, color:RGBA, roughness:float, ior:float)->MatId:
def new_mirror_material(name:str, color:RGBA)->MatId:
def line(ps:List[Point3d], closed:bool, mat:MatId)->Id:
def draft_circle(c:Point3d, v:Vector3d, r:Length, mat:MatId)->Id:
def draft_spline(ps:List[Point3d], closed:bool, mat:MatId)->Id:
def objmesh(verts:List[Point3d], edges:List[Tuple[int,int]], faces:List[List[int]], smooth:bool, mat:MatId)->Id:
def trig(p1:Point3d, p2:Point3d, p3:Point3d, mat:MatId)->Id:
def quad(p1:Point3d, p2:Point3d, p3:Point3d, p4:Point3d, mat:MatId)->Id:
def quad_strip(ps:List[Point3d], qs:List[Point3d], smooth:bool, mat:MatId)->Id:
def quad_strip_closed(ps:List[Point3d], qs:List[Point3d], smooth:bool, mat:MatId)->Id:
def ngon(ps:List[Point3d], pivot:Point3d, smooth:bool, mat:MatId)->Id:
def polygon(ps:List[Point3d], mat:MatId)->Id:
def polygon_with_holes(pss:List[List[Point3d]], mat:MatId)->Id:
def quad_surface(ps:List[Point3d], nu:int, nv:int, closed_u:bool, closed_v:bool, smooth:bool, mat:MatId)->Id:
def circle(c:Point3d, v:Vector3d, r:Length, mat:MatId)->Id:
def cuboid(verts:List[Point3d], mat:MatId)->Id:
def pyramid_frustum(bs:List[Point3d], ts:List[Point3d], smooth:bool, bmat:MatId, tmat:MatId, smat:MatId)->Id:
def sphere(center:Point3d, radius:Length, mat:MatId)->Id:
def cone_frustum(b:Point3d, br:Length, t:Point3d, tr:Length, bmat:MatId, tmat:MatId, smat:MatId)->Id:
def box(p:Point3d, vx:Vector3d, vy:Vector3d, dx:Length, dy:Length, dz:Length, mat:MatId)->Id:
def text(txt:str, p:Point3d, vx:Vector3d, vy:Vector3d, size:float)->Id:
def area_light(p:Point3d, v:Vector3d, size:float, color:RGBA, strength:float)->Id:
def sun_light(p:Point3d, v:Vector3d)->Id:
def light(p:Point3d, type:str)->Id:
def camera_from_view()->None:
def set_view(camera:Point3d, target:Point3d, lens:float)->None:
def get_view()->Tuple[Point3d, Point3d, float]:
def set_render_size(width:int, height:int)->None:
def set_render_path(filepath:str)->None:
def default_renderer()->None:
def cycles_renderer(samples:int, denoising:bool, motion_blur:bool, transparent:bool, exposure:float)->None:
def freestylesvg_renderer(thickness:float, crease_angle:float)->None:
def clay_renderer(samples:int, denoising:bool, motion_blur:bool, transparent:bool)->None:
def set_sun(latitude:float, longitude:float, elevation:float, year:int, month:int, day:int, time:float, UTC_zone:float, use_daylight_savings:bool)->None:
def set_sky(turbidity:float)->None:
def set_max_repeated(n:Int)->Int:
def freecad_cmd(expr:str)->None:
def wall(ps:List[Point3d], height:Length, align:str, mat:MatId)->Id:
"""

abstract type FRCADKey end
const FRCADId = Union{Int32,String} # Although shapes and materials are ints, layers are strings
const FRCADIds = Vector{FRCADId}
const FRCADRef = NativeRef{FRCADKey, FRCADId}
const FRCADRefs = Vector{FRCADRef}
const FRCAD = SocketBackend{FRCADKey, FRCADId}

const KhepriServerPath = Parameter(abspath(@__DIR__, "FreeCADServer.py"))
export headless_freecad
const headless_freecad = Parameter(false)
const starting_freecad = Parameter(false)

start_freecad() =
  starting_freecad() ?
    sleep(1) : # Just wait a little longer
    let freecad_cmd = Sys.iswindows() ?
		  let versions = filter(p->!isnothing(match(r"FreeCAD", p)), readdir("C:/Program Files/", join=true))
			isempty(versions) ?
			  error("Could not find FreeCAD!") :
			  joinpath(versions[1], "bin/FreeCAD.exe")
		  end :
    	  "freecad"
	  starting_freecad(true)
      run(detach(headless_freecad() ?
            `$(freecad_cmd) -P $(@__DIR__) --console $(KhepriServerPath())` :
      	    `$(freecad_cmd) -P $(@__DIR__) $(KhepriServerPath())`),
    	  wait=false)
    end

#
#=
To support reload in FreeCAD, redefine:

start_freecad() =
  starting_freecad() ?
    sleep(1) : # Just wait a little longer
    let start = abspath(@__DIR__, "StartKhepri.py"),
		    freecad_cmd = Sys.iswindows() ?
		      let versions = filter(p->!isnothing(match(r"FreeCAD", p)), readdir("C:/Program Files/", join=true))
			      isempty(versions) ?
			        error("Could not find FreeCAD!") :
			        joinpath(versions[1], "bin/FreeCAD.exe")
		      end :
    	    "freecad"
	  starting_freecad(true)
      run(detach(headless_freecad() ?
            `$(freecad_cmd) -P $(@__DIR__) --console $(start)` :
      	    `$(freecad_cmd) -P $(@__DIR__) $(start)`),
    	  wait=false)
    end
=#



KhepriBase.retry_connecting(b::FRCAD) =
  (@info("Starting $(b.name)."); start_freecad(); sleep(2))

KhepriBase.after_connecting(b::FRCAD) =
  begin
	starting_freecad(false)
	# #set_material(b, material_basic, )
	# set_material(b, material_metal, "asset_base_id:f1774cb0-b679-46b4-879e-e7223e2b4b5f asset_type:material")
	# #set_material(b, material_glass, "asset_base_id:ee2c0812-17f5-40d4-992c-68c5a66261d7 asset_type:material")
	# set_material(b, material_glass, "asset_base_id:ffa3c281-6184-49d8-b05e-8c6e9fe93e68 asset_type:material")
	# set_material(b, material_wood, "asset_base_id:d5097824-d5a1-4b45-ab5b-7b16bdc5a627 asset_type:material")
	# #set_material(b, material_concrete, "asset_base_id:0662b3bf-a762-435d-9407-e723afd5eafc asset_type:material")
	# set_material(b, material_concrete, "asset_base_id:df1161da-050c-4638-b376-38ced992ec18 asset_type:material")
	# set_material(b, material_plaster, "asset_base_id:c674137d-cfae-45f1-824f-e85dc214a3af asset_type:material")
	#
	# #set_material(b, material_grass, "asset_base_id:97b171b4-2085-4c25-8793-2bfe65650266 asset_type:material")
	# #set_material(b, material_grass, "asset_base_id:7b05be22-6bed-4584-a063-d0e616ddea6a asset_type:material")
	# set_material(b, material_grass, "asset_base_id:b4be2338-d838-433b-9f0d-2aa9b97a0a8a asset_type:material")
	# set_material(b, material_clay, b -> b_plastic_material(b, "Clay", rgb(0.9, 0.9, 0.9),	1.0))
	# We will use the same view as Rhino
	b_set_view(b, xyz(43.11,-74.67,49.78), xyz(-0.19,0.33,-0.22), 50, 22)
  end

const freecad = FRCAD("FreeCAD", freecad_port, freecad_api)

KhepriBase.has_boolean_ops(::Type{FRCAD}) = HasBooleanOps{true}()

KhepriBase.backend(::FRCADRef) = freecad
KhepriBase.void_ref(b::FRCAD) = -1 % Int32

# Primitives

KhepriBase.b_line(b::FRCAD, ps, mat) =
  @remote(b, line(ps, false, mat))

KhepriBase.b_polygon(b::FRCAD, ps, mat) =
  @remote(b, line(ps, true, mat))

KhepriBase.b_spline(b::FRCAD, ps, v1, v2, mat) =
  #HACK: ignoring v1, v2
  @remote(b, draft_spline(ps, false, mat))

KhepriBase.b_closed_spline(b::FRCAD, ps, mat) =
  @remote(b, draft_spline(ps, true, mat))

KhepriBase.b_trig(b::FRCAD, p1, p2, p3, mat) =
  @remote(b, trig(p1, p2, p3, mat))

KhepriBase.b_quad(b::FRCAD, p1, p2, p3, p4, mat) =
	@remote(b, quad(p1, p2, p3, p4, mat))

KhepriBase.b_ngon(b::FRCAD, ps, pivot, smooth, mat) =
	@remote(b, ngon(ps, pivot, smooth, mat))

KhepriBase.b_quad_strip(b::FRCAD, ps, qs, smooth, mat) =
  @remote(b, quad_strip(ps, qs, smooth, mat))

KhepriBase.b_quad_strip_closed(b::FRCAD, ps, qs, smooth, mat) =
  @remote(b, quad_strip_closed(ps, qs, smooth, mat))

KhepriBase.b_surface_polygon(b::FRCAD, ps, mat) =
  @remote(b, polygon(ps, mat))

KhepriBase.b_surface_polygon_with_holes(b::FRCAD, ps, qss, mat) =
  @remote(b, polygon_with_holes([ps, qss...], mat))

KhepriBase.b_surface_circle(b::FRCAD, c, r, mat) =
  @remote(b, circle(c, vz(1, c.cs), r, mat))

KhepriBase.b_surface_grid(b::FRCAD, ptss, closed_u, closed_v, smooth_u, smooth_v, mat) =
  let (nu, nv) = size(ptss)
	smooth_u && smooth_v ?
	  @remote(b, quad_surface(vcat(ptss...), nu, nv, closed_u, closed_v, true, mat)) :
	  smooth_u ?
	  	(closed_u ?
          vcat([b_quad_strip_closed(b, ptss[:,i], ptss[:,i+1], true, mat) for i in 1:nv-1],
	           closed_v ? [b_quad_strip_closed(b, ptss[:,end], ptss[:,1], true, mat)] : []) :
	      vcat([b_quad_strip(b, ptss[:,i], ptss[:,i+1], true, mat) for i in 1:nv-1],
	           closed_v ? [b_quad_strip(b, ptss[:,end], ptss[:,1], true, mat)] : [])) :
 	    (closed_v ?
           vcat([b_quad_strip_closed(b, ptss[i,:], ptss[i+1,:], smooth_v, mat) for i in 1:nu-1],
  	         	closed_u ? [b_quad_strip_closed(b, ptss[end,:], ptss[1,:], smooth_v, mat)] : []) :
  	       vcat([b_quad_strip(b, ptss[i,:], ptss[i+1,:], smooth_v, mat) for i in 1:nu-1],
  	          	closed_u ? [b_quad_strip(b, ptss[end,:], ptss[1,:], smooth_v, mat)] : []))
  end

KhepriBase.b_generic_pyramid_frustum(b::FRCAD, bs, ts, smooth, bmat, tmat, smat) =
  @remote(b, pyramid_frustum(bs, ts, smooth, bmat, tmat, smat))

KhepriBase.b_cone(b::FRCAD, cb, r, h, bmat, smat) =
  @remote(b, cone_frustum(cb, r, add_z(cb, h), 0, bmat, bmat, smat))

KhepriBase.b_cone_frustum(b::FRCAD, cb, rb, h, rt, bmat, tmat, smat) =
  @remote(b, cone_frustum(cb, rb, add_z(cb, h), rt, bmat, tmat, smat))

KhepriBase.b_cylinder(b::FRCAD, cb, r, h, bmat, tmat, smat) =
  @remote(b, cone_frustum(cb, r, add_z(cb, h), r, bmat, tmat, smat))

KhepriBase.b_box(b::FRCAD, c, dx, dy, dz, mat) =
  @remote(b, box(c, vx(1, c.cs), vy(1, c.cs), dx, dy, dz, mat))

KhepriBase.b_cuboid(b::FRCAD, pb0, pb1, pb2, pb3, pt0, pt1, pt2, pt3, mat) =
  @remote(b, cuboid([pb0, pb1, pb2, pb3, pt0, pt1, pt2, pt3], mat))

KhepriBase.b_sphere(b::FRCAD, c, r, mat) =
  @remote(b, sphere(c, r, mat))


# BIM

KhepriBase.b_wall(b::FRCAD, w_path, w_height, family, offset, openings) =
  path_length(w_path) < path_tolerance() ?
  	void_ref(b) :
    @remote(b, wall(path_vertices(w_path), w_height, "Center", -1))




# Materials

KhepriBase.b_get_material(b::FRCAD, spec::AbstractString) =
  startswith(spec, "asset_base_id") ?
    @remote(b, get_freecadkit_material(spec)) :
    @remote(b, get_material(spec))

KhepriBase.b_get_material(b::FRCAD, spec::Function) = spec(b)

#=
Important source of materials:

1. Activate Blender's freecadkit addon:
https://www.freecadkit.com/get-freecadkit/

2. Browse BlenderKit's material database:
https://www.freecadkit.com/asset-gallery?query=category_subtree:material

3. Select material and copy reference, e.g.:
asset_base_id:ced25dc0-d461-42f7-aa03-85cb88f671a1 asset_type:material

4. Install material and retrive its id with:
b_get_material(freecad, "asset_base_id:ced25dc0-d461-42f7-aa03-85cb88f671a1 asset_type:material")
=#

KhepriBase.b_new_material(b::FRCAD, name,
						  base_color,
						  metallic, specular, roughness,
	                 	  clearcoat, clearcoat_roughness,
						  ior,
						  transmission, transmission_roughness,
	                 	  emission_color,
						  emission_strength) =
  @remote(b, new_material(name,
  						  convert(RGBA, base_color),
						  metallic, specular, roughness,
  						  clearcoat, clearcoat_roughness,
  				  		  ior,
  				  		  transmission, transmission_roughness,
						  convert(RGBA, emission_color), emission_strength))

KhepriBase.b_plastic_material(b::FRCAD, name, color, roughness) =
  @remote(b, new_material(name, convert(RGBA, color), 0.0, 1.0, roughness, 0.0, 0.0, 1.4, 0.0, 0.0, RGBA(0.0, 0.0, 0.0, 1.0), 0.0))

KhepriBase.b_metal_material(b::FRCAD, name, color, roughness, ior) =
  @remote(b, new_metal_material(name, convert(RGBA, color), roughness, ior))

KhepriBase.b_glass_material(b::FRCAD, name, color, roughness, ior) =
  @remote(b, new_glass_material(name, convert(RGBA, color), roughness, ior))

KhepriBase.b_mirror_material(b::FRCAD, name, color) =
  @remote(b, new_mirror_material(name, convert(RGBA, color)))

#KhepriBase.b_translucent_material(b::FRCAD, name, diffuse, specular, roughness, reflect, transmit, bump_map)
#KhepriBase.b_substrate_material(name, diffuse, specular, roughness, bump_map)

#=

Default families

=#
export freecad_family_materials
freecad_family_materials(m1, m2=m1, m3=m2, m4=m3) = (materials=(m1, m2, m3, m4), )

KhepriBase.b_layer(b::FRCAD, name, active, color) =
  @remote(b, find_or_create_collection(name, active, color))
KhepriBase.b_current_layer_ref(b::FRCAD) =
  @remote(b, get_current_collection())
KhepriBase.b_current_layer_ref(b::FRCAD, layer) =
  @remote(b, set_current_collection(layer))
KhepriBase.b_all_shapes_in_layer(b::FRCAD, layer) =
  @remote(b, all_shapes_in_collection(layer))
KhepriBase.b_delete_all_shapes_in_layer(b::FRCAD, layer) =
  @remote(b, delete_all_shapes_in_collection(layer))

KhepriBase.b_set_view(b::FRCAD, camera::Loc, target::Loc, lens::Real, aperture::Real) =
  @remote(b, set_view(camera, target, lens))

KhepriBase.b_get_view(b::FRCAD) =
  @remote(b, get_view())

KhepriBase.b_zoom_extents(b::FRCAD) = @remote(b, ZoomExtents())

KhepriBase.b_set_view_top(b::FRCAD) = @remote(b, ViewTop())

# KhepriBase.b_set_time_place(b::FRCAD, date, latitude, longitude, elevation, meridian) =
#   @remote(b, set_sun(latitude, longitude, elevation, year(date), month(date), day(date), hour(date)+minute(date)/60, meridian, false))
#
# KhepriBase.b_set_sky(b::FRCAD, turbidity, sun) =
#   @remote(b, set_sky(turbidity)) #Add withsun

KhepriBase.b_delete_ref(b::FRCAD, r::FRCADId) =
  @remote(b, delete_shape(r))

KhepriBase.b_delete_all_shape_refs(b::FRCAD) =
  @remote(b, delete_all_shapes())

####################

KhepriBase.b_highlight_ref(b::FRCAD, r::FRCADId) =
  @remote(b, select_shape(r))

KhepriBase.b_unhighlight_ref(b::FRCAD, r::FRCADId) =
  @remote(b, deselect_shape(r))

KhepriBase.b_unhighlight_all_refs(b::FRCAD) =
  @remote(b, deselect_all_shapes())

KhepriBase.b_render_and_save_view(b::FRCAD, path::String) =
  let (camera, target, lens) = @remote(b, get_view())
    @remote(b, set_camera_view(camera, target, lens))
    @remote(b, set_render_size(render_width(), render_height()))
    @remote(b, set_render_path(path))
  	@remote(b, cycles_renderer(1200, true, false, false, render_exposure()))
  end

export render_svg
render_svg(b::FRCAD, path) =
  let (camera, target, lens) = @remote(b, get_view())
    @remote(b, set_camera_view(camera, target, lens))
    @remote(b, set_render_size(render_width(), render_height()))
    @remote(b, set_render_path(path))
    @remote(b, freestylesvg_renderer(1.0, deg2rad(135), 0.001, 0.0))
  end

#=
with_clay_model(f, level::Real=0) =
  begin
  	with(f, default_material, material_clay)
	area_light
=#
