"""
Question repository for database operations.
Handles CRUD and search queries.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_, Text, text, cast, String
from sqlalchemy.dialects.postgresql import JSONB
from pgvector.sqlalchemy import Vector
from typing import Optional, List, Set
import uuid

from app.domains.questions.models import Question
from app.domains.questions.schemas import QuestionCreate, SearchFilters
from app.core.embedding import generate_embeddings


class QuestionRepository:
    """Repository for Question database operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, data: QuestionCreate) -> Question:
        """Create a new question with search preparation."""
        content, embedding = self._prepare_search_data(data.model_dump())
        question = Question(**data.model_dump(), search_content=content, embedding=embedding)
        self.session.add(question)
        await self.session.flush()
        await self.session.refresh(question)
        return question

    def _prepare_search_data(self, data: dict) -> tuple[str, List[float]]:
        """Combine fields into 'Content Soup' and generate vector embedding."""
        # 1. Build Content Soup (Text)
        parts = [
            str(data.get("question_text", "")),
            str(data.get("year", "")),      # Add Year to content
            str(data.get("source", ""))     # Add Source to content
        ]
        
        # Extract Tier 1 Concepts
        tier1 = data.get("tier_1_core_research", {})
        if tier1:
            tags = tier1.get("hierarchical_tags", {})
            parts.append(str(tags.get("topic", {}).get("name", "")))
            concepts = [str(c.get("name", "")) for c in tags.get("concepts", [])]
            parts.extend(concepts)
            
            # Extract Explanation summary
            expl = tier1.get("explanation", {})
            parts.append(str(expl.get("question_nature", "")))
            if expl.get("step_by_step"):
                parts.extend([str(s) for s in expl["step_by_step"] if s])

        # Extract Tier 3 Keywords
        tier3 = data.get("tier_3_enhanced_learning", {})
        if tier3:
            keywords = tier3.get("search_keywords", [])
            if keywords:
                parts.extend([str(k) for k in keywords])

        search_content = " | ".join([p for p in parts if p and p.strip()])
        
        # 2. Generate Embedding (BGE-Large)
        embedding_vec = generate_embeddings(search_content)
        embedding = embedding_vec.tolist()
        
        return search_content, embedding
    
    async def get_by_id(self, question_id: uuid.UUID) -> Optional[Question]:
        """Get question by UUID."""
        result = await self.session.execute(
            select(Question).where(Question.id == question_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_question_id(self, question_id: str) -> Optional[Question]:
        """Get question by string ID (e.g., GATE_AE_2008_Q01)."""
        result = await self.session.execute(
            select(Question).where(Question.question_id == question_id)
        )
        return result.scalar_one_or_none()
    
    async def search(
        self,
        query: str,
        filters: Optional[SearchFilters] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Question], int]:
        """
        Hybrid Search: Combined pgvector (Semantic) + pg_trgm (Typos).
        Logic: Score = (0.7 * cosine_similarity) + (0.3 * trigram_similarity).
        """
        if not query:
            # Fallback to basic list if no query, sorted by question number ascending
            stmt = select(Question).order_by(Question.year.desc(), Question.question_number.asc())
            count_stmt = select(func.count(Question.id))
        else:
            # Generate query embedding
            query_vector = generate_embeddings(query)
            
            # 1. Semantic Similarity (pgvector)
            # pgvector's <=> is cosine distance which is 1 - cosine_similarity.
            semantic_distance = Question.embedding.cosine_distance(query_vector)
            
            # 2. Text Similarity (pg_trgm)
            text_score = func.similarity(Question.search_content, query)
            
            # Hybrid Formula: Higher is better
            hybrid_score = (0.7 * (1 - semantic_distance)) + (0.3 * text_score)
            
            # Content Filter: For longer queries (likely from autocomplete selections),
            # require that the search_content actually contains the query term.
            # This ensures only relevant questions appear for specific concept searches.
            # UPDATE: Also check if the query matches the Year column (e.g. "2008")
            content_contains = or_(
                Question.search_content.ilike(f"%{query}%"),
                cast(Question.year, String).ilike(f"%{query}%")
            )
            
            stmt = (
                select(Question)
                .add_columns(hybrid_score.label("relevance"))
                .where(content_contains)
                .order_by(hybrid_score.desc())
            )
            count_stmt = select(func.count(Question.id)).where(content_contains)



        conditions = []
        if filters:
            if filters.year:
                conditions.append(Question.year == filters.year)
            if filters.years:
                conditions.append(Question.year.in_(filters.years))
            if filters.subject:
                conditions.append(func.lower(Question.subject).contains(filters.subject.lower()))
            if filters.question_type:
                conditions.append(Question.question_type == filters.question_type)
        
        # Apply all conditions
        if conditions:
            stmt = stmt.where(and_(*conditions))
            count_stmt = count_stmt.where(and_(*conditions))
        
        # Get total count
        total_result = await self.session.execute(count_stmt)
        total = total_result.scalar_one()
        
        # Apply pagination
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        
        result = await self.session.execute(stmt)
        # Handle cases where we have either Question or (Question, relevance)
        if query:
            questions = [row[0] for row in result.all()]
        else:
            questions = list(result.scalars().all())
        
        return questions, total
    
    async def get_suggestions(self, query: str, limit: int = 5) -> List[str]:
        """
        Get distinct concept/keyword suggestions based on fuzzy matching.
        Aggregates from Tier 1 (Topics/Concepts) and Tier 3 (Keywords).
        Zero Hallucination: Returns only values present in the DB.
        """
        if not query or len(query) < 2:
            return []
            
        sql = text("""
            WITH candidates AS (
                -- 1. Keywords (Tier 3) - check if search_keywords is an array
                SELECT jsonb_array_elements_text(tier_3_enhanced_learning::jsonb -> 'search_keywords') as term 
                FROM questions
                WHERE tier_3_enhanced_learning IS NOT NULL
                  AND jsonb_typeof(tier_3_enhanced_learning::jsonb -> 'search_keywords') = 'array'
                
                UNION
                
                -- 2. Concepts (Tier 1) - check if concepts is an array
                SELECT jsonb_array_elements(tier_1_core_research::jsonb -> 'hierarchical_tags' -> 'concepts') ->> 'name' as term 
                FROM questions
                WHERE tier_1_core_research IS NOT NULL
                  AND jsonb_typeof(tier_1_core_research::jsonb -> 'hierarchical_tags' -> 'concepts') = 'array'
                
                UNION
                
                -- 3. Topics (Tier 1)
                SELECT tier_1_core_research::jsonb -> 'hierarchical_tags' -> 'topic' ->> 'name' as term 
                FROM questions
                WHERE tier_1_core_research IS NOT NULL
            )
            SELECT term
            FROM candidates
            WHERE term IS NOT NULL 
              AND length(term) > 2
              AND word_similarity(:query, term) > 0.3 
            GROUP BY term
            ORDER BY max(word_similarity(:query, term)) DESC
            LIMIT :limit
        """)
        
        result = await self.session.execute(sql, {"query": query, "limit": limit})
        return result.scalars().all()
    
    async def get_filter_options(self) -> dict:
        """Get all available filter options for the UI."""
        # Get distinct years
        years_result = await self.session.execute(
            select(Question.year).distinct().order_by(Question.year.desc())
        )
        years = [row[0] for row in years_result.all()]
        
        # Get distinct subjects
        subjects_result = await self.session.execute(
            select(Question.subject).distinct()
        )
        subjects = [row[0] for row in subjects_result.all()]
        
        # Get distinct question types
        types_result = await self.session.execute(
            select(Question.question_type).distinct()
        )
        question_types = [row[0] for row in types_result.all()]
        
        return {
            "years": years,
            "subjects": subjects,
            "question_types": question_types,
            "topics": [],  # Will be extracted from tier_1 in future
            "concepts": [],  # Will be extracted from tier_1 in future
        }
    
    async def bulk_create(self, questions_data: list[dict]) -> int:
        """Bulk import questions with search enrichment."""
        count = 0
        for data in questions_data:
            existing = await self.get_by_question_id(data.get("question_id", ""))
            if not existing:
                content, embedding = self._prepare_search_data(data)
                question = Question(**data, search_content=content, embedding=embedding)
                self.session.add(question)
                count += 1
        
        await self.session.flush()
        return count
    
    async def count_all(self) -> int:
        """Get total question count."""
        result = await self.session.execute(select(func.count(Question.id)))
        return result.scalar_one()

    async def get_year_counts(self) -> dict[int, int]:
        """Get question counts grouped by year."""
        result = await self.session.execute(
            select(Question.year, func.count(Question.id))
            .group_by(Question.year)
            .order_by(Question.year.desc())
        )
        return {year: count for year, count in result.all()}

    async def get_syllabus_tree(self) -> dict:
        """
        Get the syllabus hierarchy (Subject -> Topics) from existing questions.
        Returns: {"Subject Name": ["Topic 1", "Topic 2"], ...}
        """
        sql = text("""
            SELECT DISTINCT
                tier_1_core_research->'hierarchical_tags'->'subject'->>'name' as subject,
                tier_1_core_research->'hierarchical_tags'->'topic'->>'name' as topic
            FROM questions
            WHERE tier_1_core_research->'hierarchical_tags'->'subject'->>'name' IS NOT NULL
            ORDER BY 1, 2
        """)
        
        result = await self.session.execute(sql)
        rows = result.fetchall()
        
        tree = {}
        for subject, topic in rows:
            if not subject:
                continue
            if subject not in tree:
                tree[subject] = []
            if topic and topic not in tree[subject]:
                tree[subject].append(topic)
                
        return tree
