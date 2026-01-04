export interface ComplexityFlags {
    requires_derivation: boolean;
    multi_concept_integration: boolean;
    ambiguous_wording: boolean;
    image_interpretation_complex: boolean;
    edge_case_scenario: boolean;
    multi_step_reasoning: boolean;
    approximation_needed: boolean;
}

export interface Tier0Classification {
    content_type: string;
    media_type: string;
    difficulty_score: number;
    complexity_flags: ComplexityFlags;
    use_gpt51: boolean;
    classification_confidence: number;
    classification_reasoning: string;
    combined_type: string;
    weight_strategy: string;
    classification_method: string;
    classifier_model: string;
}

export interface AnswerValidation {
    correct_answer: string;
    is_correct: boolean;
    confidence: number;
    confidence_type: string;
    reasoning: string;
}

export interface Explanation {
    question_nature: string;
    step_by_step: string[];
    formulas_used: string[];
    estimated_time_minutes: number;
}

export interface HierarchicalTags {
    subject: { name: string; confidence: number };
    topic: { name: string; syllabus_ref: string };
    concepts: Array<{ name: string; importance: string; consensus: string }>;
}

export interface Prerequisites {
    essential: string[];
    helpful: string[];
    dependency_tree: Record<string, string[]>;
}

export interface DifficultyAnalysis {
    overall: string;
    score: number;
    complexity_breakdown: Record<string, number>;
    estimated_solve_time_seconds: number;
    expected_accuracy_percent: number;
    difficulty_factors: string[];
}

export interface TextbookReference {
    source_type: string;
    book: string;
    author: string;
    chapter_number?: string;
    chapter_title: string;
    section: string;
    page_range?: string;
    complexity: string;
    relevance_score: number;
    source: string;
    text_snippet?: string;
}

export interface VideoReference {
    source_type: string;
    professor: string;
    timestamp_start: string;
    timestamp_end: string;
    video_url: string;
    book_reference: string;
    topic_covered: string;
    relevance_score: number;
    source: string;
}

export interface StepByStepSolution {
    approach_type: string;
    total_steps: number;
    solution_path: string;
    key_insights: string[];
}

export interface Formula {
    formula: string;
    name: string;
    conditions: string;
    type: string;
    relevance: string;
}

export interface RealWorldApplications {
    industry_examples: string[];
    specific_systems: string[];
    practical_relevance: string;
}

export interface Tier1CoreResearch {
    answer_validation: AnswerValidation;
    explanation: Explanation;
    hierarchical_tags: HierarchicalTags;
    prerequisites: Prerequisites;
    difficulty_analysis: DifficultyAnalysis;
    textbook_references: TextbookReference[];
    video_references: VideoReference[];
    step_by_step_solution: StepByStepSolution;
    formulas_principles: Formula[];
    real_world_applications: RealWorldApplications;
}

export interface CommonMistake {
    mistake: string;
    why_students_make_it: string;
    type: string;
    severity: string;
    frequency: string;
    how_to_avoid: string;
    consequence: string;
}

export interface Mnemonic {
    mnemonic: string;
    concept: string;
    effectiveness: string;
    context: string;
}

export interface Flashcard {
    card_type: string;
    front: string;
    back: string;
    difficulty: string;
    time_limit_seconds: number;
}

export interface RealWorldContext {
    application: string;
    industry_example: string;
    why_it_matters: string;
}

export interface ExamStrategy {
    priority: string;
    triage_tip: string;
    guessing_heuristic: string;
    time_management: string;
}

export interface Tier2StudentLearning {
    common_mistakes: CommonMistake[];
    mnemonics_memory_aids: Mnemonic[];
    flashcards: Flashcard[];
    real_world_context: RealWorldContext[];
    exam_strategy: ExamStrategy;
}

export interface AlternativeMethod {
    name: string;
    description: string;
    pros_cons: string;
    when_to_use: string;
}

export interface Tier3EnhancedLearning {
    search_keywords: string[];
    alternative_methods: AlternativeMethod[];
    connections_to_other_subjects: Record<string, string>;
    deeper_dive_topics: string[];
}

export interface ModelMeta {
    models_used: string[];
    model_count: number;
    weight_strategy: string;
    weights_applied: Record<string, number>;
    consensus_method: string;
    debate_rounds: number;
    converged_fields_count: number;
    debated_fields_count: number;
    flagged_for_review: string[];
    gpt51_added_in_debate: boolean;
    timestamp: string;
    pipeline_version: string;
}

export interface QualityScore {
    overall: number;
    band: string;
    metrics: Record<string, number>;
}

export interface CostBreakdown {
    total_cost: number;
    currency: string;
    per_model: Record<string, number>;
    classification_cost: number;
    image_consensus_cost: number;
    debate_cost: number;
    total_api_calls: number;
}

export interface TokenUsage {
    total_input_tokens: number;
    total_output_tokens: number;
    total_tokens: number;
    per_model: Record<string, { input: number; output: number; total: number }>;
}

export interface ProcessingTime {
    total_seconds: number;
    per_stage: Record<string, number>;
    bottleneck_stage: string;
    parallel_generation_time: number;
    debate_time: number;
}

export interface RagQuality {
    relevance_score: number;
    chunks_used: number;
    sources_distribution: Record<string, number>;
    notes: string;
}

export interface SyllabusMapping {
    gate_section: string;
    gate_subsection: string;
    syllabus_relevance_score: number;
    weightage: string;
    feedback_for_syllabus_design: string;
}

export interface Tier4Metadata {
    model_meta: ModelMeta;
    quality_score: QualityScore;
    cost_breakdown: CostBreakdown;
    token_usage: TokenUsage;
    processing_time: ProcessingTime;
    rag_quality?: RagQuality;
    syllabus_mapping?: SyllabusMapping;
    future_questions_potential?: string[];
}
