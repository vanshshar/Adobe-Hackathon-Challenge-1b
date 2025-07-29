
import math
from typing import Dict, List, Any
from collections import Counter


class SectionRanker:
    
    def __init__(self):
        pass
    
    def _compute_position_weight(self, doc_section: Dict[str, Any]) -> float:
        idx = doc_section.get("position", 0)
        if idx < 3:
            return 1.0
        elif idx < 10:
            return 0.8
        else:
            return 0.6

    def _extract_context_keywords(self, role_info: str, task_info: str) -> set:
        combined_text = f"{role_info} {task_info}".lower()
        keyword_set = set(word for word in combined_text.split() if len(word) > 2)
        return keyword_set

    def rank_sections(self, doc_sections: List[Dict[str, Any]], user_persona: Dict[str, str], job_details: Dict[str, str]) -> List[Dict[str, Any]]:
        if not doc_sections:
            return []
        
        context_data = self._build_persona_context(user_persona, job_details)
        
        ranked_sections = []
        for doc_section in doc_sections:
            relevance_value = self._compute_final_score(doc_section, context_data)
            updated_section = doc_section.copy()
            updated_section['relevance_score'] = relevance_value
            updated_section['final_relevance_score'] = relevance_value
            ranked_sections.append(updated_section)
        
        ranked_sections.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        return ranked_sections

    def _calculate_word_frequencies(self, text_content: str) -> Counter:
        word_list = text_content.lower().split()
        return Counter(word_list)

    def _build_persona_context(self, user_persona: Dict[str, str], job_details: Dict[str, str]) -> Dict[str, Any]:
        return {
            "persona_role": user_persona.get("role", ""),
            "job_context": job_details.get("task", "")
        }

    def _assess_content_length(self, text_content: str) -> float:
        word_count = len(text_content.split())
        
        if word_count < 10:
            return 0.3
        elif word_count < 50:
            return 0.8
        elif word_count < 200:
            return 1.0
        elif word_count < 500:
            return 0.7
        else:
            return 0.4

    def _compute_tfidf_relevance(self, text_content: str, context_data: Dict[str, Any]) -> float:
        role_keywords = self._extract_context_keywords(
            context_data.get("persona_role", ""),
            context_data.get("job_context", "")
        )
        
        if not role_keywords:
            return 0.5
        
        word_frequencies = self._calculate_word_frequencies(text_content)
        total_words = len(text_content.lower().split())
        
        relevance_sum = self._sum_keyword_scores(role_keywords, word_frequencies, total_words)
        
        return min(relevance_sum, 1.0)

    def _sum_keyword_scores(self, keywords: set, word_freq: Counter, total_count: int) -> float:
        total_score = 0.0
        for keyword in keywords:
            if keyword in word_freq:
                term_frequency = word_freq[keyword] / total_count
                inverse_doc_freq = math.log(1 + 1 / max(1, word_freq[keyword]))
                total_score += term_frequency * inverse_doc_freq
        
        return total_score

    def _compute_final_score(self, doc_section: Dict[str, Any], context_data: Dict[str, Any]) -> float:
        section_content = doc_section.get("content", "")
        if not section_content:
            return 0.0
        
        semantic_score = self._compute_tfidf_relevance(section_content, context_data)
        
        length_weight = self._assess_content_length(section_content)
        
        position_weight = self._compute_position_weight(doc_section)
        
        final_score = (0.6 * semantic_score + 0.3 * length_weight + 0.1 * position_weight)
        
        return min(final_score, 1.0)
