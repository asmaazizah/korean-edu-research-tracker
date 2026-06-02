"""Data source adapters."""

from research_tracker.adapters.kci import KCIAdapter
from research_tracker.adapters.riss import RISSPlaceholderAdapter
from research_tracker.adapters.scopus import ScopusAdapter
from research_tracker.adapters.wos import WebOfScienceAdapter

__all__ = ["KCIAdapter", "RISSPlaceholderAdapter", "ScopusAdapter", "WebOfScienceAdapter"]
