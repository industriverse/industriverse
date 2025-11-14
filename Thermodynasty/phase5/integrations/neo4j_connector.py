"""
Neo4j Connector for Energy Atlas

Production-grade Neo4j integration for energy network topology,
flow patterns, and graph-based analytics.
"""

import logging
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
from enum import Enum

try:
    from neo4j import GraphDatabase, Driver, Session, Transaction
    from neo4j.exceptions import Neo4jError, ServiceUnavailable
except ImportError:
    GraphDatabase = None
    Driver = None
    Session = None
    Transaction = None
    Neo4jError = Exception
    ServiceUnavailable = Exception

import numpy as np
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class Neo4jConfig(BaseModel):
    """Neo4j configuration"""
    uri: str = Field(default="bolt://localhost:7687", description="Neo4j URI")
    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password")
    database: str = Field(default="neo4j", description="Database name")
    max_connection_lifetime: int = Field(default=3600, description="Max connection lifetime (s)")
    max_connection_pool_size: int = Field(default=50, description="Connection pool size")
    connection_timeout: int = Field(default=30, description="Connection timeout (s)")
    encrypted: bool = Field(default=False, description="Use encryption")


class NodeType(str, Enum):
    """Energy network node types"""
    DOMAIN = "Domain"
    CLUSTER = "Cluster"
    NODE = "Node"
    REGIME = "Regime"
    ENERGY_STATE = "EnergyState"


class RelationType(str, Enum):
    """Energy network relationship types"""
    CONTAINS = "CONTAINS"
    FLOWS_TO = "FLOWS_TO"
    IN_REGIME = "IN_REGIME"
    TRANSITIONS_TO = "TRANSITIONS_TO"
    INFLUENCES = "INFLUENCES"


class Neo4jConnector:
    """
    Production Neo4j connector for Energy Atlas.

    Features:
    - Connection pooling and retry logic
    - ACID transactions
    - Cypher query builder
    - Graph traversal algorithms
    - Energy flow analysis
    - Topology management
    - Batch operations for performance
    """

    def __init__(self, config: Neo4jConfig):
        """
        Initialize Neo4j connector.

        Args:
            config: Neo4j configuration
        """
        if GraphDatabase is None:
            raise ImportError(
                "neo4j driver required for Neo4j integration. "
                "Install with: pip install neo4j"
            )

        self.config = config

        # Create driver
        self.driver = GraphDatabase.driver(
            config.uri,
            auth=(config.username, config.password),
            max_connection_lifetime=config.max_connection_lifetime,
            max_connection_pool_size=config.max_connection_pool_size,
            connection_timeout=config.connection_timeout,
            encrypted=config.encrypted
        )

        # Verify connectivity
        self.verify_connectivity()

        # Create indexes and constraints
        self._ensure_schema()

        logger.info(
            f"Neo4jConnector initialized: uri={config.uri}, "
            f"database={config.database}"
        )

    def close(self):
        """Close driver"""
        self.driver.close()
        logger.info("Neo4j connection closed")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def verify_connectivity(self) -> bool:
        """
        Verify connection to Neo4j.

        Returns:
            True if connected
        """
        try:
            with self.driver.session(database=self.config.database) as session:
                result = session.run("RETURN 1 AS num")
                record = result.single()
                if record and record["num"] == 1:
                    logger.info("Neo4j connectivity verified")
                    return True
                return False

        except (Neo4jError, ServiceUnavailable) as e:
            logger.error(f"Connectivity check failed: {e}")
            return False

    def _ensure_schema(self):
        """Create indexes and constraints"""
        constraints = [
            # Unique constraints
            f"CREATE CONSTRAINT IF NOT EXISTS FOR (d:{NodeType.DOMAIN.value}) REQUIRE d.domain_id IS UNIQUE",
            f"CREATE CONSTRAINT IF NOT EXISTS FOR (c:{NodeType.CLUSTER.value}) REQUIRE c.cluster_id IS UNIQUE",
            f"CREATE CONSTRAINT IF NOT EXISTS FOR (n:{NodeType.NODE.value}) REQUIRE n.node_id IS UNIQUE",
            f"CREATE CONSTRAINT IF NOT EXISTS FOR (r:{NodeType.REGIME.value}) REQUIRE r.regime_name IS UNIQUE"
        ]

        indexes = [
            # Performance indexes
            f"CREATE INDEX IF NOT EXISTS FOR (d:{NodeType.DOMAIN.value}) ON (d.name)",
            f"CREATE INDEX IF NOT EXISTS FOR (n:{NodeType.NODE.value}) ON (n.created_at)",
            f"CREATE INDEX IF NOT EXISTS FOR (e:{NodeType.ENERGY_STATE.value}) ON (e.timestamp)"
        ]

        with self.driver.session(database=self.config.database) as session:
            for constraint in constraints:
                try:
                    session.run(constraint)
                except Neo4jError as e:
                    logger.warning(f"Constraint creation failed (may already exist): {e}")

            for index in indexes:
                try:
                    session.run(index)
                except Neo4jError as e:
                    logger.warning(f"Index creation failed (may already exist): {e}")

        logger.info("Schema ensured: constraints and indexes created")

    # ========================================================================
    # Execute Queries
    # ========================================================================

    def execute_query(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute Cypher query.

        Args:
            query: Cypher query string
            parameters: Query parameters

        Returns:
            Query results
        """
        with self.driver.session(database=self.config.database) as session:
            try:
                result = session.run(query, parameters or {})
                return [dict(record) for record in result]

            except Neo4jError as e:
                logger.error(f"Query execution failed: {e}")
                raise

    def execute_write_transaction(
        self,
        transaction_function,
        *args,
        **kwargs
    ) -> Any:
        """
        Execute write transaction.

        Args:
            transaction_function: Function to execute in transaction
            args: Positional arguments
            kwargs: Keyword arguments

        Returns:
            Transaction result
        """
        with self.driver.session(database=self.config.database) as session:
            try:
                return session.write_transaction(transaction_function, *args, **kwargs)
            except Neo4jError as e:
                logger.error(f"Write transaction failed: {e}")
                raise

    def execute_read_transaction(
        self,
        transaction_function,
        *args,
        **kwargs
    ) -> Any:
        """
        Execute read transaction.

        Args:
            transaction_function: Function to execute in transaction
            args: Positional arguments
            kwargs: Keyword arguments

        Returns:
            Transaction result
        """
        with self.driver.session(database=self.config.database) as session:
            try:
                return session.read_transaction(transaction_function, *args, **kwargs)
            except Neo4jError as e:
                logger.error(f"Read transaction failed: {e}")
                raise

    # ========================================================================
    # Node Operations
    # ========================================================================

    def create_domain(
        self,
        domain_id: str,
        name: str,
        properties: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create energy domain node.

        Args:
            domain_id: Unique domain identifier
            name: Domain name
            properties: Additional properties

        Returns:
            Created node
        """
        query = f"""
        CREATE (d:{NodeType.DOMAIN.value} {{
            domain_id: $domain_id,
            name: $name,
            created_at: datetime(),
            properties: $properties
        }})
        RETURN d
        """

        params = {
            'domain_id': domain_id,
            'name': name,
            'properties': properties or {}
        }

        result = self.execute_query(query, params)
        logger.info(f"Created domain: {domain_id}")
        return result[0]['d'] if result else {}

    def create_cluster(
        self,
        cluster_id: str,
        domain_id: str,
        properties: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create cluster node and link to domain.

        Args:
            cluster_id: Unique cluster identifier
            domain_id: Parent domain
            properties: Additional properties

        Returns:
            Created node
        """
        query = f"""
        MATCH (d:{NodeType.DOMAIN.value} {{domain_id: $domain_id}})
        CREATE (c:{NodeType.CLUSTER.value} {{
            cluster_id: $cluster_id,
            domain_id: $domain_id,
            created_at: datetime(),
            properties: $properties
        }})
        CREATE (d)-[:{RelationType.CONTAINS.value}]->(c)
        RETURN c
        """

        params = {
            'cluster_id': cluster_id,
            'domain_id': domain_id,
            'properties': properties or {}
        }

        result = self.execute_query(query, params)
        logger.info(f"Created cluster: {cluster_id} in domain {domain_id}")
        return result[0]['c'] if result else {}

    def create_node(
        self,
        node_id: str,
        cluster_id: str,
        properties: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create node and link to cluster.

        Args:
            node_id: Unique node identifier
            cluster_id: Parent cluster
            properties: Additional properties

        Returns:
            Created node
        """
        query = f"""
        MATCH (c:{NodeType.CLUSTER.value} {{cluster_id: $cluster_id}})
        CREATE (n:{NodeType.NODE.value} {{
            node_id: $node_id,
            cluster_id: $cluster_id,
            created_at: datetime(),
            properties: $properties
        }})
        CREATE (c)-[:{RelationType.CONTAINS.value}]->(n)
        RETURN n
        """

        params = {
            'node_id': node_id,
            'cluster_id': cluster_id,
            'properties': properties or {}
        }

        result = self.execute_query(query, params)
        logger.info(f"Created node: {node_id} in cluster {cluster_id}")
        return result[0]['n'] if result else {}

    def create_energy_state(
        self,
        node_id: str,
        energy: float,
        entropy: float,
        regime: str,
        timestamp: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create energy state snapshot for node.

        Args:
            node_id: Node identifier
            energy: Total energy
            entropy: Entropy
            regime: Current regime
            timestamp: State timestamp
            metadata: Additional metadata

        Returns:
            Created state node
        """
        query = f"""
        MATCH (n:{NodeType.NODE.value} {{node_id: $node_id}})
        CREATE (e:{NodeType.ENERGY_STATE.value} {{
            node_id: $node_id,
            energy: $energy,
            entropy: $entropy,
            regime: $regime,
            timestamp: $timestamp,
            metadata: $metadata
        }})
        CREATE (n)-[:HAS_STATE {{timestamp: $timestamp}}]->(e)
        RETURN e
        """

        params = {
            'node_id': node_id,
            'energy': energy,
            'entropy': entropy,
            'regime': regime,
            'timestamp': timestamp or datetime.utcnow(),
            'metadata': metadata or {}
        }

        result = self.execute_query(query, params)
        logger.debug(f"Created energy state for node: {node_id}")
        return result[0]['e'] if result else {}

    # ========================================================================
    # Relationship Operations
    # ========================================================================

    def create_energy_flow(
        self,
        from_node_id: str,
        to_node_id: str,
        flow_rate: float,
        timestamp: Optional[datetime] = None
    ):
        """
        Create energy flow relationship between nodes.

        Args:
            from_node_id: Source node
            to_node_id: Destination node
            flow_rate: Energy flow rate
            timestamp: Flow timestamp
        """
        query = f"""
        MATCH (n1:{NodeType.NODE.value} {{node_id: $from_node_id}})
        MATCH (n2:{NodeType.NODE.value} {{node_id: $to_node_id}})
        CREATE (n1)-[:{RelationType.FLOWS_TO.value} {{
            flow_rate: $flow_rate,
            timestamp: $timestamp,
            created_at: datetime()
        }}]->(n2)
        """

        params = {
            'from_node_id': from_node_id,
            'to_node_id': to_node_id,
            'flow_rate': flow_rate,
            'timestamp': timestamp or datetime.utcnow()
        }

        self.execute_query(query, params)
        logger.debug(f"Created energy flow: {from_node_id} -> {to_node_id}")

    def create_regime_transition(
        self,
        node_id: str,
        from_regime: str,
        to_regime: str,
        confidence: float,
        timestamp: Optional[datetime] = None
    ):
        """
        Record regime transition.

        Args:
            node_id: Node identifier
            from_regime: Source regime
            to_regime: Destination regime
            confidence: Transition confidence
            timestamp: Transition timestamp
        """
        query = f"""
        MATCH (n:{NodeType.NODE.value} {{node_id: $node_id}})
        MERGE (r1:{NodeType.REGIME.value} {{regime_name: $from_regime}})
        MERGE (r2:{NodeType.REGIME.value} {{regime_name: $to_regime}})
        CREATE (n)-[:WAS_IN {{timestamp: $timestamp}}]->(r1)
        CREATE (n)-[:NOW_IN {{timestamp: $timestamp, confidence: $confidence}}]->(r2)
        CREATE (r1)-[:{RelationType.TRANSITIONS_TO.value} {{
            via_node: $node_id,
            confidence: $confidence,
            timestamp: $timestamp
        }}]->(r2)
        """

        params = {
            'node_id': node_id,
            'from_regime': from_regime,
            'to_regime': to_regime,
            'confidence': confidence,
            'timestamp': timestamp or datetime.utcnow()
        }

        self.execute_query(query, params)
        logger.info(f"Recorded regime transition: {from_regime} -> {to_regime} for {node_id}")

    # ========================================================================
    # Query Operations
    # ========================================================================

    def get_domain_topology(self, domain_id: str) -> Dict[str, Any]:
        """
        Get complete topology for domain.

        Args:
            domain_id: Domain identifier

        Returns:
            Topology structure
        """
        query = f"""
        MATCH (d:{NodeType.DOMAIN.value} {{domain_id: $domain_id}})
        OPTIONAL MATCH (d)-[:{RelationType.CONTAINS.value}]->(c:{NodeType.CLUSTER.value})
        OPTIONAL MATCH (c)-[:{RelationType.CONTAINS.value}]->(n:{NodeType.NODE.value})
        RETURN d, collect(DISTINCT c) as clusters, collect(DISTINCT n) as nodes
        """

        result = self.execute_query(query, {'domain_id': domain_id})
        return result[0] if result else {}

    def get_energy_flow_paths(
        self,
        from_node_id: str,
        to_node_id: str,
        max_hops: int = 5
    ) -> List[List[str]]:
        """
        Find energy flow paths between nodes.

        Args:
            from_node_id: Source node
            to_node_id: Destination node
            max_hops: Maximum path length

        Returns:
            List of paths (each path is list of node IDs)
        """
        query = f"""
        MATCH path = (n1:{NodeType.NODE.value} {{node_id: $from_node_id}})
                     -[:{RelationType.FLOWS_TO.value}*1..{max_hops}]->
                     (n2:{NodeType.NODE.value} {{node_id: $to_node_id}})
        RETURN [node IN nodes(path) | node.node_id] AS path
        LIMIT 10
        """

        params = {
            'from_node_id': from_node_id,
            'to_node_id': to_node_id
        }

        result = self.execute_query(query, params)
        return [record['path'] for record in result]

    def get_regime_distribution(self, domain_id: Optional[str] = None) -> Dict[str, int]:
        """
        Get regime distribution across nodes.

        Args:
            domain_id: Filter by domain

        Returns:
            Regime counts
        """
        if domain_id:
            query = f"""
            MATCH (d:{NodeType.DOMAIN.value} {{domain_id: $domain_id}})
                  -[:{RelationType.CONTAINS.value}*]->
                  (n:{NodeType.NODE.value})
            MATCH (n)-[:NOW_IN]->(r:{NodeType.REGIME.value})
            RETURN r.regime_name AS regime, count(n) AS count
            """
            params = {'domain_id': domain_id}
        else:
            query = f"""
            MATCH (n:{NodeType.NODE.value})-[:NOW_IN]->(r:{NodeType.REGIME.value})
            RETURN r.regime_name AS regime, count(n) AS count
            """
            params = {}

        result = self.execute_query(query, params)
        return {record['regime']: record['count'] for record in result}

    def get_node_energy_history(
        self,
        node_id: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get energy state history for node.

        Args:
            node_id: Node identifier
            limit: Maximum states to return

        Returns:
            Energy state history
        """
        query = f"""
        MATCH (n:{NodeType.NODE.value} {{node_id: $node_id}})
              -[:HAS_STATE]->(e:{NodeType.ENERGY_STATE.value})
        RETURN e
        ORDER BY e.timestamp DESC
        LIMIT $limit
        """

        params = {
            'node_id': node_id,
            'limit': limit
        }

        result = self.execute_query(query, params)
        return [record['e'] for record in result]

    # ========================================================================
    # Graph Analytics
    # ========================================================================

    def compute_centrality(
        self,
        algorithm: str = "pagerank"
    ) -> List[Dict[str, Any]]:
        """
        Compute node centrality using graph algorithms.

        Args:
            algorithm: Algorithm to use (pagerank, betweenness, degree)

        Returns:
            Centrality scores
        """
        if algorithm == "pagerank":
            # Requires Graph Data Science library
            logger.warning("PageRank requires Neo4j GDS plugin")
            return []
        elif algorithm == "degree":
            query = f"""
            MATCH (n:{NodeType.NODE.value})
            RETURN n.node_id AS node_id,
                   size((n)-[:{RelationType.FLOWS_TO.value}]->()) AS out_degree,
                   size((n)<-[:{RelationType.FLOWS_TO.value}]-()) AS in_degree
            ORDER BY out_degree + in_degree DESC
            LIMIT 100
            """
            return self.execute_query(query)
        else:
            logger.error(f"Unknown centrality algorithm: {algorithm}")
            return []

    def find_energy_bottlenecks(self) -> List[Dict[str, Any]]:
        """
        Find nodes with high energy flow (bottlenecks).

        Returns:
            Bottleneck nodes
        """
        query = f"""
        MATCH (n:{NodeType.NODE.value})-[f:{RelationType.FLOWS_TO.value}]->()
        WITH n, sum(f.flow_rate) AS total_outflow
        WHERE total_outflow > 1000  // Threshold
        RETURN n.node_id AS node_id, total_outflow
        ORDER BY total_outflow DESC
        LIMIT 20
        """

        return self.execute_query(query)

    # ========================================================================
    # Batch Operations
    # ========================================================================

    def batch_create_nodes(
        self,
        nodes: List[Dict[str, Any]],
        node_type: NodeType
    ):
        """
        Batch create nodes for performance.

        Args:
            nodes: List of node dictionaries
            node_type: Type of nodes to create
        """
        query = f"""
        UNWIND $nodes AS node_data
        CREATE (n:{node_type.value})
        SET n = node_data
        SET n.created_at = datetime()
        """

        self.execute_query(query, {'nodes': nodes})
        logger.info(f"Batch created {len(nodes)} {node_type.value} nodes")

    def batch_create_relationships(
        self,
        relationships: List[Tuple[str, str, float]],
        rel_type: RelationType
    ):
        """
        Batch create relationships.

        Args:
            relationships: List of (from_id, to_id, flow_rate) tuples
            rel_type: Relationship type
        """
        query = f"""
        UNWIND $rels AS rel
        MATCH (n1:{NodeType.NODE.value} {{node_id: rel.from_id}})
        MATCH (n2:{NodeType.NODE.value} {{node_id: rel.to_id}})
        CREATE (n1)-[:{rel_type.value} {{
            flow_rate: rel.flow_rate,
            created_at: datetime()
        }}]->(n2)
        """

        rel_data = [
            {'from_id': from_id, 'to_id': to_id, 'flow_rate': flow_rate}
            for from_id, to_id, flow_rate in relationships
        ]

        self.execute_query(query, {'rels': rel_data})
        logger.info(f"Batch created {len(relationships)} {rel_type.value} relationships")


# ============================================================================
# Global Neo4j Connector
# ============================================================================

_neo4j_connector: Optional[Neo4jConnector] = None


def get_neo4j_connector(config: Optional[Neo4jConfig] = None) -> Neo4jConnector:
    """Get global Neo4j connector instance"""
    global _neo4j_connector
    if _neo4j_connector is None:
        if config is None:
            raise ValueError("Neo4jConfig required for first initialization")
        _neo4j_connector = Neo4jConnector(config)
    return _neo4j_connector


# ============================================================================
# Convenience Functions
# ============================================================================

def create_energy_network(
    domain_id: str,
    clusters: List[str],
    nodes_per_cluster: int,
    config: Optional[Neo4jConfig] = None
):
    """Create complete energy network topology"""
    connector = get_neo4j_connector(config)

    # Create domain
    connector.create_domain(domain_id, f"Domain-{domain_id}")

    # Create clusters and nodes
    for cluster_id in clusters:
        connector.create_cluster(cluster_id, domain_id)

        for i in range(nodes_per_cluster):
            node_id = f"{cluster_id}_node_{i}"
            connector.create_node(node_id, cluster_id)

    logger.info(f"Created energy network: {len(clusters)} clusters, {len(clusters) * nodes_per_cluster} nodes")
