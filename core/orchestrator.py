# core/orchestrator.py
"""
Main orchestrator that coordinates the entire workflow
"""

import asyncio
from datetime import datetime

from github.file_downloader import GitHubFileDownloader
from agents.code_analyzer import CodeAnalyzer
from agents.business_translator import BusinessTranslator
from models.ollama_client import OllamaClient
from utils.logger import logger

class BusinessReportOrchestrator:
    """
    Orchestrates the complete workflow:
    1. Download files from GitHub
    2. Analyze each file
    3. Translate to business language
    4. Generate beautiful report
    """
    
    def __init__(self):
        self.downloader = GitHubFileDownloader()
        self.analyzer = CodeAnalyzer()
        self.translator = BusinessTranslator()
        self.ollama = OllamaClient()
    
    async def generate_report(self, repo_url: str, files_to_download: list = None):
        """
        Main method: Download files, analyze, and generate business report
        """
        logger.info(f"🚀 Starting business report generation for {repo_url}")
        start_time = datetime.now()
        
        # Step 1: Parse GitHub URL
        repo_info = self.downloader.parse_github_url(repo_url)
        logger.info(f"📦 Repository: {repo_info['owner']}/{repo_info['repo']}")
        
        # Step 2: Download files
        if not files_to_download:
            # Default important files to check
            files_to_download = [
                "README.md",
                "app.py",
                "main.py",
                "routes.py",
                "models.py",
                "templates/index.html",
                "templates/login.html",
                "static/js/main.js",
                "static/css/style.css"
            ]
        
        logger.info(f"📥 Downloading {len(files_to_download)} files...")
        async with self.downloader as downloader:
            downloaded_files = await downloader.download_multiple_files(
                repo_info['owner'],
                repo_info['repo'],
                files_to_download
            )
        
        logger.info(f"✅ Downloaded {len(downloaded_files)} files")
        
        # Step 3: Analyze each file
        logger.info("🔍 Analyzing files...")
        file_analyses = {}
        for path, file_info in downloaded_files.items():
            analysis = self.analyzer.analyze_file(file_info)
            file_analyses[path] = analysis
            logger.info(f"   ✅ Analyzed {path} - {analysis.get('type', 'unknown')}")
        
        # Step 4: Translate to business language
        logger.info("💼 Translating to business language...")
        business_report = self.translator.translate(file_analyses)
        
        # Step 5: Generate final HTML report
        logger.info("📊 Generating business report...")
        html_report = await self._generate_html_report(
            repo_url,
            downloaded_files,
            file_analyses,
            business_report,
            start_time
        )
        
        # Step 6: Print the report (no saving)
        print("\n" + "="*80)
        print(html_report)
        print("="*80)
        
        # Also print a quick summary
        self._print_summary(business_report, len(downloaded_files), start_time)
        
        return html_report
    
    async def _generate_html_report(self, repo_url, files, analyses, business_report, start_time):
        """Generate beautiful HTML report"""
        
        # Count business items
        features_count = len(business_report.get('features', []))
        ui_count = len(business_report.get('user_interfaces', []))
        rules_count = len(business_report.get('business_logic', []))
        
        # Build features HTML
        features_html = ""
        for feature in business_report.get('features', [])[:5]:
            features_html += f"""
            <div class="feature-item">
                <span class="feature-icon">✨</span>
                <span>{feature}</span>
            </div>
            """
        
        # Build UI HTML
        ui_html = ""
        for ui in business_report.get('user_interfaces', [])[:5]:
            ui_html += f"""
            <div class="feature-item">
                <span class="feature-icon">🖥️</span>
                <span>{ui}</span>
            </div>
            """
        
        # Build business rules HTML
        rules_html = ""
        for rule in business_report.get('business_logic', [])[:5]:
            if isinstance(rule, dict):
                rules_html += f"""
                <div class="feature-item">
                    <span class="feature-icon">🧮</span>
                    <span><strong>Rule:</strong> {rule.get('description', '')[:100]}</span>
                </div>
                """
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return f"""
<!DOCTYPE html>
<html>
<head>
    <title>📊 Business Impact Report</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .container {{
            background: white;
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
        }}
        .header h1 {{
            font-size: 2.5em;
            margin: 0;
            font-weight: 300;
        }}
        .header h1 strong {{
            font-weight: 700;
        }}
        .header .repo {{
            font-size: 1.2em;
            opacity: 0.9;
            margin-top: 10px;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            padding: 30px;
            background: #f8fafc;
        }}
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }}
        .stat-value {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }}
        .stat-label {{
            color: #666;
            font-size: 0.9em;
            margin-top: 5px;
        }}
        .section {{
            padding: 30px;
            border-bottom: 1px solid #e0e0e0;
        }}
        .section-title {{
            font-size: 1.5em;
            color: #333;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .section-title::after {{
            content: '';
            flex: 1;
            height: 2px;
            background: linear-gradient(90deg, #667eea, transparent);
        }}
        .feature-item {{
            padding: 15px;
            background: #f8fafc;
            border-radius: 8px;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 10px;
            border-left: 3px solid #667eea;
        }}
        .feature-icon {{
            font-size: 1.2em;
        }}
        .summary-box {{
            background: linear-gradient(135deg, #f5f7fa 0%, #e4e8f0 100%);
            padding: 25px;
            border-radius: 10px;
            margin-bottom: 20px;
            font-size: 1.1em;
        }}
        .file-list {{
            background: #f8fafc;
            padding: 20px;
            border-radius: 8px;
        }}
        .file-item {{
            padding: 8px;
            border-bottom: 1px solid #e0e0e0;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .file-item:last-child {{
            border-bottom: none;
        }}
        .badge {{
            display: inline-block;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 0.8em;
            font-weight: bold;
            margin-left: 10px;
        }}
        .badge-python {{ background: #3776ab; color: white; }}
        .badge-js {{ background: #f7df1e; color: black; }}
        .badge-html {{ background: #e34c26; color: white; }}
        .badge-css {{ background: #264de4; color: white; }}
        .badge-docs {{ background: #28a745; color: white; }}
        .footer {{
            text-align: center;
            padding: 30px;
            color: #666;
            background: #f8fafc;
        }}
        .timestamp {{
            color: #999;
            font-size: 0.9em;
            margin-top: 10px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 <strong>Business Impact</strong> Report</h1>
            <p class="repo">🔗 {repo_url}</p>
            <p class="timestamp">Generated in {processing_time:.1f} seconds</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">{len(files)}</div>
                <div class="stat-label">Files Analyzed</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{features_count}</div>
                <div class="stat-label">New Features</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{ui_count}</div>
                <div class="stat-label">UI Components</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{rules_count}</div>
                <div class="stat-label">Business Rules</div>
            </div>
        </div>
        
        <div class="section">
            <div class="section-title">📋 Executive Summary</div>
            <div class="summary-box">
                {business_report.get('summary', 'Analysis complete. See details below.')}
            </div>
        </div>
        
        <div class="section">
            <div class="section-title">✨ What's New</div>
            {features_html if features_html else '<p>No new features detected in this update.</p>'}
        </div>
        
        <div class="section">
            <div class="section-title">🖥️ User Interface Updates</div>
            {ui_html if ui_html else '<p>No UI changes detected.</p>'}
        </div>
        
        <div class="section">
            <div class="section-title">🧮 Business Logic</div>
            {rules_html if rules_html else '<p>No new business rules detected.</p>'}
        </div>
        
        <div class="section">
            <div class="section-title">📁 Files Analyzed</div>
            <div class="file-list">
"""

        # Add file list
        for path, analysis in analyses.items():
            file_type = analysis.get('type', 'unknown')
            badge_class = {
                'python': 'badge-python',
                'javascript': 'badge-js',
                'html': 'badge-html',
                'css': 'badge-css',
                'documentation': 'badge-docs'
            }.get(file_type, '')
            
            html_report += f"""
                <div class="file-item">
                    <span>📄 {path}</span>
                    <span class="badge {badge_class}">{file_type}</span>
                </div>
            """
        
        html_report += f"""
            </div>
        </div>
        
        <div class="footer">
            <p>🤖 Generated by AI Agents • DeepSeek + Ollama</p>
            <p>This report translates code changes into business value</p>
        </div>
    </div>
</body>
</html>
"""
    
    def _print_summary(self, business_report, files_count, start_time):
        """Print a quick console summary"""
        processing_time = (datetime.now() - start_time).total_seconds()
        
        print("\n" + "="*60)
        print("📊 BUSINESS IMPACT SUMMARY")
        print("="*60)
        print(f"📁 Files analyzed: {files_count}")
        print(f"⏱️  Processing time: {processing_time:.1f}s")
        print("\n✨ Key Business Impact:")
        
        for feature in business_report.get('features', [])[:3]:
            print(f"   • {feature}")
        for ui in business_report.get('user_interfaces', [])[:3]:
            print(f"   • {ui}")
        for rule in business_report.get('business_logic', [])[:3]:
            if isinstance(rule, dict):
                print(f"   • {rule.get('description', '')[:80]}")
        
        print("\n" + "="*60)
    # In core/orchestrator.py, update the generate_report method:

async def generate_report(self, repo_url: str, files_to_download: list = None):
    """
    Main method: Download files, analyze, and generate business report
    """
    logger.info(f"🚀 Starting business report generation for {repo_url}")
    start_time = datetime.now()
    
    # ... (existing download and analysis code remains the same)
    
    # After analysis, prepare metadata for report
    file_details = {}
    for path, analysis in file_analyses.items():
        file_details[path] = analysis.get('type', 'unknown')
    
    metadata = {
        'repo_url': repo_url,
        'files_fetched': len(downloaded_files),
        'total_files': len(files_to_download),
        'processing_time': (datetime.now() - start_time).total_seconds(),
        'api_calls': self.downloader.api_calls,
        'cache_hits': 0,  # You can track this if needed
        'confidence': business_report.get('confidence', 0.85),
        'file_details': file_details
    }
    
    # Generate text report
    logger.info("📊 Generating text business report...")
    text_report = await self.report_agent.generate(business_report, metadata)
    
    # Print the beautiful text report
    print("\n" + "="*80)
    print(text_report['text'])
    print("="*80)
    
    # Also print quick summary
    self._print_summary(text_report, len(downloaded_files), start_time)
    
    return text_report