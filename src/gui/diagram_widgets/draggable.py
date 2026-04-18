"""Drag-and-drop managers for matplotlib Text and arrow artists."""
from __future__ import annotations

import logging
from typing import Callable, Optional

from matplotlib.text import Text
from PyQt6.QtCore import Qt

logger = logging.getLogger(__name__)


class DraggableTextManager:
    """Manages mouse-based dragging of matplotlib Text artists.

    Usage:
        manager = DraggableTextManager(canvas, on_change_callback)
        manager.register(text_artist, label_id)
        manager.register(text_artist_2, label_id_2)

    When the user drags a registered text, its position updates in real time
    and on_change_callback(label_id, new_xy) is called on mouse release.
    """

    def __init__(
        self,
        canvas,
        on_change: Callable[[str, tuple[float, float]], None],
    ) -> None:
        self._canvas = canvas
        self._on_change = on_change
        # id(artist) → (artist, label_id)
        self._artists: dict[int, tuple[Text, str]] = {}
        # (artist, label_id, dx_offset, dy_offset) while dragging
        self._dragging: Optional[tuple[Text, str, float, float]] = None

        self._cids = [
            canvas.mpl_connect("button_press_event", self._on_press),
            canvas.mpl_connect("motion_notify_event", self._on_motion),
            canvas.mpl_connect("button_release_event", self._on_release),
        ]

    def register(self, artist: Text, label_id: str) -> None:
        """Register a Text artist as draggable with the given label_id."""
        self._artists[id(artist)] = (artist, label_id)

    def clear(self) -> None:
        """Remove all registered artists without disconnecting canvas events."""
        self._artists.clear()
        self._dragging = None

    def disconnect(self) -> None:
        """Disconnect all canvas event handlers and clear state."""
        for cid in self._cids:
            self._canvas.mpl_disconnect(cid)
        self._cids.clear()
        self._artists.clear()
        self._dragging = None

    # ------------------------------------------------------------------
    # Canvas event handlers
    # ------------------------------------------------------------------

    def _on_press(self, event) -> None:
        if event.button != 1 or event.xdata is None:
            return
        for artist, label_id in list(self._artists.values()):
            try:
                contains, _ = artist.contains(event)
            except Exception:
                continue
            if contains:
                try:
                    x, y = artist.get_position()
                except Exception:
                    continue
                # Track offset so the text doesn't jump on drag start
                dx = x - event.xdata
                dy = y - event.ydata
                self._dragging = (artist, label_id, dx, dy)
                self._canvas.setCursor(Qt.CursorShape.SizeAllCursor)
                logger.debug("Drag started: %s at (%.3f, %.3f)", label_id, x, y)
                return

    def _on_motion(self, event) -> None:
        if event.xdata is None:
            return

        if self._dragging is not None:
            artist, _label_id, dx, dy = self._dragging
            new_x = event.xdata + dx
            new_y = event.ydata + dy
            artist.set_position((new_x, new_y))
            self._canvas.draw_idle()
            return

        # Not dragging — update cursor based on hover
        hovering = False
        for artist, _ in self._artists.values():
            try:
                contains, _ = artist.contains(event)
            except Exception:
                continue
            if contains:
                hovering = True
                break
        if hovering:
            self._canvas.setCursor(Qt.CursorShape.SizeAllCursor)
        else:
            self._canvas.unsetCursor()

    def _on_release(self, event) -> None:
        if event.button != 1 or self._dragging is None:
            return
        artist, label_id, _, _ = self._dragging
        self._dragging = None
        self._canvas.unsetCursor()

        try:
            x, y = artist.get_position()
        except Exception:
            return
        logger.debug("Drag ended: %s at (%.3f, %.3f)", label_id, x, y)
        self._on_change(label_id, (x, y))


class DraggableArrowManager:
    """Horizontal-only drag for arrow artists (absorption arrows, ISC curves).

    Unlike DraggableTextManager, this manager does NOT directly manipulate
    the artist position. Instead it fires callbacks so the diagram widget
    can update the style dict (x_offset) and trigger a redraw:

        on_drag_start(arrow_type)
        on_drag(arrow_type, delta_x)      – fired on every mouse move
        on_drag_end(arrow_type, delta_x)  – fired on mouse release

    The manager survives widget redraws: call update_artists() after each
    redraw to refresh the artist references without disturbing an active drag.
    Only horizontal motion is tracked; vertical is locked.
    """

    def __init__(
        self,
        canvas,
        on_drag_start: Callable[[str], None],
        on_drag: Callable[[str, float], None],
        on_drag_end: Callable[[str, float], None],
    ) -> None:
        self._canvas = canvas
        self._on_drag_start = on_drag_start
        self._on_drag = on_drag
        self._on_drag_end = on_drag_end
        # arrow_type -> artist
        self._artists: dict[str, object] = {}
        # (artist, arrow_type) while dragging, or None
        self._dragging: Optional[tuple[object, str]] = None
        self._drag_start_x: float = 0.0

        self._cids = [
            canvas.mpl_connect("button_press_event", self._on_press),
            canvas.mpl_connect("motion_notify_event", self._on_motion),
            canvas.mpl_connect("button_release_event", self._on_release),
        ]

    @property
    def is_dragging(self) -> bool:
        return self._dragging is not None

    def update_artists(self, artists_dict: dict[str, object]) -> None:
        """Replace the registered artists without disturbing an active drag."""
        self._artists = dict(artists_dict)

    def disconnect(self) -> None:
        for cid in self._cids:
            self._canvas.mpl_disconnect(cid)
        self._cids.clear()
        self._artists.clear()
        self._dragging = None

    # ------------------------------------------------------------------
    # Canvas event handlers
    # ------------------------------------------------------------------

    def _on_press(self, event) -> None:
        if event.button != 1 or event.xdata is None:
            return
        for arrow_type, artist in self._artists.items():
            hit = self._hit_test(artist, event)
            if hit:
                self._dragging = (artist, arrow_type)
                self._drag_start_x = event.xdata
                self._canvas.setCursor(Qt.CursorShape.SizeHorCursor)
                self._on_drag_start(arrow_type)
                logger.debug("Arrow drag started: %s", arrow_type)
                return

    def _on_motion(self, event) -> None:
        if event.xdata is None:
            return
        if self._dragging is not None:
            _, arrow_type = self._dragging
            delta_x = event.xdata - self._drag_start_x
            self._on_drag(arrow_type, delta_x)
            return
        # Hover cursor
        for artist in self._artists.values():
            if self._hit_test(artist, event):
                self._canvas.setCursor(Qt.CursorShape.SizeHorCursor)
                return
        self._canvas.unsetCursor()

    def _on_release(self, event) -> None:
        if event.button != 1 or self._dragging is None:
            return
        _, arrow_type = self._dragging
        self._dragging = None  # clear BEFORE callback so is_dragging=False
        self._canvas.unsetCursor()
        delta_x = (event.xdata or self._drag_start_x) - self._drag_start_x
        logger.debug("Arrow drag ended: %s delta_x=%.3f", arrow_type, delta_x)
        self._on_drag_end(arrow_type, delta_x)

    @staticmethod
    def _hit_test(artist, event) -> bool:
        """Return True if *event* falls on *artist*, trying multiple methods."""
        if event.xdata is None:
            return False
        try:
            contains, _ = artist.contains(event)
            return contains
        except Exception:
            pass
        # Fallback for FancyArrowPatch: test via contains_point on display coords
        try:
            return bool(artist.contains_point([event.x, event.y], radius=5.0))
        except Exception:
            return False
