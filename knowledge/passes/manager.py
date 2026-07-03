"""Pass manager — orchestrates compiler pass execution.

The pass manager is responsible for:
- Registering compiler passes.
- Resolving execution order via topological sort.
- Executing passes in dependency order.
- Collecting diagnostics across all passes.
- Collecting scores from scoring passes.
- Detecting circular dependencies and missing dependencies.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from knowledge.models import KnowledgeGraph
from knowledge.passes.base import CompilerPass, KnowledgeScore, PassResult, Phase
from knowledge.passes.diagnostics import Diagnostic


class PipelineResult(BaseModel, frozen=True):
    """The result of executing a full pipeline of compiler passes."""

    graph: KnowledgeGraph
    diagnostics: list[Diagnostic] = Field(default_factory=list)
    execution_order: list[str] = Field(default_factory=list)
    executed: list[str] = Field(default_factory=list)
    score: KnowledgeScore | None = None
    total_repairs: int = 0


class PassManager:
    """Orchestrates registration, dependency resolution, and execution
    of compiler passes.
    """

    def __init__(self) -> None:
        """Initialize an empty pass manager."""
        self.passes: dict[str, CompilerPass] = {}

    @property
    def registered_ids(self) -> list[str]:
        """Return the IDs of all registered passes.

        Returns:
            List of pass ID strings in registration order.
        """
        return list(self.passes.keys())

    def register(self, pass_: CompilerPass) -> None:
        """Register a compiler pass.

        Args:
            pass_: An instance of a CompilerPass subclass.

        Raises:
            ValueError: If the pass has an empty id, no phase,
                or a duplicate id.
        """
        if not pass_.id:
            raise ValueError("Pass must have a non-empty id")
        if not isinstance(pass_.phase, Phase):
            raise ValueError(f"Pass {pass_.id} must have a valid phase")
        if pass_.id in self.passes:
            raise ValueError(f"Pass already registered: {pass_.id}")
        self.passes[pass_.id] = pass_

    def resolve_order(self, phases: list[Phase] | None = None) -> list[str]:
        """Resolve a topological execution order.

        Uses Kahn's algorithm to produce a total order that respects
        all declared dependencies.

        Args:
            phases: Optional filter to only include passes in the
                given phases. If None, all registered passes are
                included.

        Returns:
            List of pass IDs in execution order.

        Raises:
            ValueError: If a dependency is unknown or a circular
                dependency is detected.
        """
        candidates = {
            pid: p for pid, p in self.passes.items() if phases is None or p.phase in phases
        }

        if not candidates:
            return []

        # Build adjacency list: edges[dep] = {pid_1, pid_2, ...}
        # meaning dep must run before these passes.
        edges: dict[str, set[str]] = {pid: set() for pid in candidates}
        in_degree: dict[str, int] = {pid: 0 for pid in candidates}

        for pid, pass_ in candidates.items():
            for dep in pass_.depends_on:
                if dep not in candidates:
                    raise ValueError(f"Unknown dependency '{dep}' required by pass '{pid}'")
                edges[dep].add(pid)
                in_degree[pid] += 1

        queue = [pid for pid, deg in in_degree.items() if deg == 0]
        order: list[str] = []

        while queue:
            pid = queue.pop(0)
            order.append(pid)
            for dependent in edges[pid]:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)

        if len(order) != len(candidates):
            raise ValueError("Circular dependency detected among passes")

        return order

    def execute(
        self,
        graph: KnowledgeGraph,
        config: dict[str, Any] | None = None,
        phases: list[Phase] | None = None,
    ) -> PipelineResult:
        """Execute registered passes in dependency order.

        Args:
            graph: The initial KnowledgeGraph to process.
            config: Optional top-level configuration. Pass-specific
                config is looked up by pass id.
            phases: Optional filter to only execute passes in the
                given phases.

        Returns:
            A PipelineResult with the final graph, collected
            diagnostics, and execution metadata.
        """
        order = self.resolve_order(phases=phases)
        all_diagnostics: list[Diagnostic] = []
        current_graph = graph
        executed: list[str] = []
        collected_score: KnowledgeScore | None = None
        total_repairs = 0

        for pid in order:
            pass_ = self.passes[pid]
            pass_config = (config or {}).get(pass_.id, {})
            result: PassResult = pass_.execute(current_graph, pass_config)
            current_graph = result.graph
            all_diagnostics.extend(result.diagnostics)
            executed.append(pid)
            if result.score is not None:
                collected_score = result.score
            total_repairs += result.repairs_applied

        return PipelineResult(
            graph=current_graph,
            diagnostics=all_diagnostics,
            execution_order=order,
            executed=executed,
            score=collected_score,
            total_repairs=total_repairs,
        )
