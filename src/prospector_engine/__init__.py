"""Public Python API for the independent extraction engine."""

from .engines.config import EngineConfig
from .cancellation import CancellationRequested, CancellationToken, cancellation_scope
from .observability import EngineObserver, ExecutionEvent, observe_execution
from .engines.errors import (
    BatchInterruptedError,
    ProspectorConfigurationError,
    ProspectorError,
    ProspectorExtractionError,
    ProspectorNavigationError,
    ProspectorRuntimeError,
    ProspectorSourceError,
)
from .engines.prospector_engine import ProspectorEngine
from .models.batch import (
    BatchQuery,
    BatchQueryResult,
    BatchSearchResult,
    DuplicateReference,
    ObservationDisposition,
    ObservationProvenance,
    ObservationRef,
    QueryFailure,
    QueryStatus,
)
from .models.business import Business
from .models.normalized_business import NormalizedBusiness
from .models.search_issue import SearchIssue
from .models.search_query import SearchQuery, Source
from .models.search_result import SearchResult
from .models.source_identity import (
    SourceIdentityEvidence,
    VerificationState,
    VerifiedSourceIdentity,
)

__version__ = "0.1.0.dev0"
__all__ = [
    "ProspectorEngine",
    "EngineConfig",
    "SearchQuery",
    "Source",
    "SearchResult",
    "Business",
    "NormalizedBusiness",
    "SearchIssue",
    "BatchQuery",
    "BatchQueryResult",
    "BatchSearchResult",
    "QueryStatus",
    "QueryFailure",
    "ObservationRef",
    "ObservationProvenance",
    "ObservationDisposition",
    "DuplicateReference",
    "SourceIdentityEvidence",
    "VerifiedSourceIdentity",
    "VerificationState",
    "ProspectorError",
    "ProspectorConfigurationError",
    "ProspectorExtractionError",
    "ProspectorNavigationError",
    "ProspectorRuntimeError",
    "ProspectorSourceError",
    "BatchInterruptedError",
    "CancellationRequested",
    "CancellationToken",
    "cancellation_scope",
    "EngineObserver",
    "ExecutionEvent",
    "observe_execution",
]
