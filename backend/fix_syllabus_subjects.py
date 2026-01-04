
import asyncio
from sqlalchemy import select
from app.core.database import get_session_context
from app.domains.questions.models import Question

async def fix_syllabus_subjects():
    async with get_session_context() as session:
        print("Starting Syllabus Subject Fix...")
        
        # Keywords for matching
        math_keywords = [
            "Calculus", "Linear Algebra", "Differential Equation", "Vector Calculus", 
            "Complex Variable", "Probability", "Statistic", "Numerical Method", 
            "Transform Theory", "Matrix", "Eigen", "Laplace", "Fourier", 
            "Limit", "Continuity", "Integration", "Differentiation"
        ]
        
        # Be careful with "Integration" (e.g. system integration vs math integration)
        # But in GATE context, usually Math if not "System Integration"
        
        aptitude_keywords = [
            "Verbal", "Reasoning", "Word", "Grammar", "Comprehension", 
            "Series Completion", "Aptitude", "English", "Vocabulary", 
            "Sentence", "Blood Relation", "Coding", "Decoding", "Data Interpretation",
            "Antonym", "Synonym", "Analogy"
        ]
        
        # Fetch ALL questions currently labeled "Aerospace Engineering"
        stmt = select(Question).where(Question.subject == "Aerospace Engineering")
        result = await session.execute(stmt)
        questions = result.scalars().all()
        
        math_count = 0
        apt_count = 0
        
        print(f"Processing {len(questions)} questions...")
        
        for q in questions:
            topic_name = ""
            if q.tier_1_core_research:
                tags = q.tier_1_core_research.get("hierarchical_tags", {})
                if tags.get("topic"):
                    topic_name = tags["topic"].get("name") or ""
            
            # Check for Math
            is_math = False
            for kw in math_keywords:
                if kw.lower() in topic_name.lower():
                    # Exclude false positives like "System Integration" if needed, 
                    # but looking at the list "Nozzle... Integration" was "Afterburner Integration".
                    if "integration" in kw.lower() and "afterburner" in topic_name.lower():
                        continue
                        
                    is_math = True
                    break
            
            if is_math:
                q.subject = "Engineering Mathematics"
                math_count += 1
                session.add(q)
                continue # Done with this question
            
            # Check for Aptitude (if not Math)
            is_apt = False
            for kw in aptitude_keywords:
                if kw.lower() in topic_name.lower():
                    is_apt = True
                    break
            
            if is_apt:
                q.subject = "General Aptitude"
                apt_count += 1
                session.add(q)
        
        await session.commit()
        print(f"Fix Complete.")
        print(f"Moved to Engineering Mathematics: {math_count}")
        print(f"Moved to General Aptitude: {apt_count}")

if __name__ == "__main__":
    asyncio.run(fix_syllabus_subjects())
