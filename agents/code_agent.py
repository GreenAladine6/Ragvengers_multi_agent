from typing import Dict, Any, List
import asyncio
import ast
import json
import re

from utils.logger import logger
from core.config import config

class CodeUnderstandingAgent:
    """
    Simplified code understanding agent with batching
    """
    
    def __init__(self):
        self.analysis_count = 0
        self.total_time = 0
    
    async def analyze_batch(self, files: Dict[str, Any], batch_size: int = 5) -> Dict[str, Any]:
        """
        Analyze files in batches for better performance
        """
        all_results = []
        file_list = list(files.items())
        
        # Process in batches
        for i in range(0, len(file_list), batch_size):
            batch = file_list[i:i+batch_size]
            logger.info(f"Processing batch {i//batch_size + 1}/{(len(file_list)-1)//batch_size + 1}")
            
            # Process batch in parallel
            tasks = [self._analyze_file(path, info) for path, info in batch]
            batch_results = await asyncio.gather(*tasks)
            all_results.extend(batch_results)
        
        # Merge results
        return self._merge_results(all_results)
    
    async def _analyze_file(self, path: str, file_info: Dict) -> Dict:
        """Analyze a single file"""
        content = file_info['content']
        ext = file_info['extension']
        
        # Simple analysis based on file type
        if ext == 'py':
            analysis = self._analyze_python(content)
        elif ext in ['js', 'jsx', 'ts']:
            analysis = self._analyze_javascript(content)
        elif ext == 'html':
            analysis = self._analyze_html(content)
        else:
            analysis = self._analyze_generic(content)
        
        return {
            'file': path,
            'type': ext,
            'analysis': analysis,
            'size': len(content)
        }
    
    def _analyze_python(self, content: str) -> Dict:
        """Analyze Python code"""
        try:
            tree = ast.parse(content)
            
            # Extract info
            functions = []
            classes = []
            imports = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append({
                        'name': node.name,
                        'line': node.lineno,
                        'args': len(node.args.args)
                    })
                elif isinstance(node, ast.ClassDef):
                    classes.append({
                        'name': node.name,
                        'line': node.lineno,
                        'methods': len([n for n in node.body if isinstance(n, ast.FunctionDef)])
                    })
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    imports.append(f"{node.module}.{node.names[0].name}")
            
            # Detect business logic patterns
            business_rules = self._detect_business_rules(content)
            
            return {
                'type': 'python',
                'functions': functions,
                'classes': classes,
                'imports': imports,
                'business_rules': business_rules,
                'complexity': len(functions) + len(classes)
            }
        except:
            return self._analyze_generic(content)
    
    def _analyze_javascript(self, content: str) -> Dict:
        """Analyze JavaScript code"""
        functions = re.findall(r'function\s+(\w+)\s*\(', content)
        classes = re.findall(r'class\s+(\w+)', content)
        imports = re.findall(r'import\s+.*?from\s+[\'"]([^\'"]+)[\'"]', content)
        
        # Detect React components
        components = re.findall(r'const\s+(\w+)\s*=\s*\(?\s*props\s*\)?\s*=>', content)
        
        return {
            'type': 'javascript',
            'functions': functions,
            'classes': classes,
            'components': components,
            'imports': imports,
            'count': len(functions) + len(classes) + len(components)
        }
    
    def _analyze_html(self, content: str) -> Dict:
        """Analyze HTML"""
        from bs4 import BeautifulSoup
        
        try:
            soup = BeautifulSoup(content, 'html.parser')
            
            forms = len(soup.find_all('form'))
            inputs = len(soup.find_all('input'))
            buttons = len(soup.find_all('button'))
            links = len(soup.find_all('a'))
            
            return {
                'type': 'html',
                'forms': forms,
                'inputs': inputs,
                'buttons': buttons,
                'links': links,
                'total_elements': forms + inputs + buttons + links
            }
        except:
            return {'type': 'html', 'error': 'parsing failed'}
    
    def _analyze_generic(self, content: str) -> Dict:
        """Generic analysis fallback"""
        lines = content.split('\n')
        return {
            'type': 'generic',
            'lines': len(lines),
            'chars': len(content),
            'has_code': len(lines) > 10
        }
    
    def _detect_business_rules(self, content: str) -> List[Dict]:
        """Simple business rule detection"""
        rules = []
        
        # Look for common business rule patterns
        patterns = [
            (r'if.*(price|total|discount).*:', 'pricing_rule'),
            (r'if.*(user|admin|role).*:', 'access_rule'),
            (r'validate.*\(', 'validation_rule'),
            (r'calculate.*\(', 'calculation_rule'),
            (r'send_email.*\(', 'notification_rule'),
        ]
        
        for pattern, rule_type in patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                rules.append({
                    'type': rule_type,
                    'line': line_num,
                    'code': match.group()[:50]
                })
        
        return rules
    
    def _merge_results(self, results: List[Dict]) -> Dict[str, Any]:
        """Merge analysis results"""
        merged = {
            'total_files': len(results),
            'by_type': {},
            'business_rules': [],
            'components': [],
            'confidence': 0.0,
            'summary': {}
        }
        
        # Count by type
        for r in results:
            file_type = r['type']
            if file_type not in merged['by_type']:
                merged['by_type'][file_type] = 0
            merged['by_type'][file_type] += 1
            
            # Collect business rules
            if 'business_rules' in r['analysis']:
                merged['business_rules'].extend(r['analysis']['business_rules'])
        
        # Generate summary
        merged['summary'] = {
            'total_files': len(results),
            'python_files': merged['by_type'].get('py', 0),
            'js_files': merged['by_type'].get('js', 0) + merged['by_type'].get('jsx', 0),
            'html_files': merged['by_type'].get('html', 0),
            'business_rules_found': len(merged['business_rules'])
        }
        
        # Calculate confidence (simple heuristic)
        if len(results) > 0:
            merged['confidence'] = min(0.9, len(results) / 20)  # More files = higher confidence
        
        return merged