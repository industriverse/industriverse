"""
Neo4j client wrapper.
"""

from __future__ import annotations

from typing import Any, Dict

from neo4j import GraphDatabase


class Neo4jWrapper:
    def __init__(self, uri: str, user: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self) -> None:
        self.driver.close()

    def upsert_node(self, label: str, node_id: str, props: Dict[str, Any]) -> None:
        with self.driver.session() as session:
            session.execute_write(
                lambda tx: tx.run(
                    f"MERGE (n:{label} {{id:$id}}) SET n += $props",
                    id=node_id,
                    props=props,
                )
            )
