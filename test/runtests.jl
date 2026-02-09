# KhepriFreeCAD tests — FreeCAD SocketBackend via Python plugin
#
# Tests cover module loading, type system, backend configuration,
# and ref type aliases. Actual FreeCAD operations require a running
# FreeCAD instance with the KhepriServer Python plugin.

using KhepriFreeCAD
using KhepriBase
using Test

@testset "KhepriFreeCAD.jl" begin

  @testset "Type system" begin
    @test isdefined(KhepriFreeCAD, :FRCADKey)
    @test KhepriFreeCAD.FRCADId === Union{Int32, String}
    @test isdefined(KhepriFreeCAD, :FRCADRef)
    @test isdefined(KhepriFreeCAD, :FRCADEmptyRef)
    @test isdefined(KhepriFreeCAD, :FRCADUnionRef)
    @test isdefined(KhepriFreeCAD, :FRCADSubtractionRef)
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
end
