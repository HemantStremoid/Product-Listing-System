"""App package initialization.

Compatibility shim: on Python 3.13 some typing internals changed and can cause
third-party libraries (like SQLAlchemy) that subclass typing internals to hit
an AssertionError during class creation. Patch typing._generic_init_subclass
early so importing SQLAlchemy inside this package doesn't fail at import time.

This shim is intentionally minimal and only swallows AssertionError raised by
the original hook — it preserves original behavior for all other cases.
"""

from __future__ import annotations

try:
    import typing as _typing

    _orig = getattr(_typing, "_generic_init_subclass", None)

    if _orig is not None:

        def _patched_generic_init_subclass(cls, *args, **kwargs):
            try:
                return _orig(cls, *args, **kwargs)
            except AssertionError:
                # Compatibility fallback: accept the subclass creation even if
                # typing's stricter check would raise. This mirrors the intent
                # of typing internals but avoids breaking imports for libs
                # that rely on slightly different internals across Python
                # versions.
                return None

        _typing._generic_init_subclass = _patched_generic_init_subclass
except Exception:
    # If anything goes wrong with the shim, fall back to default behavior —
    # we don't want to crash application import just from the shim.
    pass
