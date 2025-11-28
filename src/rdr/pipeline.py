from .ingestion import PhysicsDataPreparation
from .reasoning import PhysicsContentReasoning
from .projection import PhysicsContentProjection
from .analysis import PhysicsEmbeddingAnalysis

class PhysicsRDRPipeline:
    def __init__(self, llm_model, embedding_model):
        self.ingestion = PhysicsDataPreparation(llm_filter_model=llm_model)
        self.reasoning = PhysicsContentReasoning(llm_model=llm_model)
        self.projection = PhysicsContentProjection(embedding_model=embedding_model)
        self.analysis = PhysicsEmbeddingAnalysis(llm_model=llm_model)
        
        self.papers_db = [] # In-memory storage for demo
        self.embedding_model = embedding_model

    def run_full_cycle(self):
        """Run the complete RDR cycle: Ingest -> Reason -> Project -> Analyze"""
        print("Stage 1: Ingestion...")
        raw_papers = self.ingestion.collect_papers()
        filtered_papers = self.ingestion.filter_papers(raw_papers)
        print(f"  > Collected {len(filtered_papers)} physics papers.")
        
        print("Stage 2: Reasoning (Perspective Extraction)...")
        papers_with_perspectives = []
        for p in filtered_papers:
            p_aug = self.reasoning.extract_perspectives(p)
            # Merge perspectives into paper dict
            p.update(p_aug)
            papers_with_perspectives.append(p)
            
        print("Stage 3: Projection (Embedding & Clustering)...")
        embeddings = self.projection.project_to_embedding_space(papers_with_perspectives)
        clustering_result = self.projection.cluster_embeddings(embeddings, papers_with_perspectives)
        
        # Assign clusters to papers
        for i, p in enumerate(papers_with_perspectives):
            p['embedding'] = embeddings[i]
            p['cluster'] = clustering_result['cluster_labels'][i]
        
        self.papers_db = papers_with_perspectives
        
        print("Stage 4: Analysis...")
        survey = self.analysis.generate_domain_survey(clustering_result['cluster_keywords'])
        trends = self.analysis.analyze_trends_over_time(self.papers_db)
        graph = self.analysis.build_knowledge_graph(self.papers_db)
        
        return {
            "survey": survey,
            "trends": trends,
            "knowledge_graph": graph,
            "papers": self.papers_db
        }

    def semantic_search(self, query: str, top_k: int = 5):
        """Search the indexed papers"""
        return self.analysis.semantic_retrieval(query, self.papers_db, self.embedding_model, top_k)
