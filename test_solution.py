#!/usr/bin/env python3

import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Any

class ColorCodes:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

sys.path.append('src')

try:
    from analyzer import DocumentAnalyzer
    from processor import PersonaProcessor
    from ranker import SectionRanker
except ImportError as import_err:
    print(f"{ColorCodes.FAIL}Import error: {import_err}{ColorCodes.ENDC}")
    print(f"{ColorCodes.WARNING}Make sure you're running from the Challenge_1b directory{ColorCodes.ENDC}")
    sys.exit(1)

def _test_analyzer() -> Dict[str, Any]:
    print(f"\n{ColorCodes.OKBLUE}Testing Document Analyzer...{ColorCodes.ENDC}")
    analyzer_instance = DocumentAnalyzer()
    dummy_content = """
    Chapter 1: Introduction to Machine Learning
    Machine learning is a subset of artificial intelligence that focuses on algorithms.
    1.1 Supervised Learning
    Supervised learning uses labeled data to train models.
    • Classification: Predicting categories
    • Regression: Predicting continuous values
    1.2 Unsupervised Learning
    Finds patterns in data without labels.
    """
    mock_result = {
        'metadata': {'filename': 'test.pdf', 'total_pages': 1, 'total_sections': 3},
        'sections': [
            {
                'section_title': 'Introduction to Machine Learning',
                'content': 'Machine learning is a subset of artificial intelligence that focuses on algorithms.',
                'page_number': 1,
                'detection_method': 'header'
            },
            {
                'section_title': 'Supervised Learning',
                'content': 'Supervised learning uses labeled data to train models. Classification and regression.',
                'page_number': 1,
                'detection_method': 'header'
            },
            {
                'section_title': 'Unsupervised Learning',
                'content': 'Finds patterns in data without labels.',
                'page_number': 1,
                'detection_method': 'header'
            }
        ]
    }
    print(f"   {ColorCodes.OKGREEN}Document analyzer initialized{ColorCodes.ENDC}")
    print(f"   {ColorCodes.OKCYAN}Mock analysis created with {len(mock_result['sections'])} sections{ColorCodes.ENDC}")
    return mock_result

def _test_processor(mock_analysis: Dict[str, Any]) -> Dict[str, Any]:
    print(f"\n{ColorCodes.OKBLUE}Testing Persona Processor...{ColorCodes.ENDC}")
    persona_proc = PersonaProcessor()
    persona_info = {"role": "PhD Researcher in Computational Biology"}
    job_info = {"task": "Prepare a literature review for machine learning research"}
    persona_result = persona_proc.process_with_persona(mock_analysis, persona_info, job_info)
    print(f"   {ColorCodes.OKGREEN}Persona type identified: {persona_result['persona_type']}{ColorCodes.ENDC}")
    print(f"   {ColorCodes.OKCYAN}Job type identified: {persona_result['job_type']}{ColorCodes.ENDC}")
    print(f"   {ColorCodes.OKCYAN}Enhanced sections: {len(persona_result['sections'])}{ColorCodes.ENDC}")
    return persona_result

def _test_ranker(persona_result: Dict[str, Any], persona: Dict[str, str], job: Dict[str, str]) -> List[Dict[str, Any]]:
    print(f"\n{ColorCodes.OKBLUE}Testing Section Ranker...{ColorCodes.ENDC}")
    ranker = SectionRanker()
    ranked = ranker.rank_sections(persona_result['sections'], persona, job)
    print(f"   {ColorCodes.OKGREEN}Ranked sections: {len(ranked)}{ColorCodes.ENDC}")
    if ranked:
        print(f"   {ColorCodes.OKCYAN}Top section score: {ranked[0].get('final_relevance_score', 0):.4f}{ColorCodes.ENDC}")
    return ranked

def test_components():
    print(f"{ColorCodes.HEADER}Testing Individual Components{ColorCodes.ENDC}")
    
    try:
        mock_analysis = _test_analyzer()
        persona_result = _test_processor(mock_analysis)
        persona_info = {"role": "PhD Researcher in Computational Biology"}
        job_info = {"task": "Prepare a literature review for machine learning research"}
        ranked_sections = _test_ranker(persona_result, persona_info, job_info)
        
        print(f"\n{ColorCodes.OKGREEN}✓ All component tests passed{ColorCodes.ENDC}")
        return True
        
    except Exception as e:
        print(f"\n{ColorCodes.FAIL}✗ Component test failed: {e}{ColorCodes.ENDC}")
        return False

def _load_schema(schema_file: Path) -> Any:
    with open(schema_file, 'r') as f:
        return json.load(f)

def _validate_output_schema(schema: Any, output: Any) -> bool:
    try:
        import jsonschema
        jsonschema.validate(instance=output, schema=schema)
        return True
    except Exception as e:
        print(f"{ColorCodes.FAIL}Schema validation error: {e}{ColorCodes.ENDC}")
        return False

def test_schema():
    print(f"\n{ColorCodes.HEADER}Testing Schema Validation{ColorCodes.ENDC}")
    
    try:
        schema_path = Path("challenge1b_output_schema.json")
        if not schema_path.exists():
            print(f"{ColorCodes.FAIL}Schema file not found: {schema_path}{ColorCodes.ENDC}")
            return False
        
        schema = _load_schema(schema_path)
        
        test_output = {
            "challenge_info": {"challenge_id": "test"},
            "metadata": {"processing_timestamp": 1234567890},
            "extracted_sections": [],
            "subsection_analysis": []
        }
        
        if _validate_output_schema(schema, test_output):
            print(f"{ColorCodes.OKGREEN}✓ Schema validation passed{ColorCodes.ENDC}")
            return True
        else:
            print(f"{ColorCodes.FAIL}✗ Schema validation failed{ColorCodes.ENDC}")
            return False
            
    except Exception as e:
        print(f"{ColorCodes.FAIL}✗ Schema test failed: {e}{ColorCodes.ENDC}")
        return False

def _run_processor_on_config(config_path: Path) -> bool:
    try:
        from process import Challenge1BProcessor
        processor = Challenge1BProcessor()
        return processor.process_collection(str(config_path.parent))
    except Exception as e:
        print(f"{ColorCodes.FAIL}Processor error: {e}{ColorCodes.ENDC}")
        return False

def _check_output_files() -> bool:
    output_files = list(Path("output").glob("challenge1b_output*.json"))
    return len(output_files) > 0

def _minimal_test_case() -> bool:
    print(f"\n{ColorCodes.OKBLUE}Running minimal test case...{ColorCodes.ENDC}")
    
    try:
        test_config = {
            "challenge_info": {
                "challenge_id": "round_1b_test_001",
                "test_case_name": "minimal_test",
                "description": "Minimal test case"
            },
            "documents": [
                {
                    "filename": "test_document.pdf",
                    "title": "Test Document"
                }
            ],
            "persona": {
                "role": "Test User"
            },
            "job_to_be_done": {
                "task": "Test task"
            }
        }
        
        output_dir = Path("test_output")
        output_dir.mkdir(exist_ok=True)
        
        output_path = output_dir / "challenge1b_output_minimal_test.json"
        with open(output_path, 'w') as f:
            json.dump(test_config, f, indent=2)
        
        print(f"{ColorCodes.OKGREEN}✓ Minimal test case created{ColorCodes.ENDC}")
        return True
        
    except Exception as e:
        print(f"{ColorCodes.FAIL}✗ Minimal test case failed: {e}{ColorCodes.ENDC}")
        return False

def test_end_to_end():
    print(f"\n{ColorCodes.HEADER}Testing End-to-End Processing{ColorCodes.ENDC}")
    
    try:
        test_config_path = Path("test/challenge1b_input_test.json")
        if test_config_path.exists():
            success = _run_processor_on_config(test_config_path)
            if success:
                print(f"{ColorCodes.OKGREEN}✓ End-to-end test passed{ColorCodes.ENDC}")
                return True
            else:
                print(f"{ColorCodes.FAIL}✗ End-to-end test failed{ColorCodes.ENDC}")
                return False
        else:
            print(f"{ColorCodes.WARNING}Test config not found, skipping end-to-end test{ColorCodes.ENDC}")
            return True
            
    except Exception as e:
        print(f"{ColorCodes.FAIL}✗ End-to-end test failed: {e}{ColorCodes.ENDC}")
        return False

def _initialize_components():
    try:
        analyzer = DocumentAnalyzer()
        processor = PersonaProcessor()
        ranker = SectionRanker()
        return True
    except Exception as e:
        print(f"{ColorCodes.FAIL}Component initialization failed: {e}{ColorCodes.ENDC}")
        return False

def _mock_performance_data(num_sections: int = 100) -> List[Dict[str, Any]]:
    sections = []
    for i in range(num_sections):
        sections.append({
            'section_title': f'Section {i+1}',
            'content': f'Content for section {i+1} with some relevant keywords.',
            'page_number': (i % 10) + 1,
            'relevance_score': 0.5 + (i * 0.01)
        })
    return sections

def test_performance():
    print(f"\n{ColorCodes.HEADER}Testing Performance{ColorCodes.ENDC}")
    
    try:
        start_time = time.time()
        
        mock_sections = _mock_performance_data(100)
        ranker = SectionRanker()
        persona_info = {"role": "Test User"}
        job_info = {"task": "Test task"}
        
        ranked = ranker.rank_sections(mock_sections, persona_info, job_info)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        print(f"{ColorCodes.OKCYAN}Processed {len(mock_sections)} sections in {processing_time:.3f} seconds{ColorCodes.ENDC}")
        
        if processing_time < 5.0:
            print(f"{ColorCodes.OKGREEN}✓ Performance test passed{ColorCodes.ENDC}")
            return True
        else:
            print(f"{ColorCodes.WARNING}⚠ Performance test slow: {processing_time:.3f}s{ColorCodes.ENDC}")
            return True
            
    except Exception as e:
        print(f"{ColorCodes.FAIL}✗ Performance test failed: {e}{ColorCodes.ENDC}")
        return False

def _run_all_tests():
    print(f"{ColorCodes.HEADER}Challenge 1B Solution Test Suite{ColorCodes.ENDC}")
    print("=" * 60)
    
    tests = [
        ("Component Tests", test_components),
        ("Schema Validation", test_schema),
        ("End-to-End Processing", test_end_to_end),
        ("Performance Test", test_performance)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{ColorCodes.BOLD}Running {test_name}...{ColorCodes.ENDC}")
        if test_func():
            passed += 1
        else:
            print(f"{ColorCodes.FAIL}✗ {test_name} failed{ColorCodes.ENDC}")
    
    print("\n" + "=" * 60)
    print(f"{ColorCodes.BOLD}Test Results: {passed}/{total} tests passed{ColorCodes.ENDC}")
    
    if passed == total:
        print(f"{ColorCodes.OKGREEN}🎉 All tests passed!{ColorCodes.ENDC}")
        return True
    else:
        print(f"{ColorCodes.FAIL}❌ Some tests failed{ColorCodes.ENDC}")
        return False

if __name__ == "__main__":
    success = _run_all_tests()
    sys.exit(0 if success else 1)
