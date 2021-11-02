module KhepriFreeCAD
using KhepriBase
using Sockets

# functions that need specialization
include(khepribase_interface_file())
include("FreeCAD.jl")

function __init__()
  add_current_backend(freecad)
end
end
