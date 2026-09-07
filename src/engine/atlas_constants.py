"""
Atlas-level scientific constants for the PETase Engineering Atlas.

All coordinates are expressed in canonical IsPETase Atlas numbering
(canonical 290-aa IsPETase Atlas reference, direct 1-indexed positions in that sequence).

This module is the single source of truth for policy-level constants that
do not require I/O.  Import from here; do not redefine locally.
"""

# ---------------------------------------------------------------------------
# Catalytic triad — IsPETase in Atlas coordinates
# S160 (nucleophile) · D206 (acid/general base) · H237 (histidine base)
#
# These positions MUST NEVER be recommended for mutation regardless of FVI
# score, scoring rule changes, or Atlas data updates.  The protection is an
# explicit invariant independent of the FVI filter so that it survives any
# future rescoring or data-pipeline changes.
#
# Reference: canonical 290-aa IsPETase Atlas reference (direct 1-indexed).
# ---------------------------------------------------------------------------
ATLAS_CATALYTIC_TRIAD: frozenset = frozenset({160, 206, 237})
