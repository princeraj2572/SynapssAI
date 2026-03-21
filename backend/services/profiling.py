"""
Query profiling and monitoring utilities.
Tracks slow queries and provides performance insights.

Usage:
    # Enable query profiling
    enable_query_logging(db)
    
    # Run queries...
    
    # View report
    report = get_performance_report()
    print(report)
"""
import logging
import time
from typing import Dict, List
from datetime import datetime, timedelta
from sqlalchemy import event
from sqlalchemy.interfaces import DBAPIConnection
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class QueryStats:
    """Statistics for a single query or query pattern."""
    
    def __init__(self, query: str):
        self.query = query[:100]  # First 100 chars
        self.count = 0
        self.total_time = 0.0
        self.min_time = float('inf')
        self.max_time = 0.0
        self.slow_count = 0  # Queries > 100ms
    
    def add(self, elapsed: float):
        """Record a query execution."""
        self.count += 1
        self.total_time += elapsed
        self.min_time = min(self.min_time, elapsed)
        self.max_time = max(self.max_time, elapsed)
        if elapsed > 0.1:
            self.slow_count += 1
    
    def avg_time(self) -> float:
        """Get average execution time."""
        return self.total_time / self.count if self.count > 0 else 0
    
    def to_dict(self) -> dict:
        """Convert to dictionary for reporting."""
        return {
            "query": self.query,
            "count": self.count,
            "total_ms": round(self.total_time * 1000, 2),
            "avg_ms": round(self.avg_time() * 1000, 2),
            "min_ms": round(self.min_time * 1000, 2),
            "max_ms": round(self.max_time * 1000, 2),
            "slow_queries": self.slow_count,
        }
    
    def __repr__(self):
        return f"QueryStats({self.count} queries, avg {self.avg_time()*1000:.1f}ms)"


class QueryProfiler:
    """Collects and tracks query performance."""
    
    def __init__(self, slow_query_threshold: float = 0.1):
        self.slow_query_threshold = slow_query_threshold
        self.queries: Dict[str, QueryStats] = {}
        self.total_queries = 0
        self.total_time = 0.0
        self.start_time = datetime.now()
    
    def record_query(self, query_string: str, elapsed: float):
        """Record a query execution."""
        # Normalize query (remove values)
        normalized = self._normalize_query(query_string)
        
        if normalized not in self.queries:
            self.queries[normalized] = QueryStats(query_string)
        
        self.queries[normalized].add(elapsed)
        self.total_queries += 1
        self.total_time += elapsed
        
        # Log slow queries
        if elapsed > self.slow_query_threshold:
            logger.warning(f"SLOW QUERY ({elapsed:.3f}s): {query_string[:100]}")
    
    @staticmethod
    def _normalize_query(query: str) -> str:
        """Normalize query to group similar queries."""
        # Simple normalization: remove WHERE values
        normalized = query
        
        # Replace common parameter patterns
        import re
        normalized = re.sub(r'WHERE \d+', 'WHERE $1', normalized)
        normalized = re.sub(r"'[^']*'", "'$VALUE'", normalized)
        normalized = re.sub(r'\$\d+', '$N', normalized)
        
        return normalized[:150]  # Keep first 150 chars
    
    def get_slowest_queries(self, limit: int = 10) -> List[Dict]:
        """Get slowest queries."""
        sorted_queries = sorted(
            self.queries.values(),
            key=lambda x: x.avg_time(),
            reverse=True
        )
        return [q.to_dict() for q in sorted_queries[:limit]]
    
    def get_most_frequent_queries(self, limit: int = 10) -> List[Dict]:
        """Get most frequently executed queries."""
        sorted_queries = sorted(
            self.queries.values(),
            key=lambda x: x.count,
            reverse=True
        )
        return [q.to_dict() for q in sorted_queries[:limit]]
    
    def get_summary(self) -> dict:
        """Get profiling summary."""
        elapsed_sec = (datetime.now() - self.start_time).total_seconds()
        return {
            "total_queries": self.total_queries,
            "unique_queries": len(self.queries),
            "total_time_sec": round(self.total_time, 2),
            "avg_query_ms": round(self.total_time / self.total_queries * 1000, 2) if self.total_queries > 0 else 0,
            "elapsed_sec": round(elapsed_sec, 2),
            "uptime": f"{int(elapsed_sec // 60)}m {int(elapsed_sec % 60)}s",
        }
    
    def get_report(self) -> str:
        """Generate performance report."""
        summary = self.get_summary()
        slowest = self.get_slowest_queries(5)
        frequent = self.get_most_frequent_queries(5)
        
        report = "=== QUERY PERFORMANCE REPORT ===\n"
        report += f"Period: {self.start_time} to {datetime.now()}\n"
        report += f"Total Queries: {summary['total_queries']}\n"
        report += f"Unique Queries: {summary['unique_queries']}\n"
        report += f"Total Time: {summary['total_time_sec']}s\n"
        report += f"Avg Query Time: {summary['avg_query_ms']}ms\n\n"
        
        report += "=== TOP 5 SLOWEST QUERIES ===\n"
        for i, q in enumerate(slowest, 1):
            report += f"\n{i}. {q['query'][:80]}\n"
            report += f"   Count: {q['count']}, Avg: {q['avg_ms']}ms, "
            report += f"Max: {q['max_ms']}ms, Slow: {q['slow_queries']}\n"
        
        report += "\n=== TOP 5 MOST FREQUENT QUERIES ===\n"
        for i, q in enumerate(frequent, 1):
            report += f"\n{i}. {q['query'][:80]}\n"
            report += f"   Count: {q['count']}, Avg: {q['avg_ms']}ms, "
            report += f"Total: {q['total_ms']}ms\n"
        
        return report
    
    def reset(self):
        """Reset profiler."""
        self.queries.clear()
        self.total_queries = 0
        self.total_time = 0.0
        self.start_time = datetime.now()


# Global profiler instance
_query_profiler = QueryProfiler()


def get_profiler() -> QueryProfiler:
    """Get the global query profiler."""
    return _query_profiler


def enable_query_logging(db: Session, slow_threshold: float = 0.1):
    """
    Enable query profiling on database session.
    
    Args:
        db: SQLAlchemy session
        slow_threshold: Threshold in seconds for logging slow queries
    """
    global _query_profiler
    _query_profiler = QueryProfiler(slow_threshold)
    
    @event.listens_for(db, "after_cursor_execute")
    def receive_after_cursor_execute(conn: DBAPIConnection, cursor, statement, parameters, context, executemany):
        elapsed = context.execution_options.get('_query_start_time', time.time())
        elapsed = time.time() - elapsed
        _query_profiler.record_query(statement, elapsed)


def get_performance_report() -> str:
    """Get current performance report."""
    return _query_profiler.get_report()


def reset_profiler():
    """Reset profiler statistics."""
    global _query_profiler
    _query_profiler.reset()


# Decorator for function-level profiling
def profile_execution(name: str = ""):
    """
    Decorator to profile function execution time.
    
    Usage:
        @profile_execution("expensive_computation")
        def my_func():
            return expensive_operation()
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            func_name = name or func.__name__
            start = time.time()
            result = func(*args, **kwargs)
            elapsed = time.time() - start
            
            if elapsed > 0.1:
                logger.warning(f"SLOW: {func_name} took {elapsed:.3f}s")
            else:
                logger.debug(f"PROFILE: {func_name} took {elapsed:.3f}s")
            
            return result
        return wrapper
    return decorator


class ExecutionTimer:
    """Context manager for timing code sections."""
    
    def __init__(self, name: str, threshold: float = 0.1):
        self.name = name
        self.threshold = threshold
        self.start_time = None
        self.elapsed = 0
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.elapsed = time.time() - self.start_time
        if self.elapsed > self.threshold:
            logger.warning(f"SLOW: {self.name} took {self.elapsed:.3f}s")
        else:
            logger.debug(f"PROFILE: {self.name} took {self.elapsed:.3f}s")
    
    def __repr__(self):
        return f"ExecutionTimer({self.name}, {self.elapsed:.3f}s)"


# Usage: with ExecutionTimer("section_name"): ...
