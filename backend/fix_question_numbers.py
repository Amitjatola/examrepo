
import asyncio
from sqlalchemy import select, update
from app.core.database import get_session_context
from app.domains.questions.models import Question

async def fix_question_numbers():
    async with get_session_context() as session:
        print("Starting Question Renumbering Fix...")
        
        # Strategy:
        # GATE Papers typically have:
        # - General Aptitude (GA): 10 Questions (Q1-Q10 or Q56-Q65)
        # - Core Subject (AE): 55 Questions (Q1-Q55 or Q11-Q65)
        
        # Our data has collisions at 1-10.
        # Let's Standardize:
        # GA -> 1 to 10
        # AE/Math -> 11 to 65
        
        # Step 1: Identify Valid GA Questions (ID contains '_GA_')
        print("Renumbering GA questions to 1-10 range (if not already match IDs)...")
        # Usually GA IDs are GA_Q01 to GA_Q10. Their number should be 1-10.
        
        # Step 2: Identify Core Questions (ID contains '_AE_')
        # If AE questions conflict at 1-10, we shift them to 11-65 range?
        # NO, usually AE Q1 is Q1 of the core section.
        # But if we want global sorting 1..65, we need a single sequence.
        # Let's check if AE IDs are Q1..Q55 or Q11..Q65.
        # From previous steps: "GATE_2019_AE_Q11" exists.
        # But "GATE_2018_AE_Q01" also exists.
        
        # If a paper has AE Q01..Q55 and GA Q01..Q10, we have overlapping numbers.
        # To fix "all questions in ascending order", we must offset one group.
        # Convention: GA is usually the FIRST section (1-10) or LAST (56-65).
        # Let's put GA at 56-65 to be safe (or 1-10 if we shift AE).
        # Shifting AE is risky if question text refers to "Q12".
        # Let's shift GA to 56-65.
        
        # Find GA questions
        stmt = select(Question).where(Question.question_id.ilike("%_GA_%"))
        result = await session.execute(stmt)
        ga_questions = result.scalars().all()
        
        count = 0
        for q in ga_questions:
            # check current number
            original_num = q.question_number
            # If it's 1-10, map to 56-65
            if 1 <= original_num <= 10:
                new_num = original_num + 55
                q.question_number = new_num
                session.add(q)
                count += 1
        
        await session.commit()
        print(f"Renumbered {count} GA questions to 56-65 range.")

if __name__ == "__main__":
    asyncio.run(fix_question_numbers())
