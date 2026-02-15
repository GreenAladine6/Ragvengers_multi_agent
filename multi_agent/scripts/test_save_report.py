from multi_agent.utils.db_client import DatabaseClient

if __name__ == '__main__':
    c = DatabaseClient()
    report = {
        'report_content': 'smoke test from script',
        'attachment': '<html><body>smoke</body></html>',
        'summary': 'smoke-summary',
        'features_count': 0,
        'business_rules_count': 0,
        'files_analyzed': 0,
        'repo_url': 'https://example.com/repo',
        'processing_time_seconds': 0.12,
        'confidence_score': 0.95,
        'id_project': 1
    }
    res = c.save_report(report)
    print('save_report ->', res)
