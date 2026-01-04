export const mockPremiumData = {
    "tier_0_classification": {
        "content_type": "conceptual_theory",
        "media_type": "text_only",
        "difficulty_score": 2,
        "complexity_flags": {
            "requires_derivation": false,
            "multi_concept_integration": false,
            "ambiguous_wording": false,
            "image_interpretation_complex": false,
            "edge_case_scenario": false,
            "multi_step_reasoning": false,
            "approximation_needed": false
        },
        "use_gpt51": false,
        "classification_confidence": 1.0,
        "classification_reasoning": "This question tests the fundamental definition of a real symmetric matrix. It's a direct recall question, making it a conceptual theory question with low difficulty.",
        "combined_type": "conceptual_theory_text_only",
        "weight_strategy": "CONCEPTUAL_WEIGHTED",
        "classification_method": "llm_assisted",
        "classifier_model": "gemini_2.0_flash_exp"
    },
    "tier_1_core_research": {
        "answer_validation": {
            "correct_answer": "D",
            "is_correct": true,
            "confidence": 0.98,
            "confidence_type": "single_model",
            "reasoning": "A real square matrix A is defined as symmetric if it is equal to its own transpose, meaning $A = A^T$. Therefore, for any real symmetric matrix $A$, its transpose is $A$ itself. This is a direct definition from linear algebra and requires understanding the basic definition and properties of symmetric matrices."
        },
        "explanation": {
            "question_nature": "Conceptual",
            "step_by_step": [
                "Recall the definition of a real symmetric matrix: A square matrix A is symmetric if and only if it is equal to its own transpose.",
                "Mathematically, this property is expressed as $A = A^T$, where $A^T$ denotes the transpose of A.",
                "The question asks for the transpose of a real symmetric matrix A. By applying the definition, if A is symmetric, then its transpose $A^T$ must be equal to A.",
                "Therefore, for any real symmetric matrix A, its transpose is A.",
                "Comparing this result with typical options, the correct answer would be A. Other options like the inverse of A, null matrix, or -A are generally incorrect for a symmetric matrix unless specific additional conditions are met.",
                "Conclude that the transpose of a real symmetric matrix A is A itself."
            ],
            "formulas_used": [
                "A = A^T"
            ],
            "estimated_time_minutes": 1.44
        },
        "hierarchical_tags": {
            "subject": {
                "name": "Linear Algebra",
                "confidence": 0.95
            },
            "topic": {
                "name": "Matrix Properties",
                "syllabus_ref": "Section 1: Linear Algebra"
            },
            "concepts": [
                {
                    "name": "Symmetric Matrix",
                    "importance": "primary",
                    "consensus": "ensemble"
                },
                {
                    "name": "Matrix Transpose",
                    "importance": "primary",
                    "consensus": "ensemble"
                },
                {
                    "name": "Matrix Properties",
                    "importance": "secondary",
                    "consensus": "ensemble"
                }
            ]
        },
        "prerequisites": {
            "essential": [
                "Definition of a Symmetric Matrix",
                "Properties of Matrix Transpose"
            ],
            "helpful": [
                "Eigenvalues and Eigenvectors of Symmetric Matrices"
            ],
            "dependency_tree": {
                "Symmetric Matrix": [
                    "requires: Definition of a Symmetric Matrix",
                    "requires: Properties of Matrix Transpose",
                    "enables: Orthogonal Diagonalization of Symmetric Matrices"
                ],
                "Main Concept: Transpose of a Symmetric Matrix": [
                    "requires: Definition of Matrix Transpose",
                    "requires: Definition of Symmetric Matrix",
                    "enables: Orthogonal Diagonalization (Spectral Theorem)",
                    "enables: Analysis of Stress/Strain Tensors (Symmetric in mechanics)"
                ],
                "Main Concept": [
                    "requires: Definition of a matrix",
                    "requires: Transpose of a Matrix",
                    "enables: Orthogonal Diagonalization",
                    "enables: Spectral Theorem"
                ]
            }
        },
        "difficulty_analysis": {
            "overall": "Easy",
            "score": 1.88,
            "complexity_breakdown": {
                "conceptual": 3,
                "mathematical": 2,
                "problem_solving": 1
            },
            "estimated_solve_time_seconds": 120,
            "expected_accuracy_percent": 85,
            "difficulty_factors": [
                "Direct recall of a fundamental definition and understanding the basic properties of symmetric matrices."
            ]
        },
        "textbook_references": [
            {
                "source_type": "book",
                "book": "Advanced Engineering Mathematics",
                "author": "Erwin Kreyszig",
                "chapter_number": "5",
                "chapter_title": "Linear Algebra: Matrices, Vectors, Determinants, Linear Systems",
                "section": "Symmetric Matrices",
                "page_range": "280-285",
                "complexity": "introductory",
                "relevance_score": 1.0,
                "source": "rag_retrieval",
                "text_snippet": "A real square matrix A is symmetric if $A = A^T$. This means that the elements $a_{ij}$ and $a_{ji}$ are equal for all i and j."
            },
            {
                "author": "B.S. Grewal",
                "book": "Higher Engineering Mathematics",
                "chapter_title": "Matrices",
                "complexity": "introductory",
                "relevance_score": 0.9,
                "section": "Transpose of a Matrix, Symmetric Matrices",
                "source": "model_consensus",
                "source_type": "book"
            }
        ],
        "video_references": [
            {
                "source_type": "video",
                "professor": "Prof. Sunita Gakkhar",
                "timestamp_start": "00:30:49",
                "timestamp_end": "00:14:51",
                "video_url": "https://www.youtube.com/watch?v=OG4qdRs9fp4",
                "book_reference": "Advanced Engineering Mathematics",
                "topic_covered": "Symmetric Matrices",
                "relevance_score": 1.0,
                "source": "rag_retrieval"
            }
        ],
        "step_by_step_solution": {
            "approach_type": "Direct Formula Application",
            "total_steps": 3,
            "solution_path": "Identify Symmetric Matrix Property -> Apply Definition -> Conclude Transpose Relationship",
            "key_insights": [
                "Symmetric matrices have the property that $A = A^T$",
                "This means the transpose of a symmetric matrix is simply the matrix itself"
            ]
        },
        "formulas_principles": [
            {
                "formula": "A = A^T",
                "name": "Definition of a Symmetric Matrix",
                "conditions": "For a real square matrix A",
                "type": "definition",
                "relevance": "Core definition for solving the problem"
            }
        ],
        "real_world_applications": {
            "industry_examples": [
                "Stiffness matrices in structural analysis (e.g., finite element method for aircraft structures)",
                "Inertia tensors in rigid body dynamics (e.g., spacecraft attitude control)",
                "Covariance matrices in statistics and data analysis (e.g., flight test data processing)"
            ],
            "specific_systems": [
                "Structural analysis of buildings and bridges often involves symmetric stiffness matrices",
                "Social network analysis uses symmetric adjacency matrices to represent bidirectional connections",
                "Aerodynamic stability derivatives (often form symmetric matrices)"
            ],
            "practical_relevance": "The properties of symmetric matrices, such as their orthogonal diagonalizability, having real eigenvalues and orthogonal eigenvectors, are fundamental to many areas of engineering and applied mathematics. Recognizing symmetry simplifies computations (e.g., eigenvalue problems, storage) and reflects physical reciprocity. Understanding these concepts is crucial for students to be able to analyze and solve problems in domains like stability analysis and modal decomposition in dynamic systems."
        }
    },
    "tier_2_student_learning": {
        "common_mistakes": [
            {
                "mistake": "Confusing symmetric matrices with orthogonal matrices.",
                "why_students_make_it": "Both symmetric and orthogonal matrices involve the transpose, leading students to mix up their distinct definitions ($A=A^T$ for symmetric vs. $A^T=A^{-1}$ for orthogonal).",
                "type": "Conceptual",
                "severity": "Medium",
                "frequency": "occasional",
                "how_to_avoid": "Clearly distinguish and memorize the exact definitions: Symmetric means $A = A^T$, while Orthogonal means $A^T = A^{-1}$. Use mnemonics or create a comparison table to reinforce understanding.",
                "consequence": "Leads to selecting the wrong answer, specifically option A (inverse of A) instead of D (A)."
            },
            {
                "mistake": "Confusing symmetric matrices with skew-symmetric matrices.",
                "why_students_make_it": "Both symmetric and skew-symmetric matrices relate to the transpose, but skew-symmetric matrices satisfy $A^T = -A$. Students might incorrectly recall or apply the negative sign.",
                "type": "Conceptual",
                "severity": "Medium",
                "frequency": "occasional",
                "how_to_avoid": "Focus on the positive equality for symmetric matrices ($A = A^T$). Associate symmetry with a 'mirror image' across the diagonal (no sign change), and remember that skew-symmetric matrices involve the negative sign ($A^T = -A$).",
                "consequence": "Leads to selecting the wrong answer, specifically option C ($-A$) instead of D (A)."
            },
            {
                "consequence": "Wastes time, leads to incorrect reasoning, or might result in incorrectly selecting option B.",
                "frequency": "occasional",
                "how_to_avoid": "Trust basic definitions. If a question asks for a definition that applies 'for any real symmetric matrix', the answer must hold universally, not just for special cases. Avoid overthinking and assuming hidden complexity.",
                "mistake": "Overthinking a simple definition, potentially overcomplicating and considering special cases like the null matrix (option B).",
                "severity": "Low",
                "type": "Conceptual",
                "why_students_make_it": "Students might assume GATE questions are always complex, leading them to search for deeper implications rather than direct definitions, or they might focus on trivial special cases like the zero matrix."
            }
        ],
        "mnemonics_memory_aids": [
            {
                "mnemonic": "SAME: Symmetric Matrices Are Equal to their Transpose",
                "concept": "Identifying and understanding the property of symmetric matrices",
                "effectiveness": "high",
                "context": "Whenever dealing with symmetric matrices, this mnemonic can help recall that the transpose is equal to the original matrix."
            },
            {
                "concept": "For an orthogonal matrix, the transpose equals the inverse.",
                "context": "To differentiate from symmetric matrices.",
                "effectiveness": "medium",
                "mnemonic": "Orthogonal = Transpose is Inverse (OTI)"
            }
        ],
        "flashcards": [
            {
                "card_type": "definition",
                "front": "What is a symmetric matrix?",
                "back": "A real square matrix A is symmetric if $A = A^T$, meaning the elements $a_{ij}$ and $a_{ji}$ are equal for all i and j.",
                "difficulty": "easy",
                "time_limit_seconds": 30
            },
            {
                "card_type": "concept_recall",
                "front": "Relationship between transpose of symmetric matrix and matrix itself?",
                "back": "For a real symmetric matrix A, the transpose of A is equal to A, i.e., $A^T = A$.",
                "difficulty": "easy",
                "time_limit_seconds": 20
            },
            {
                "card_type": "mistake_prevention",
                "front": "Common mistake about transpose of symmetric matrix?",
                "back": "Thinking the transpose is the negative (skew-symmetric) or inverse (orthogonal). It's actually the matrix itself.",
                "difficulty": "medium",
                "time_limit_seconds": 45
            }
        ],
        "real_world_context": [
            {
                "application": "Structural analysis",
                "industry_example": "In finite element analysis of structures like buildings and bridges, the stiffness matrix relating forces and displacements is often symmetric due to the reciprocal nature of the internal forces.",
                "why_it_matters": "Recognizing the symmetry of the stiffness matrix allows for more efficient computational methods and a better understanding of the underlying physics of the structural system."
            }
        ],
        "exam_strategy": {
            "priority": "Attempt If Time",
            "triage_tip": "Quickly check if the matrix is given as symmetric. If so, recall that the transpose is equal to the original matrix. Answer immediately.",
            "guessing_heuristic": "Recalling 'symmetric' implies 'mirrored', implying $A^T = A$. Eliminate inverse or negative options.",
            "time_management": "Allocate no more than 30 seconds."
        }
    },
    "tier_3_enhanced_learning": {
        "search_keywords": [
            "symmetric matrix properties",
            "transpose of symmetric matrix",
            "orthogonal diagonalization",
            "applications of symmetric matrices",
            "skew-symmetric matrix"
        ],
        "alternative_methods": [
            {
                "name": "Verifying Symmetry Using Matrix Elements",
                "description": "An alternative approach is to directly check that the matrix elements satisfy $a_{ij} = a_{ji}$ for all i and j.",
                "pros_cons": "More tedious than simply checking $A = A^T$, but useful if transpose isn't readily available.",
                "when_to_use": "Always for such direct recall questions."
            }
        ],
        "connections_to_other_subjects": {
            "Linear Algebra": "Fundamental to eigenvalues, eigenvectors, and diagonalization.",
            "Structural Mechanics": "Symmetric stiffness matrices arise in structural systems.",
            "Data Science": "Covariance matrices are symmetric, crucial for PCA."
        },
        "deeper_dive_topics": [
            "Spectral Decomposition of Symmetric Matrices",
            "Hermitian matrices (complex analogue)",
            "Positive definite symmetric matrices"
        ]
    },
    "tier_4_metadata_and_future": {
        "model_meta": {
            "models_used": [
                "gemini_2.5_pro",
                "claude_sonnet_4.5",
                "deepseek_r1"
            ],
            "model_count": 3,
            "weight_strategy": "CONCEPTUAL_WEIGHTED",
            "weights_applied": {
                "gemini_2.5_pro": 0.375,
                "claude_sonnet_4.5": 0.4375,
                "deepseek_r1": 0.1875
            },
            "consensus_method": "weighted_voting",
            "debate_rounds": 0,
            "converged_fields_count": 5,
            "debated_fields_count": 0,
            "flagged_for_review": [],
            "gpt51_added_in_debate": false,
            "timestamp": "2025-12-27T21:18:43.453745",
            "pipeline_version": "1.0.0"
        },
        "quality_score": {
            "overall": 0.831,
            "band": "SILVER",
            "metrics": {
                "avg_model_confidence": 0.75,
                "consensus_rate": 0.9,
                "debate_efficiency": 1.0,
                "rag_relevance": 0.489,
                "field_completeness": 1.0
            }
        },
        "cost_breakdown": {
            "total_cost": 0.10223442,
            "currency": "USD",
            "per_model": {
                "gemini_2.5_pro": 0.0036800999999999995,
                "claude_sonnet_4.5": 0.084093,
                "deepseek_r1": 0.01446132
            },
            "classification_cost": 5e-05,
            "image_consensus_cost": 0,
            "debate_cost": 0.0,
            "total_api_calls": 3
        },
        "token_usage": {
            "total_input_tokens": 31035,
            "total_output_tokens": 11127,
            "total_tokens": 42162,
            "per_model": {
                "gemini_2.5_pro": {
                    "input": 10242,
                    "output": 3573,
                    "total": 13815
                },
                "claude_sonnet_4.5": {
                    "input": 11076,
                    "output": 3391,
                    "total": 14467
                },
                "deepseek_r1": {
                    "input": 9717,
                    "output": 4163,
                    "total": 13880
                }
            }
        },
        "processing_time": {
            "total_seconds": 258.92990231513977,
            "per_stage": {
                "stage_1": 0.0015058517456054688,
                "stage_2": 1.8223743438720703,
                "stage_3": 2.5024681091308594,
                "stage_4": 7.45851993560791,
                "stage_5": 102.88826012611389,
                "stage_6": 144.25677394866943,
                "stage_8": 0.0021173954010009766
            },
            "bottleneck_stage": "stage_6",
            "parallel_generation_time": 102.88826012611389,
            "debate_time": 0
        }
    },
    "tier_4_metadata": {} // Map metadata_and_future to metadata for consistency with schema
};

// Fix the mapping for Tier 4
mockPremiumData.tier_4_metadata = mockPremiumData.tier_4_metadata_and_future;
delete mockPremiumData.tier_4_metadata_and_future;
