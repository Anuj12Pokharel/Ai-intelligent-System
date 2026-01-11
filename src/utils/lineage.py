import uuid
from dataclasses import dataclass, field
from typing import List, Dict, Any
import time

# Simple in-memory lineage tracking for each query

@dataclass
class QueryLineage:
    lineage_id: str
    query: str
    answer: str = ""
    sources: List[Dict] = field(default_factory=list)
    start_time: float = field(default_factory=time.time)
    latency_ms: float = 0.0
    tokens_used: int = 0

class LineageTracker:
    def __init__(self):
        # lineage_id -> QueryLineage
        self.traces: Dict[str, QueryLineage] = {}

    def start_trace(self, query: str) -> QueryLineage:
        lineage_id = str(uuid.uuid4())
        trace = QueryLineage(lineage_id=lineage_id, query=query)
        self.traces[lineage_id] = trace
        return trace

    def add_sources(self, trace: QueryLineage, sources: List[Dict]):
        trace.sources.extend(sources)

    def complete_trace(self, trace: QueryLineage, answer: str, latency_ms: float, tokens: int):
        trace.answer = answer
        trace.latency_ms = latency_ms
        trace.tokens_used = tokens

    def get_citation_path(self, trace: QueryLineage) -> List[str]:
        # Return a simple list of citation strings for each source
        citations = []
        for src in trace.sources:
            act = src.get('act_title', 'Unknown')
            section = src.get('section_number', '??')
            clause = src.get('clause_number', '')
            if clause:
                citations.append(f"{act}, दफा {section}, खण्ड {clause}")
            else:
                citations.append(f"{act}, दफा {section}")
        return citations

    def get_stats(self) -> Dict[str, Any]:
        return {
            "total_traces": len(self.traces),
            "average_latency_ms": (sum(t.latency_ms for t in self.traces.values()) / len(self.traces)) if self.traces else 0,
            "average_tokens": (sum(t.tokens_used for t in self.traces.values()) / len(self.traces)) if self.traces else 0,
        }
