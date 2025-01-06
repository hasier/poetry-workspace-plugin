from tomlkit.api import table
from tomlkit.items import Table
from tomlkit.toml_document import TOMLDocument

PLUGIN_SECTION = "poetry-workspace-plugin"


def get_workspaces_table(pyproject: TOMLDocument) -> Table:
    workspace_section = get_workspace_section(pyproject)
    if "workspaces" not in workspace_section:
        workspace_section["workspaces"] = table()
    return workspace_section["workspaces"]  # type: ignore


def get_workspace_section(pyproject: TOMLDocument) -> Table:
    if "tool" not in pyproject:
        # Might be missing if formatted as PEP 621
        pyproject["tool"] = table()

    tool_section = pyproject["tool"]

    if PLUGIN_SECTION not in tool_section:  # type: ignore
        tool_section[PLUGIN_SECTION] = table()  # type: ignore
    return tool_section[PLUGIN_SECTION]  # type: ignore
