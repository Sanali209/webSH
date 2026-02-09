import logging
import polars as pl
from typing import List, Dict, Any, Optional
from core.database_manager import db_manager

logger = logging.getLogger(__name__)

class HybridSearcher:
    """
    Orchestrates search across Core Metadata (Text) and Plugin Tables (Vector).
    """
    def __init__(self, database_manager=db_manager):
        self.db = database_manager

    def search_text(self, query: str, limit: int = 50) -> pl.DataFrame:
        """
        Performs a text search on the Core Metadata Table.
        """
        try:
            core_table = self.db.get_core_table()
            try:
                results = core_table.search(query).limit(limit).to_polars()
                return results.with_columns(
                    pl.arange(0, pl.len()).alias("rank_text")
                )
            except Exception:
                logger.debug("FTS search failed, falling back to simple filter.")
                df = core_table.to_polars()
                filtered = df.filter(
                    pl.col("filename").str.contains(query, literal=True)
                )
                return filtered.head(limit).with_columns(
                    pl.arange(0, pl.len()).alias("rank_text")
                )

        except Exception as e:
            logger.error(f"Text search failed: {e}")
            return pl.DataFrame()

    def search_vectors(self, query_vector: List[float], plugin_ids: List[str], limit: int = 50) -> pl.DataFrame:
        """
        Searches vector tables of specified plugins.
        """
        dfs = []
        for plugin_id in plugin_ids:
            try:
                table_name = f"plugin_{plugin_id}_vectors"
                if table_name in self.db.list_tables():
                    table = self.db.get_table(table_name)
                    res = table.search(query_vector).limit(limit).to_polars()
                    if not res.is_empty():
                        dfs.append(res)
            except Exception as e:
                logger.warning(f"Vector search failed for plugin {plugin_id}: {e}")

        if not dfs:
            return pl.DataFrame()

        combined = pl.concat(dfs)
        return combined.with_columns(
            pl.arange(0, pl.len()).alias("rank_vector")
        )

    def reciprocal_rank_fusion(self, text_results: pl.DataFrame, vector_results: pl.DataFrame, k: int = 60) -> pl.DataFrame:
        """
        Merges text and vector results using RRF.
        """
        if text_results.is_empty() and vector_results.is_empty():
            return pl.DataFrame()

        if text_results.is_empty():
            return vector_results.with_columns(
                (1.0 / (k + pl.col("rank_vector"))).alias("rrf_score")
            ).sort("rrf_score", descending=True)

        if vector_results.is_empty():
            return text_results.with_columns(
                (1.0 / (k + pl.col("rank_text"))).alias("rrf_score")
            ).sort("rrf_score", descending=True)

        # Explicitly use how='full' and ensure coalescing
        joined = text_results.join(
            vector_results.select(["entity_id", "rank_vector"]),
            on="entity_id",
            how="full",
            coalesce=True
        )

        joined = joined.with_columns([
            pl.col("rank_text").fill_null(10000),
            pl.col("rank_vector").fill_null(10000)
        ])

        joined = joined.with_columns(
            (
                (1.0 / (k + pl.col("rank_text"))) +
                (1.0 / (k + pl.col("rank_vector")))
            ).alias("rrf_score")
        )

        return joined.sort("rrf_score", descending=True)

    def search(self, query: str, query_vector: Optional[List[float]] = None, plugin_ids: List[str] = None) -> List[Dict[str, Any]]:
        """
        Main entry point for search.
        """
        text_df = self.search_text(query)

        vector_df = pl.DataFrame()
        if query_vector and plugin_ids:
            vector_df = self.search_vectors(query_vector, plugin_ids)

        final_df = self.reciprocal_rank_fusion(text_df, vector_df)

        return final_df.to_dicts()

# Global instance
search_orchestrator = HybridSearcher()
