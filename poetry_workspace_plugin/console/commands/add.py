from pathlib import Path

from cleo.helpers import argument
from poetry.console.commands.command import Command
from poetry.core.factory import Factory

from poetry_workspace_plugin.helpers import get_workspaces_table


class WorkspaceAddCommand(Command):
    name = "workspace add"
    description = "Begins tracking an existing Python project at <path> as a workspace."

    arguments = [argument("path", "The path to the Python project")]

    def handle(self) -> int:

        # Check path is a valid project
        path = Path(self.argument("path"))
        name = self._get_target_project_name(path)

        # Read current pyproject.toml
        content = self.poetry.file.read()

        workspaces = get_workspaces_table(content)

        # Check that name is already used
        if name in workspaces:
            self.line(f"<fg=red>Workspace already registered with name <options=bold>{name}</></>")
            return 1

        # Add the new workspace to current pyproject.toml
        workspaces[name] = str(path)
        self.poetry.file.write(content)
        return 0

    @staticmethod
    def _get_target_project_name(path: Path) -> str:
        if not path.exists():
            raise RuntimeError(f"Path {str(path)!r} does not exist.")

        poetry_file = path / "pyproject.toml"
        if not poetry_file.exists():
            raise RuntimeError(f"Poetry could not find a pyproject.toml file in {str(path)!r}.")

        poetry = Factory().create_poetry(path)
        return poetry.package.name
