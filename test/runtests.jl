# KhepriFreeCAD tests — FreeCAD SocketBackend via Python plugin
#
# Tests cover module loading, type system, backend configuration,
# and ref type aliases. Actual FreeCAD operations require a running
# FreeCAD instance with the KhepriServer Python plugin.

using KhepriFreeCAD
using KhepriBase
using KhepriBase: SocketBackend, NativeRef
using Test

@testset "KhepriFreeCAD.jl" begin

  @testset "Type system" begin
    @test isdefined(KhepriFreeCAD, :FRCADKey)
    @test KhepriFreeCAD.FRCADId === Union{Int32, String}
    @test isdefined(KhepriFreeCAD, :FRCADRef)
    @test KhepriFreeCAD.FRCADRef === NativeRef{KhepriFreeCAD.FRCADKey, Union{Int32, String}}
    @test KhepriFreeCAD.FRCAD === SocketBackend{KhepriFreeCAD.FRCADKey, Union{Int32, String}}
  end

  @testset "Backend initialization" begin
    @test freecad isa KhepriBase.Backend
    @test KhepriBase.backend_name(freecad) == "FreeCAD"
    @test KhepriBase.void_ref(freecad) === Int32(-1)
  end

  @testset "Configuration parameters" begin
    @test KhepriFreeCAD.headless_freecad isa KhepriBase.Parameter
    @test headless_freecad() isa Bool
  end

  @testset "Exported helpers" begin
    @test isdefined(KhepriFreeCAD, :freecad_family_materials)
  end

  @testset "Exact geometry capabilities" begin
    @test KhepriBase.supports_exact_interpolating_spline_curves(KhepriFreeCAD.FRCAD)
    @test KhepriBase.supports_exact_bezier_curves(KhepriFreeCAD.FRCAD)
    @test KhepriBase.supports_exact_bspline_curves(KhepriFreeCAD.FRCAD)
    @test KhepriBase.supports_exact_nurbs_curves(KhepriFreeCAD.FRCAD)
    @test !KhepriBase.supports_exact_polycurves(KhepriFreeCAD.FRCAD)
    @test KhepriBase.supports_exact_bezier_surfaces(KhepriFreeCAD.FRCAD)
    @test KhepriBase.supports_exact_bspline_surfaces(KhepriFreeCAD.FRCAD)
    @test KhepriBase.supports_exact_nurbs_surfaces(KhepriFreeCAD.FRCAD)
    @test !KhepriBase.supports_exact_trimmed_surfaces(KhepriFreeCAD.FRCAD)
  end

  @testset "Backend import mapping" begin
    report = KhepriBase.backend_geometry_mapping(freecad)
    @test report.import_mapping.storage == :remote_refs
    @test report.import_mapping.all_shapes
    @test report.import_mapping.create_shape
    @test report.operations.closest_points_path_path
    @test report.operations.project_point_surface
    @test report.operations.classify_region_point
  end

  if get(ENV, "KHEPRI_FREECAD_EXACT_GEOMETRY_TESTS", "0") == "1"
    @testset "Exact Geometry (FreeCAD)" begin
      include(joinpath(dirname(pathof(KhepriBase)), "..", "test", "ExactGeometrySmokeTests.jl"))
      using .ExactGeometrySmokeTests

      delete_all_shapes()
      backend(freecad)
      run_exact_geometry_smoke_tests(freecad; verify_samples=false, verify_surface_samples=false)
    end
  end
end
