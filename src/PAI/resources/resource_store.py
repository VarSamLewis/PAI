from pathlib import Path
from .resource_registry import ResourceRegistry


ResourceRegistry.create_resource(
    Name="example_resource",
    Description="An example resource for demonstration purposes",
    content=Path.cwd().joinpath("example_resource.txt"),
    ContentType="file",
    local_file=True,
    Filetype="txt",
)

ResourceRegistry.create_resource(
    Name="Sam's Cake Preferences",
    Description="A string containing Sam's preferences for cake flavors and types",
    content="Sam likes most cakes but likes red velvet the most of all",
    ContentType="string",
    local_file=False,
    Filetype=None,
)
