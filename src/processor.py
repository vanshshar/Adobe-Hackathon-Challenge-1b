
import re
from typing import Dict, List, Any
from collections import Counter
import math


class PersonaProcessor:
    
    def __init__(self):
        self.role_terms = {
            "researcher": ["research", "study", "analysis", "methodology", "data", "experiment", "hypothesis", "literature", "publication", "findings", "results", "conclusion"],
            "student": ["learn", "study", "understand", "concept", "theory", "practice", "example", "exercise", "exam", "assignment", "knowledge", "skill"],
            "analyst": ["analyze", "evaluate", "assess", "trend", "pattern", "metric", "performance", "comparison", "forecast", "strategy", "insight", "recommendation"],
            "teacher": ["teach", "explain", "instruction", "curriculum", "lesson", "education", "training", "guidance", "demonstration", "assessment", "learning", "development"],
            "manager": ["manage", "plan", "organize", "control", "strategy", "decision", "resource", "team", "process", "objective", "performance", "leadership"],
            "entrepreneur": ["business", "opportunity", "market", "innovation", "startup", "venture", "revenue", "growth", "investment", "competition", "strategy", "scalability"]
        }
        
        self.task_terms = {
            "review": ["review", "summary", "overview", "evaluation", "assessment", "analysis"],
            "learn": ["learn", "understand", "study", "master", "practice", "acquire"],
            "analyze": ["analyze", "examine", "investigate", "evaluate", "assess", "compare"],
            "prepare": ["prepare", "plan", "organize", "design", "develop", "create"],
            "summarize": ["summarize", "condense", "extract", "highlight", "synthesize", "distill"]
        }

    def _compute_task_alignment_score(self, text_content: str, task_description: str) -> float:
        normalized_content = text_content.lower()
        normalized_task = task_description.lower()
        
        task_keywords = set(re.findall(r'\b\w{4,}\b', normalized_task))
        content_keywords = set(re.findall(r'\b\w{4,}\b', normalized_content))
        
        if not task_keywords:
            return 0.0
        
        matched_terms = len(task_keywords.intersection(content_keywords))
        similarity_score = matched_terms / len(task_keywords)
        
        return min(similarity_score, 1.0)

    def _extract_role_specific_observations(self, text_content: str, role_category: str, task_category: str) -> List[str]:
        observations = []
        normalized_text = text_content.lower()
        
        if role_category == "researcher":
            if any(keyword in normalized_text for keyword in ["methodology", "method", "approach"]):
                observations.append("Research methodology identified")
            if any(keyword in normalized_text for keyword in ["data", "dataset", "sample"]):
                observations.append("Data sources and datasets mentioned")
            if any(keyword in normalized_text for keyword in ["result", "finding", "conclusion"]):
                observations.append("Research findings and results presented")
        
        elif role_category == "student":
            if any(keyword in normalized_text for keyword in ["concept", "principle", "theory"]):
                observations.append("Key concepts for learning identified")
            if any(keyword in normalized_text for keyword in ["example", "illustration", "case"]):
                observations.append("Examples and illustrations available")
            if any(keyword in normalized_text for keyword in ["exercise", "problem", "practice"]):
                observations.append("Practice materials and exercises found")
        
        elif role_category == "analyst":
            if any(keyword in normalized_text for keyword in ["trend", "pattern", "analysis"]):
                observations.append("Analytical insights and trends identified")
            if any(keyword in normalized_text for keyword in ["metric", "kpi", "performance"]):
                observations.append("Performance metrics and KPIs mentioned")
            if any(keyword in normalized_text for keyword in ["forecast", "prediction", "projection"]):
                observations.append("Forecasting and predictive information")
        
        if task_category == "review":
            if any(keyword in normalized_text for keyword in ["summary", "overview", "abstract"]):
                observations.append("Summary content suitable for review")
        elif task_category == "analyze":
            if any(keyword in normalized_text for keyword in ["comparison", "contrast", "versus"]):
                observations.append("Comparative analysis opportunities")
        
        return observations

    def _determine_importance_level(self, relevance_metric: float, observation_list: List[str], concept_list: List[str]) -> str:
        if relevance_metric >= 0.6 and len(observation_list) >= 2:
            return "high"
        elif relevance_metric >= 0.3 and (len(observation_list) >= 1 or len(concept_list) >= 3):
            return "medium"
        else:
            return "low"

    def _find_relevant_concepts(self, text_content: str, role_category: str) -> List[str]:
        relevant_concepts = []
        normalized_text = text_content.lower()
        
        if role_category in self.role_terms:
            role_keywords = self.role_terms[role_category]
            for keyword in role_keywords:
                if keyword in normalized_text:
                    relevant_concepts.append(keyword)
        
        return relevant_concepts[:5]

    def process_with_persona(self, doc_analysis: Dict[str, Any], user_persona: Dict[str, str], user_job: Dict[str, str]) -> Dict[str, Any]:
        role_description = user_persona.get("role", "")
        task_description = user_job.get("task", "")
        
        role_category = self._classify_user_role(role_description)
        task_category = self._classify_user_task(task_description)
        
        enhanced_sections = []
        
        for section in doc_analysis.get("sections", []):
            enhanced_section = self._augment_section_with_role_context(
                section, role_category, task_category, role_description, task_description
            )
            enhanced_sections.append(enhanced_section)
        
        role_analysis = self._build_role_analysis_summary(enhanced_sections, role_category, role_description)
        
        return {
            "persona_type": role_category,
            "job_type": task_category,
            "sections": enhanced_sections,
            "role_analysis": role_analysis
        }

    def _compute_relevance_score(self, text_content: str, role_category: str, task_category: str, task_description: str) -> float:
        role_score = 0.0
        task_score = 0.0
        
        if role_category in self.role_terms:
            role_keywords = self.role_terms[role_category]
            normalized_text = text_content.lower()
            
            keyword_matches = sum(1 for keyword in role_keywords if keyword in normalized_text)
            role_score = min(keyword_matches / len(role_keywords), 1.0)
        
        task_score = self._compute_task_alignment_score(text_content, task_description)
        
        weighted_score = (0.6 * role_score) + (0.4 * task_score)
        return min(weighted_score, 1.0)

    def _classify_user_task(self, task_description: str) -> str:
        normalized_task = task_description.lower()
        
        for task_type, keywords in self.task_terms.items():
            if any(keyword in normalized_task for keyword in keywords):
                return task_type
        
        return "general"

    def _build_role_analysis_summary(self, section_list: List[Dict[str, Any]], role_category: str, role_description: str) -> Dict[str, Any]:
        total_sections = len(section_list)
        high_importance = sum(1 for section in section_list if section.get("importance_level") == "high")
        medium_importance = sum(1 for section in section_list if section.get("importance_level") == "medium")
        
        avg_relevance = sum(section.get("relevance_score", 0) for section in section_list) / total_sections if total_sections > 0 else 0
        
        return {
            "role_category": role_category,
            "role_description": role_description,
            "total_sections_analyzed": total_sections,
            "high_importance_sections": high_importance,
            "medium_importance_sections": medium_importance,
            "average_relevance_score": round(avg_relevance, 3)
        }

    def _augment_section_with_role_context(self, section_data: Dict[str, Any], role_category: str, task_category: str, role_description: str, task_description: str) -> Dict[str, Any]:
        text_content = section_data.get("content", "")
        
        relevance_score = self._compute_relevance_score(text_content, role_category, task_category, task_description)
        observations = self._extract_role_specific_observations(text_content, role_category, task_category)
        relevant_concepts = self._find_relevant_concepts(text_content, role_category)
        importance_level = self._determine_importance_level(relevance_score, observations, relevant_concepts)
        
        enhanced_section = section_data.copy()
        enhanced_section.update({
            "relevance_score": relevance_score,
            "role_observations": observations,
            "relevant_concepts": relevant_concepts,
            "importance_level": importance_level,
            "role_category": role_category,
            "task_category": task_category
        })
        
        return enhanced_section

    def _classify_user_role(self, role_description: str) -> str:
        normalized_role = role_description.lower()
        
        for role_type, keywords in self.role_terms.items():
            if any(keyword in normalized_role for keyword in keywords):
                return role_type
        
        return "general"
