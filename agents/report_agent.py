from typing import Dict, Any, Optional
from datetime import datetime
import jinja2
import json

class ReportGeneratorAgent:
    """
    Simplified report generator
    """
    
    def __init__(self, template_dir: str = "templates"):
        self.template_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(template_dir),
            autoescape=True
        )
    
    async def generate(self, business_context: Dict, metadata: Dict) -> Dict[str, Any]:
        """Generate report from business context"""
        
        # Create report data
        report_data = self._prepare_report_data(business_context, metadata)
        
        # Generate HTML
        html = await self._generate_html(report_data)
        
        # Generate JSON version
        json_data = json.dumps(report_data, indent=2)
        
        return {
            'html': html,
            'json': json_data,
            'summary': report_data['summary'],
            'generated_at': datetime.now().isoformat()
        }
    
    def _prepare_report_data(self, context: Dict, metadata: Dict) -> Dict:
        """Prepare data for report"""
        
        # Extract key metrics
        summary = context.get('summary', {})
        business_rules = context.get('business_rules', [])
        
        # Group business rules by type
        rules_by_type = {}
        for rule in business_rules:
            rule_type = rule.get('type', 'other')
            if rule_type not in rules_by_type:
                rules_by_type[rule_type] = []
            rules_by_type[rule_type].append(rule)
        
        return {
            'project_info': {
                'repo_url': metadata.get('repo_url', 'N/A'),
                'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M'),
                'files_analyzed': metadata.get('files_analyzed', 0),
                'total_files_in_repo': metadata.get('total_files', 0),
                'coverage': f"{metadata.get('files_analyzed', 0)/max(metadata.get('total_files', 1),1)*100:.1f}%"
            },
            'metrics': {
                'total_files': summary.get('total_files', 0),
                'python_files': summary.get('python_files', 0),
                'js_files': summary.get('js_files', 0),
                'html_files': summary.get('html_files', 0),
                'business_rules': len(business_rules),
                'confidence': f"{metadata.get('confidence', 0)*100:.1f}%"
            },
            'business_rules': {
                'total': len(business_rules),
                'by_type': {k: len(v) for k, v in rules_by_type.items()},
                'examples': business_rules[:5]  # Show first 5
            },
            'performance': {
                'api_calls': metadata.get('api_calls', 0),
                'cache_hits': metadata.get('cache_hits', 0),
                'processing_time': f"{metadata.get('processing_time', 0):.2f}s",
                'sampling_rate': f"{metadata.get('files_analyzed', 0)}/{metadata.get('total_files', 0)}"
            },
            'summary': f"""
                Analysis complete! Analyzed {metadata.get('files_analyzed', 0)} out of 
                {metadata.get('total_files', 0)} files ({metadata.get('files_analyzed', 0)/max(metadata.get('total_files', 1),1)*100:.1f}% coverage).
                Found {len(business_rules)} business rules across {summary.get('python_files', 0)} Python, 
                {summary.get('js_files', 0)} JavaScript, and {summary.get('html_files', 0)} HTML files.
                Confidence score: {metadata.get('confidence', 0)*100:.1f}%
            """
        }
    
    async def _generate_html(self, data: Dict) -> str:
        """Generate HTML report"""
        template = self.template_env.get_template("report_template.html")
        return template.render(
            data=data,
            generated_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )