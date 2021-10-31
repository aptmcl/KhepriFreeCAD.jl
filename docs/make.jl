using KhepriFreeCAD
using Documenter

DocMeta.setdocmeta!(KhepriFreeCAD, :DocTestSetup, :(using KhepriFreeCAD); recursive=true)

makedocs(;
    modules=[KhepriFreeCAD],
    authors="António Menezes Leitão <antonio.menezes.leitao@gmail.com>",
    repo="https://github.com/aptmcl/KhepriFreeCAD.jl/blob/{commit}{path}#{line}",
    sitename="KhepriFreeCAD.jl",
    format=Documenter.HTML(;
        prettyurls=get(ENV, "CI", "false") == "true",
        canonical="https://aptmcl.github.io/KhepriFreeCAD.jl",
        assets=String[],
    ),
    pages=[
        "Home" => "index.md",
    ],
)

deploydocs(;
    repo="github.com/aptmcl/KhepriFreeCAD.jl",
)
