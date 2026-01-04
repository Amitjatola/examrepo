
import asyncio
from sqlalchemy import select
from app.core.database import get_session_context
from app.domains.questions.models import Question

async def verify_math_topics():
    async with get_session_context() as session:
        print("Searching for Math topics in 'Aerospace Engineering'...")
        
        math_keywords = [
            "Calculus", "Linear Algebra", "Differential Equations", "Vector Calculus", 
            "Complex Variables", "Probability", "Statistics", "Numerical Methods", 
            "Transform Theory", "Matrix", "Eigen", "Integration", "Differentiation",
            "Laplace", "Fourier", "Series", "Limits", "Continuity"
        ]
        
        stmt = select(Question).where(Question.subject == "Aerospace Engineering")
        result = await session.execute(stmt)
        questions = result.scalars().all()
        
        count = 0
        topics_found = set()
        
        for q in questions:
            is_math = False
            topic_name = "Unknown"
            if q.tier_1_core_research:
                tags = q.tier_1_core_research.get("hierarchical_tags", {})
                if tags.get("topic"):
                    topic_name = tags["topic"].get("name")
                    if topic_name:
                        for keyword in math_keywords:
                            if keyword.lower() in topic_name.lower():
                                is_math = True
                                break
            
            if is_math:
                count += 1
                topics_found.add(topic_name)
                # Print sample
                if count <= 5:
                    print(f"Match found: {q.question_id} | Topic: {topic_name}")
        
        print(f"\nTotal potential Math questions found: {count}")
        print("Topics identified:")
        for t in sorted(list(topics_found)):
            print(f"- {t}")

if __name__ == "__main__":
    asyncio.run(verify_math_topics())
