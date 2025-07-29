import fitz
import re
from pathlib import Path
from typing import Dict, List, Any, Tuple
from datetime import datetime


class DocumentAnalyzer:
    
    def __init__(self):
        self.min_section_length = 30
        self.max_section_length = 2000
        self.max_sections = 50
        self.max_lookahead_lines = 5
    
    def analyze_document(self, file_path: str) -> Dict[str, Any]:
        try:
            doc = fitz.open(file_path)
            full_text, page_contents = self._extract_pdf_content(doc)
            doc.close()
            
            sections = self._detect_sections(full_text, Path(file_path).name, page_contents)
            metadata = self._generate_metadata(file_path, page_contents, full_text, sections)
            
            return {
                "metadata": metadata,
                "full_text": full_text,
                "pages": page_contents,
                "sections": sections
            }
            
        except Exception as e:
            return self._create_error_response(file_path, e)
    
    def _extract_pdf_content(self, doc) -> Tuple[str, List[Dict]]:
        full_text = ""
        page_contents = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            page_text = page.get_text()
            full_text += page_text + "\n"
            
            page_contents.append({
                "page_number": page_num + 1,
                "text": page_text.strip(),
                "char_count": len(page_text)
            })
        
        return full_text, page_contents
    
    def _generate_metadata(self, file_path: str, pages: List[Dict], 
                          full_text: str, sections: List[Dict]) -> Dict[str, Any]:
        return {
            "filename": Path(file_path).name,
            "total_pages": len(pages),
            "total_characters": len(full_text),
            "total_sections": len(sections),
            "processing_timestamp": datetime.now().isoformat()
        }
    
    def _create_error_response(self, file_path: str, error: Exception) -> Dict[str, Any]:
        print(f"Error analyzing document {file_path}: {str(error)}")
        return {
            "metadata": {"filename": Path(file_path).name, "error": str(error)},
            "full_text": "",
            "pages": [],
            "sections": []
        }
    
    def _detect_sections(self, text: str, filename: str, pages: List[Dict]) -> List[Dict[str, Any]]:
        sections = []
        
        sections.extend(self._detect_by_headers(text, pages))
        sections.extend(self._detect_by_paragraphs(text, pages))
        sections.extend(self._detect_by_lines(text, pages))
        
        return self._process_detected_sections(sections, filename)
    
    def _process_detected_sections(self, sections: List[Dict[str, Any]], filename: str) -> List[Dict[str, Any]]:
        processed_sections = []
        seen_titles = set()
        
        for section in sections:
            if self._is_valid_section(section, seen_titles):
                processed_sections.append(section)
                seen_titles.add(section['section_title'].lower())
        
        return processed_sections[:self.max_sections]
    
    def _is_valid_section(self, section: Dict[str, Any], seen_titles: set) -> bool:
        content = section.get('content', '')
        title = section.get('section_title', '')
        return (len(content) >= self.min_section_length and 
                len(content) <= self.max_section_length and
                title.lower() not in seen_titles)
    
    def _detect_by_headers(self, text: str, pages: List[Dict]) -> List[Dict[str, Any]]:
        sections = []
        patterns = self._get_header_patterns()
        
        for page_info in pages:
            sections.extend(self._find_headers_in_page(page_info, patterns))
        
        return sections
    
    def _get_header_patterns(self) -> List[str]:
        return [
            r'^([A-Z][A-Z\s&]+)$',
            r'^(\d+\.\s+[A-Z][A-Za-z\s]+)$',
            r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s*:)$',
            r'^([A-Z][A-Z\s]+(?:\s+[A-Z][A-Z\s]+)*)$'
        ]
    
    def _find_headers_in_page(self, page_info: Dict, patterns: List[str]) -> List[Dict[str, Any]]:
        sections = []
        page_text = page_info['text']
        page_num = page_info['page_number']
        lines = page_text.split('\n')
        
        for i, line in enumerate(lines):
            if self._is_valid_line(line):
                title = self._match_header_patterns(line, patterns)
                if title:
                    content = self._extract_content_after_header(page_text, line)
                    if content:
                        sections.append(self._create_header_section(title, content, page_num))
        
        return sections
    
    def _is_valid_line(self, line: str) -> bool:
        return len(line.strip()) > 0 and len(line.strip()) < 100
    
    def _match_header_patterns(self, line: str, patterns: List[str]) -> str:
        line = line.strip()
        for pattern in patterns:
            match = re.match(pattern, line)
            if match:
                title = match.group(1).strip().rstrip(':')
                return title
        return ""
    
    def _create_header_section(self, title: str, page_text: str, page_num: int) -> Dict[str, Any]:
        return {
            'section_title': title,
            'content': page_text[:self.max_section_length],
            'page_number': page_num,
            'detection_method': 'header',
            'confidence': self._calculate_confidence({'section_title': title, 'content': page_text})
        }
    
    def _detect_by_paragraphs(self, text: str, pages: List[Dict]) -> List[Dict[str, Any]]:
        sections = []
        
        for page_info in pages:
            sections.extend(self._extract_paragraph_sections(page_info))
        
        return sections
    
    def _extract_paragraph_sections(self, page_info: Dict) -> List[Dict[str, Any]]:
        sections = []
        page_text = page_info['text']
        page_num = page_info['page_number']
        
        paragraphs = page_text.split('\n\n')
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if self._is_valid_paragraph_length(paragraph):
                sections.append(self._create_paragraph_section(paragraph, page_num))
        
        return sections
    
    def _is_valid_paragraph_length(self, paragraph: str) -> bool:
        return self.min_section_length <= len(paragraph) <= self.max_section_length
    
    def _create_paragraph_section(self, paragraph: str, page_num: int) -> Dict[str, Any]:
        return {
            'section_title': self._generate_paragraph_title(paragraph),
            'content': paragraph,
            'page_number': page_num,
            'detection_method': 'paragraph',
            'confidence': self._calculate_confidence({'section_title': '', 'content': paragraph})
        }
    
    def _generate_paragraph_title(self, paragraph: str) -> str:
        words = paragraph.split()[:5]
        return ' '.join(words) + '...'
    
    def _detect_by_lines(self, text: str, pages: List[Dict]) -> List[Dict[str, Any]]:
        sections = []
        
        for page_info in pages:
            sections.extend(self._extract_list_sections(page_info))
        
        return sections
    
    def _extract_list_sections(self, page_info: Dict) -> List[Dict[str, Any]]:
        sections = []
        page_text = page_info['text']
        page_num = page_info['page_number']
        lines = page_text.split('\n')
        
        i = 0
        while i < len(lines):
            if self._is_list_item(lines[i]):
                start_index = i
                while i < len(lines) and (self._is_list_item(lines[i]) or self._is_continuation_line(lines[i])):
                    i += 1
                
                if i - start_index >= 2:
                    sections.append(self._create_list_section(lines, start_index, page_num))
            else:
                i += 1
        
        return sections
    
    def _is_list_item(self, line: str) -> bool:
        line = line.strip()
        return (line.startswith('•') or line.startswith('-') or 
                re.match(r'^\d+\.', line) or re.match(r'^[a-z]\)', line))
    
    def _create_list_section(self, lines: List[str], start_index: int, page_num: int) -> Dict[str, Any]:
        content = self._gather_list_content(lines, start_index)
        return {
            'section_title': f'List Section {start_index + 1}',
            'content': content,
            'page_number': page_num,
            'detection_method': 'list',
            'confidence': self._calculate_confidence({'section_title': '', 'content': content})
        }
    
    def _gather_list_content(self, lines: List[str], start_index: int) -> str:
        content_lines = []
        i = start_index
        
        while i < len(lines) and (self._is_list_item(lines[i]) or self._is_continuation_line(lines[i])):
            content_lines.append(lines[i].strip())
            i += 1
        
        return '\n'.join(content_lines)
    
    def _is_continuation_line(self, line: str) -> bool:
        line = line.strip()
        return len(line) > 0 and not line.startswith('•') and not line.startswith('-') and not re.match(r'^\d+\.', line)
    
    def _extract_content_after_header(self, page_text: str, header_line: str) -> str:
        lines = page_text.split('\n')
        content_lines = []
        header_found = False
        
        for line in lines:
            if self._is_header_line(line, header_line):
                header_found = True
                continue
            
            if header_found:
                if self._should_stop_content_extraction(line, content_lines):
                    break
                content_lines.append(line)
        
        content = '\n'.join(content_lines).strip()
        return content if len(content) >= self.min_section_length else ""
    
    def _is_header_line(self, line: str, header_line: str) -> bool:
        return line.strip() == header_line.strip()
    
    def _should_stop_content_extraction(self, line: str, content_lines: List[str]) -> bool:
        if not line.strip():
            return len(content_lines) > 0
        
        if len(content_lines) > 20:
            return True
        
        if re.match(r'^[A-Z][A-Z\s]+$', line.strip()):
            return True
        
        return False
    
    def _calculate_confidence(self, section: Dict[str, Any]) -> float:
        base_score = self._get_base_confidence_score()
        method_score = self._get_method_score(section.get('detection_method', 'unknown'))
        quality_score = self._get_content_quality_score(section.get('content', ''), section.get('section_title', ''))
        
        return min(1.0, base_score + method_score + quality_score)
    
    def _get_base_confidence_score(self) -> float:
        return 0.3
    
    def _get_method_score(self, method: str) -> float:
        method_scores = {
            'header': 0.4,
            'paragraph': 0.3,
            'list': 0.2,
            'unknown': 0.1
        }
        return method_scores.get(method, 0.1)
    
    def _get_content_quality_score(self, content: str, title: str) -> float:
        if not content:
            return 0.0
        
        length_score = min(1.0, len(content) / 500)
        title_score = 0.2 if title and len(title) > 3 else 0.0
        
        return length_score + title_score