```@meta
CurrentModule = KhepriFreeCAD
```

# KhepriFreeCAD

A Khepri backend for [FreeCAD](https://www.freecad.org/), communicating via a Python plugin over TCP (port 11004).

## Architecture

KhepriFreeCAD is a **SocketBackend** using the `:PY` (Python) binary protocol. Julia sends commands to a Python server script running inside FreeCAD's embedded Python interpreter.

- **Backend type**: `SocketBackend{FRCADKey, Union{Int32, String}}`
- **Reference IDs**: `Int32` for shapes/materials, `String` for collections
- **CSG references**: `FRCADUnionRef` and `FRCADSubtractionRef` for boolean operations

## Key Features

- **Draft workbench**: Circle, spline, and 2D geometry via FreeCAD's Draft module
- **Parametric design**: Full Part workbench integration with boolean operations
- **Headless batch processing**: Enabled via `headless_freecad()` parameter
- **FreeCADKit materials**: Material support through FreeCAD's material library
- **Collections**: Uses FreeCAD's collection system instead of traditional layers
- **OBJ mesh export**: Mesh-based geometry output support

## Setup

```julia
using KhepriFreeCAD
using KhepriBase

backend(freecad)

sphere(xyz(0, 0, 0), 5)
box(xyz(10, 0, 0), 5, 5, 5)
```

Requires FreeCAD with the Khepri Python plugin running. Set `headless_freecad(true)` for batch mode.

## Dependencies

- **KhepriBase**: Core Khepri functionality
- **Sockets**: TCP communication

```@index
```

```@autodocs
Modules = [KhepriFreeCAD]
```
