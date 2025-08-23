from pathlib import Path
from .resource_registry import ResourceRegistry


ResourceRegistry.create_resource(
    Name="example_resource",
    Description="An example resource for demonstration purposes",
    content = Path.cwd().joinpath("example_resource.txt"), 
    ContentType = "file", 
    local_file = True, 
    Filetype= "txt"
        )

