"""Undo/redo history manager for DFT Visualizer."""
from __future__ import annotations

import copy
import logging
from dataclasses import dataclass

from src.data.models import DFTDataset

logger = logging.getLogger(__name__)


@dataclass
class AppSnapshot:
    """Immutable snapshot of full app state for undo/redo."""
    dataset: DFTDataset
    style: dict
    ui_state: dict


class HistoryManager:
    """Stack-based undo/redo manager.

    Push a new AppSnapshot after each discrete user action (debounced for
    rapid changes such as spin-box adjustments). Undo moves the current
    state to the redo stack and returns the previous state; redo reverses.
    """

    MAX_HISTORY: int = 50

    def __init__(self) -> None:
        self._undo_stack: list[AppSnapshot] = []
        self._redo_stack: list[AppSnapshot] = []

    def push(self, snapshot: AppSnapshot) -> None:
        """Save a new snapshot and clear the redo stack."""
        self._undo_stack.append(snapshot)
        if len(self._undo_stack) > self.MAX_HISTORY:
            self._undo_stack.pop(0)
        self._redo_stack.clear()
        logger.debug(
            "History push: undo_depth=%d", len(self._undo_stack)
        )

    def can_undo(self) -> bool:
        """True when there is at least one earlier state to return to."""
        return len(self._undo_stack) > 1

    def can_redo(self) -> bool:
        """True when there is a state to reapply."""
        return bool(self._redo_stack)

    def undo(self) -> AppSnapshot | None:
        """Move current state to redo stack; return the previous state.

        Returns None if there is nothing to undo.
        """
        if not self.can_undo():
            return None
        current = self._undo_stack.pop()
        self._redo_stack.append(current)
        return self._undo_stack[-1]

    def redo(self) -> AppSnapshot | None:
        """Reapply the next state from the redo stack.

        Returns None if there is nothing to redo.
        """
        if not self.can_redo():
            return None
        snapshot = self._redo_stack.pop()
        self._undo_stack.append(snapshot)
        return snapshot
