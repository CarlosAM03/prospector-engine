from dataclasses import dataclass, field

from prospector_engine.models.business import Business
from prospector_engine.models.normalized_business import NormalizedBusiness
from prospector_engine.models.search_query import SearchQuery
from prospector_engine.models.search_issue import SearchIssue
from prospector_engine.models.source_identity import SourceIdentityEvidence


@dataclass
class SearchResult:

    query: SearchQuery

    businesses: list[NormalizedBusiness] = field(
        default_factory=list
    )

    execution_time: float = 0.0

    issues: list[SearchIssue] = field(default_factory=list)

    original_businesses: list[Business] = field(default_factory=list)

    source_identities: tuple[SourceIdentityEvidence, ...] = field(default=(), kw_only=True)

    def __post_init__(self) -> None:
        if any(type(item) is not NormalizedBusiness for item in self.businesses):
            raise TypeError("businesses must contain NormalizedBusiness")
        if any(type(item) is not Business for item in self.original_businesses):
            raise TypeError("original_businesses must contain Business")
        if len(self.original_businesses) != len(self.businesses):
            raise ValueError("original and normalized counts must match")
        self.source_identities = tuple(self.source_identities)
        if not self.source_identities:
            self.source_identities = tuple(
                SourceIdentityEvidence.unverified() for _ in self.businesses
            )
        if len(self.source_identities) != len(self.businesses) or any(
            type(item) is not SourceIdentityEvidence for item in self.source_identities
        ):
            raise ValueError("public source identity evidence must align with businesses")

    @property
    def total_found(self) -> int:
        return len(self.businesses)
