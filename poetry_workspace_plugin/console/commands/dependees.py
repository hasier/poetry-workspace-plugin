from collections import defaultdict
from functools import cached_property
from pathlib import Path

from cleo.helpers import argument, option
from poetry.console.commands.command import Command
from poetry.core.factory import Factory

from poetry_workspace_plugin.helpers import get_workspaces_table

# TODO: group dependees?


class WorkspaceDependeesCommand(Command):
    name = "workspace dependees"
    description = "List workspaces which depend on the specified workspaces."

    arguments = [argument("targets", "The workspaces to compute dependees of, by name", multiple=True)]
    options = [
        option("no-transitive", None, "Only show the immediate dependees", flag=True),
        option("csv", None, "Return comma-separated list", flag=True),
    ]

    def handle(self) -> int:
        targets = set(self.argument("targets"))
        transitive = not self.option("no-transitive")
        workspaces = get_workspaces_table(self.poetry.file.read())
        if unexpected := (targets - set(workspaces)):
            self.line_error(
                f"<fg=red>Unknown workspace{'s' if len(unexpected) > 1 else ''}:"
                f" <options=bold>{', '.join(unexpected)}</></>"
            )
            return 1
        dependees = targets.union(*[self._find_dependees(name, transitive=transitive) for name in targets])

        sorted_dependees = sorted(dependees)

        if self.option("csv"):
            self.line(",".join(sorted_dependees))
            return 0

        for dependee in sorted_dependees:
            self.line(dependee)
        return 0

    def _find_dependees(self, name: str, transitive: bool = True, visited: set[str] | None = None) -> set[str]:
        visited = visited or set()
        dependees = self._dependee_map[name]
        if not transitive or name in visited:
            return dependees
        visited.add(name)
        for dependee in set(dependees):
            dependees |= self._find_dependees(dependee, visited=visited)
        return dependees

    @cached_property
    def _dependee_map(self) -> dict[str, set[str]]:
        result = defaultdict(set)
        for name in self._workspaces:
            for dependency_name in self._get_workspace_direct_dependencies(name):
                result[dependency_name].add(name)
        return result

    def _get_workspace_direct_dependencies(self, name: str) -> set[str]:
        path = Path(self._workspaces[name])
        poetry = Factory().create_poetry(cwd=path)
        result = set()
        for dependency in poetry.package.all_requires:
            if dependency.source_type == "directory" and dependency.source_url:
                target_path = Path(dependency.source_url)
                if target_path in self._workspace_absolute_paths:
                    result.add(self._workspace_absolute_paths[target_path])
        return result

    @cached_property
    def _workspace_absolute_paths(self) -> dict[Path, str]:
        return {Path(path).resolve(): name for name, path in self._workspaces.items()}

    @cached_property
    def _workspaces(self) -> dict[str, str]:
        return get_workspaces_table(self.poetry.file.read())
