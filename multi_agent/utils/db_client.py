# utils/db_client.py
import os
import psycopg2
from datetime import datetime
from dotenv import load_dotenv
from utils.logger import logger

load_dotenv()

class DatabaseClient:
    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL", "postgresql://postgres:green2690@localhost/ragvengers_db")
        self.conn = None

    def connect(self):
        try:
            self.conn = psycopg2.connect(self.db_url)
            return self.conn
        except Exception as e:
            logger.error(f"❌ Failed to connect to database: {e}")
            return None

    def save_report(self, report_data: dict):
        """
        Saves the generated report to the database.
        report_data expects:
        - report_content (str)
        - summary (str)
        - features_count (int)
        - business_rules_count (int)
        - files_analyzed (int)
        - repo_url (str)
        - processing_time_seconds (float)
        - confidence_score (float)
        - id_project (int)
        """
        conn = self.connect()
        if not conn:
            return False

        try:
            cur = conn.cursor()
            query = """
                INSERT INTO report (
                    creation_date, report_content, attachment, summary, features_count, 
                    business_rules_count, files_analyzed, repo_url, 
                    processing_time_seconds, confidence_score, id_project
                ) VALUES (
                    CURRENT_DATE, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                ) RETURNING id_report;
            """
            cur.execute(query, (
                report_data['report_content'],
                report_data.get('attachment'),
                report_data.get('summary'),
                report_data.get('features_count', 0),
                report_data.get('business_rules_count', 0),
                report_data.get('files_analyzed', 0),
                report_data.get('repo_url'),
                report_data.get('processing_time_seconds', 0),
                report_data.get('confidence_score', 0),
                report_data['id_project']
            ))
            report_id = cur.fetchone()[0]
            conn.commit()
            cur.close()
            conn.close()
            logger.info(f"✅ Report saved successfully to database (ID: {report_id})")
            return report_id
        except Exception as e:
            logger.error(f"❌ Failed to save report to database: {e}")
            if conn:
                conn.rollback()
                conn.close()
            return False
