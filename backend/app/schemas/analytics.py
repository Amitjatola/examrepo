from typing import List, Dict, Optional, Any
from pydantic import BaseModel

# --- Tier 0: Classification ---
class ComplexityFlags(BaseModel):
    requires_derivation: bool
    multi_concept_integration: bool
    ambiguous_wording: bool
    image_interpretation_complex: bool
    edge_case_scenario: bool
    multi_step_reasoning: bool
    approximation_needed: bool

class Tier0Classification(BaseModel):
    content_type: str
    media_type: str
    difficulty_score: float
    complexity_flags: ComplexityFlags
    use_gpt51: bool
    classification_confidence: float
    classification_reasoning: str
    combined_type: str
    weight_strategy: str
    classification_method: str
    classifier_model: str

# --- Tier 1: Core Research ---
class AnswerValidation(BaseModel):
    correct_answer: Optional[str] = None
    is_correct: Optional[bool] = None
    confidence: Optional[float] = None
    confidence_type: Optional[str] = None
    reasoning: Optional[str] = None

class Explanation(BaseModel):
    question_nature: Optional[str] = None
    step_by_step: Optional[List[Optional[Any]]] = []
    formulas_used: Optional[List[Optional[Any]]] = []
    estimated_time_minutes: Optional[float] = None

class Concept(BaseModel):
    name: Optional[str] = None
    importance: Optional[str] = None
    consensus: Optional[str] = None

class HierarchicalTags(BaseModel):
    subject: Optional[Dict[str, Any]] = None
    topic: Optional[Dict[str, str]] = None
    concepts: Optional[List[Concept]] = []

class Prerequisites(BaseModel):
    essential: Optional[List[Optional[str]]] = []
    helpful: Optional[List[Optional[str]]] = []
    dependency_tree: Optional[Any] = {}

class DifficultyAnalysis(BaseModel):
    overall: Optional[Any] = None
    score: Optional[Any] = None
    complexity_breakdown: Optional[Dict[str, float]] = {}
    estimated_solve_time_seconds: Optional[Any] = None
    expected_accuracy_percent: Optional[Any] = None
    difficulty_factors: Optional[List[Optional[Any]]] = []

class TextbookReference(BaseModel):
    source_type: Optional[Any] = None
    book: Optional[Any] = None
    author: Optional[Any] = None
    chapter_number: Optional[Any] = None
    chapter_title: Optional[Any] = None
    section: Optional[Any] = None
    page_range: Optional[Any] = None
    complexity: Optional[Any] = None
    relevance_score: Optional[Any] = None
    source: Optional[Any] = None
    text_snippet: Optional[Any] = None

class VideoReference(BaseModel):
    source_type: Optional[Any] = None
    professor: Optional[Any] = None
    timestamp_start: Optional[Any] = None
    timestamp_end: Optional[Any] = None
    video_url: Optional[Any] = None
    book_reference: Optional[Any] = None
    topic_covered: Optional[Any] = None
    relevance_score: Optional[Any] = None
    source: Optional[Any] = None

class StepByStepSolution(BaseModel):
    approach_type: Optional[Any] = None
    total_steps: Optional[Any] = None
    solution_path: Optional[Any] = None
    key_insights: Optional[List[Optional[Any]]] = []

class Formula(BaseModel):
    formula: Optional[Any] = None
    name: Optional[Any] = None
    conditions: Optional[Any] = None
    type: Optional[Any] = None
    relevance: Optional[Any] = None

class RealWorldApplications(BaseModel):
    industry_examples: Optional[List[Optional[str]]] = []
    specific_systems: Optional[List[Optional[str]]] = []
    practical_relevance: Optional[str] = None

class Tier1CoreResearch(BaseModel):
    answer_validation: Optional[AnswerValidation] = None
    explanation: Optional[Explanation] = None
    hierarchical_tags: Optional[HierarchicalTags] = None
    prerequisites: Optional[Prerequisites] = None
    difficulty_analysis: Optional[DifficultyAnalysis] = None
    textbook_references: Optional[List[TextbookReference]] = []
    video_references: Optional[List[VideoReference]] = []
    step_by_step_solution: Optional[StepByStepSolution] = None
    formulas_principles: Optional[List[Formula]] = []
    real_world_applications: Optional[RealWorldApplications] = None

# --- Tier 2: Student Learning ---
class CommonMistake(BaseModel):
    mistake: Optional[str] = None
    why_students_make_it: Optional[str] = None
    type: Optional[str] = None
    severity: Optional[str] = None
    frequency: Optional[str] = None
    how_to_avoid: Optional[str] = None
    consequence: Optional[str] = None

class Mnemonic(BaseModel):
    mnemonic: Optional[str] = None
    concept: Optional[str] = None
    effectiveness: Optional[str] = None
    context: Optional[str] = None

class Flashcard(BaseModel):
    card_type: Optional[str] = None
    front: Optional[str] = None
    back: Optional[str] = None
    difficulty: Optional[str] = None
    time_limit_seconds: Optional[int] = None

class RealWorldContext(BaseModel):
    application: Optional[str] = None
    industry_example: Optional[str] = None
    why_it_matters: Optional[str] = None

class ExamStrategy(BaseModel):
    priority: Optional[str] = None
    triage_tip: Optional[str] = None
    guessing_heuristic: Optional[str] = None
    time_management: Optional[str] = None

class Tier2StudentLearning(BaseModel):
    common_mistakes: Optional[List[CommonMistake]] = []
    mnemonics_memory_aids: Optional[List[Mnemonic]] = []
    flashcards: Optional[List[Flashcard]] = []
    real_world_context: Optional[List[RealWorldContext]] = []
    exam_strategy: Optional[ExamStrategy] = None

# --- Tier 3: Enhanced Learning ---
class AlternativeMethod(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    pros_cons: Optional[str] = None
    when_to_use: Optional[str] = None

class Tier3EnhancedLearning(BaseModel):
    search_keywords: Optional[List[Optional[str]]] = []
    alternative_methods: Optional[List[AlternativeMethod]] = []
    connections_to_other_subjects: Optional[Dict[str, Any]] = {}
    deeper_dive_topics: Optional[List[Optional[str]]] = []

# --- Tier 4: Metadata ---
class ModelMeta(BaseModel):
    models_used: List[str]
    model_count: int
    weight_strategy: str
    weights_applied: Dict[str, float]
    consensus_method: str
    debate_rounds: int
    converged_fields_count: int
    debated_fields_count: int
    flagged_for_review: Optional[List[Optional[str]]] = []
    gpt51_added_in_debate: bool
    timestamp: str
    pipeline_version: str

class QualityScore(BaseModel):
    overall: float
    band: str
    metrics: Dict[str, float]

class CostBreakdown(BaseModel):
    total_cost: float
    currency: str
    per_model: Dict[str, float]
    classification_cost: float
    image_consensus_cost: float
    debate_cost: float
    total_api_calls: int

class TokenUsage(BaseModel):
    total_input_tokens: int
    total_output_tokens: int
    total_tokens: int
    per_model: Dict[str, Dict[str, int]] # {input: int, output: int, total: int}

class ProcessingTime(BaseModel):
    total_seconds: float
    per_stage: Dict[str, float]
    bottleneck_stage: str
    parallel_generation_time: float
    debate_time: float

class RagQuality(BaseModel):
    relevance_score: float
    chunks_used: int
    sources_distribution: Dict[str, int]
    notes: str

class SyllabusMapping(BaseModel):
    gate_section: str
    gate_subsection: str
    syllabus_relevance_score: float
    weightage: str
    feedback_for_syllabus_design: str

class Tier4Metadata(BaseModel):
    model_meta: ModelMeta
    quality_score: QualityScore
    cost_breakdown: CostBreakdown
    token_usage: TokenUsage
    processing_time: ProcessingTime
    rag_quality: Optional[RagQuality] = None
    syllabus_mapping: Optional[SyllabusMapping] = None
    future_questions_potential: Optional[List[str]] = None

# --- Root Premium Data ---
class QuestionPremiumData(BaseModel):
    tier_0_classification: Tier0Classification
    tier_1_core_research: Tier1CoreResearch
    tier_2_student_learning: Tier2StudentLearning
    tier_3_enhanced_learning: Tier3EnhancedLearning
    tier_4_metadata_and_future: Tier4Metadata
