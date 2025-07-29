#!/usr/bin/env python3

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
import time

sys.path.append('src')

from analyzer import DocumentAnalyzer
from processor import PersonaProcessor
from ranker import SectionRanker


class Challenge1BProcessor:
    
    def __init__(self):
        self.analyzer = DocumentAnalyzer()
        self.processor = PersonaProcessor()
        self.ranker = SectionRanker()
        self.max_sections = 15
        
    def load_config(self, config_path: str) -> Dict[str, Any]:
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config {config_path}: {e}")
            return {}
    
    def process_document(self, pdf_path: str, document_info: Dict[str, str]) -> Dict[str, Any]:
        try:
            analysis_result = self.analyzer.analyze_document(pdf_path)
            
            if not analysis_result.get('sections'):
                print(f"Warning: No sections found in {pdf_path}")
                return {}
            
            persona_info = {"role": document_info.get("persona_role", "General")}
            job_info = {"task": document_info.get("job_task", "General analysis")}
            
            persona_result = self.processor.process_with_persona(
                analysis_result, persona_info, job_info
            )
            
            ranked_sections = self.ranker.rank_sections(
                persona_result.get('sections', []), persona_info, job_info
            )
            
            return {
                'document_path': pdf_path,
                'document_info': document_info,
                'analysis_result': analysis_result,
                'persona_result': persona_result,
                'ranked_sections': ranked_sections
            }
            
        except Exception as e:
            print(f"Error processing document {pdf_path}: {e}")
            return {}
    
    def process_collection(self, collection_dir: str) -> bool:
        try:
            config_path = os.path.join(collection_dir, "challenge1b_input.json")
            config = self.load_config(config_path)
            
            if not config:
                print(f"Failed to load config for {collection_dir}")
                return False
            
            persona_role = config.get('persona', {}).get('role', 'General')
            job_task = config.get('job_to_be_done', {}).get('task', 'General analysis')
            
            all_sections = []
            processed_docs = []
            
            for doc_info in config.get('documents', []):
                pdf_filename = doc_info.get('filename')
                if not pdf_filename:
                    continue
                
                pdf_path = os.path.join(collection_dir, "PDFs", pdf_filename)
                if not os.path.exists(pdf_path):
                    print(f"PDF not found: {pdf_path}")
                    continue
                
                doc_result = self.process_document(pdf_path, {
                    'persona_role': persona_role,
                    'job_task': job_task,
                    'title': doc_info.get('title', ''),
                    'filename': pdf_filename
                })
                
                if doc_result:
                    processed_docs.append(pdf_filename)
                    for section in doc_result.get('ranked_sections', []):
                        section['document_filename'] = pdf_filename
                        all_sections.append(section)
            
            all_sections.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
            
            top_sections = all_sections[:self.max_sections]
            
            output_data = self._generate_output(config, processed_docs, top_sections)
            
            output_path = os.path.join(collection_dir, "challenge1b_output.json")
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2)
            
            print(f"Successfully processed {collection_dir}: {len(processed_docs)} documents, {len(top_sections)} sections")
            return True
            
        except Exception as e:
            print(f"Error processing collection {collection_dir}: {e}")
            return False
    
    def _generate_output(self, config: Dict[str, Any], processed_docs: List[str], 
                        top_sections: List[Dict[str, Any]]) -> Dict[str, Any]:
        
        challenge_info = config.get('challenge_info', {})
        persona_info = config.get('persona', {})
        job_info = config.get('job_to_be_done', {})
        
        metadata = {
            "processing_timestamp": int(datetime.now().timestamp()),
            "persona_type": self._classify_persona(persona_info.get('role', '')),
            "job_context": job_info.get('task', ''),
            "total_documents_processed": len(processed_docs),
            "total_sections_analyzed": len(top_sections),
            "top_sections_selected": len(top_sections),
            "input_documents": processed_docs
        }
        
        extracted_sections = []
        for i, section in enumerate(top_sections):
            extracted_sections.append({
                "document_filename": section.get('document_filename', ''),
                "section_title": section.get('section_title', ''),
                "content": section.get('content', '')[:1000],
                "page_number": section.get('page_number', 1),
                "relevance_score": round(section.get('relevance_score', 0), 4)
            })
        
        subsection_analysis = []
        for section in top_sections[:5]:
            subsection_analysis.append({
                "document_filename": section.get('document_filename', ''),
                "refined_text": section.get('content', '')[:300],
                "page_number": section.get('page_number', 1)
            })
        
        persona_insights = {
            "identified_persona": self._classify_persona(persona_info.get('role', '')),
            "alignment_quality": self._assess_alignment_quality(top_sections),
            "persona_context": persona_info.get('role', ''),
            "task_context": job_info.get('task', '')
        }
        
        high_relevance = len([s for s in top_sections if s.get('relevance_score', 0) >= 0.7])
        medium_relevance = len([s for s in top_sections if 0.4 <= s.get('relevance_score', 0) < 0.7])
        low_relevance = len([s for s in top_sections if s.get('relevance_score', 0) < 0.4])
        
        content_distribution = {
            "high_relevance_sections": high_relevance,
            "medium_relevance_sections": medium_relevance,
            "low_relevance_sections": low_relevance
        }
        
        top_sections_summary = []
        for section in top_sections[:5]:
            top_sections_summary.append({
                "document": section.get('document_filename', ''),
                "title": section.get('section_title', ''),
                "score": round(section.get('relevance_score', 0), 4)
            })
        
        return {
            "challenge_info": challenge_info,
            "metadata": metadata,
            "extracted_sections": extracted_sections,
            "subsection_analysis": subsection_analysis,
            "subsection_analysis": {
                "persona_insights": persona_insights,
                "content_distribution": content_distribution,
                "top_sections_summary": top_sections_summary
            }
        }
    
    def _classify_persona(self, role: str) -> str:
        role_lower = role.lower()
        if any(keyword in role_lower for keyword in ['travel', 'trip', 'vacation', 'tourism']):
            return 'travel_planner'
        elif any(keyword in role_lower for keyword in ['hr', 'human resource', 'employee', 'onboarding']):
            return 'hr_professional'
        elif any(keyword in role_lower for keyword in ['food', 'catering', 'chef', 'restaurant']):
            return 'food_contractor'
        else:
            return 'general'
    
    def _assess_alignment_quality(self, sections: List[Dict[str, Any]]) -> str:
        if not sections:
            return 'low'
        
        avg_score = sum(s.get('relevance_score', 0) for s in sections) / len(sections)
        
        if avg_score >= 0.7:
            return 'high'
        elif avg_score >= 0.4:
            return 'medium'
        else:
            return 'low'


def main():
    processor = Challenge1BProcessor()
    
    collections = ["Collection 1", "Collection 2", "Collection 3"]
    
    for collection in collections:
        if os.path.exists(collection):
            print(f"\nProcessing {collection}...")
            success = processor.process_collection(collection)
            if success:
                print(f"✓ {collection} processed successfully")
            else:
                print(f"✗ {collection} processing failed")
        else:
            print(f"Collection {collection} not found, skipping...")
    
    print("\nProcessing complete!")


if __name__ == "__main__":
    main() 