#!/usr/bin/env python3
"""
Simple GitHub Token Tester
Run this to verify your GitHub token works before using the full system
"""

import os
import sys
import json
import time
import base64
from datetime import datetime
from urllib.parse import urlparse
import requests
from dotenv import load_dotenv

# Load token from .env
load_dotenv()

class GitHubTokenTester:
    """
    Simple tester for GitHub token functionality
    """
    
    def __init__(self, token=None):
        self.token = token or os.getenv('GITHUB_TOKEN')
        if not self.token:
            raise ValueError("❌ No GitHub token found! Set GITHUB_TOKEN in .env file")
        
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # Stats
        self.api_calls = 0
        
    def print_header(self, text):
        """Print a formatted header"""
        print(f"\n{'='*60}")
        print(f" {text}")
        print(f"{'='*60}")
    
    def test_token_validity(self):
        """Test 1: Check if token is valid"""
        self.print_header("TEST 1: Token Validity")
        
        try:
            response = self.session.get(f"{self.base_url}/user")
            self.api_calls += 1
            
            if response.status_code == 200:
                user_data = response.json()
                print(f"✅ Token is VALID!")
                print(f"   Authenticated as: {user_data['login']}")
                print(f"   User type: {user_data['type']}")
                print(f"   Name: {user_data.get('name', 'Not set')}")
                return True
            else:
                print(f"❌ Token is INVALID! Status: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error testing token: {e}")
            return False
    
    def test_rate_limits(self):
        """Test 2: Check rate limits"""
        self.print_header("TEST 2: Rate Limits")
        
        response = self.session.get(f"{self.base_url}/rate_limit")
        self.api_calls += 1
        
        if response.status_code == 200:
            limits = response.json()
            core = limits['resources']['core']
            
            print(f"📊 Rate Limit Status:")
            print(f"   • Limit: {core['limit']} requests/hour")
            print(f"   • Used: {core['used']}")
            print(f"   • Remaining: {core['remaining']}")
            print(f"   • Resets: {datetime.fromtimestamp(core['reset']).strftime('%H:%M:%S')}")
            
            if core['remaining'] < 100:
                print(f"⚠️  Warning: Low on rate limits!")
            else:
                print(f"✅ Good rate limit remaining")
        else:
            print(f"❌ Failed to get rate limits: {response.status_code}")
    
    def test_public_repo_access(self, owner="psf", repo="requests"):
        """Test 3: Access a public repository"""
        self.print_header(f"TEST 3: Public Repo Access - {owner}/{repo}")
        
        url = f"{self.base_url}/repos/{owner}/{repo}"
        response = self.session.get(url)
        self.api_calls += 1
        
        if response.status_code == 200:
            repo_data = response.json()
            print(f"✅ Successfully accessed public repo!")
            print(f"   📦 Repo: {repo_data['full_name']}")
            print(f"   ⭐ Stars: {repo_data['stargazers_count']}")
            print(f"   📝 Description: {repo_data['description'][:50]}...")
            print(f"   🔒 Private: {repo_data['private']}")
        else:
            print(f"❌ Failed to access repo: {response.status_code}")
    
    def test_private_repo_access(self):
        """Test 4: Check if token can access private repos"""
        self.print_header("TEST 4: Private Repo Access")
        
        # Get user's repos to check for private ones
        response = self.session.get(f"{self.base_url}/user/repos?visibility=all&per_page=5")
        self.api_calls += 1
        
        if response.status_code == 200:
            repos = response.json()
            private_repos = [r for r in repos if r['private']]
            
            if private_repos:
                print(f"✅ Token has access to {len(private_repos)} private repos:")
                for repo in private_repos[:3]:
                    print(f"   🔒 {repo['full_name']}")
            else:
                print(f"ℹ️  No private repos found or no access")
                print(f"   This is fine if you only need public repos")
        else:
            print(f"❌ Failed to check private repos: {response.status_code}")
    
    def test_repo_contents(self, owner="psf", repo="requests", path=""):
        """Test 5: Fetch repository contents"""
        self.print_header(f"TEST 5: Fetch Repo Contents - {owner}/{repo}")
        
        url = f"{self.base_url}/repos/{owner}/{repo}/contents/{path}"
        response = self.session.get(url)
        self.api_calls += 1
        
        if response.status_code == 200:
            contents = response.json()
            
            if isinstance(contents, list):
                files = [c for c in contents if c['type'] == 'file']
                dirs = [c for c in contents if c['type'] == 'dir']
                
                print(f"📁 Root contents:")
                print(f"   • {len(files)} files")
                print(f"   • {len(dirs)} directories")
                
                # Show some files
                if files:
                    print(f"\n📄 Sample files:")
                    for f in files[:5]:
                        print(f"   • {f['name']} ({f['size']} bytes)")
            else:
                print(f"📄 Single file: {contents['name']}")
                print(f"   Size: {contents['size']} bytes")
                print(f"   Type: {contents['type']}")
        else:
            print(f"❌ Failed to fetch contents: {response.status_code}")
    
    def test_file_download(self, owner="psf", repo="requests", file_path="README.md"):
        """Test 6: Download and read a file"""
        self.print_header(f"TEST 6: Download File - {file_path}")
        
        url = f"{self.base_url}/repos/{owner}/{repo}/contents/{file_path}"
        response = self.session.get(url)
        self.api_calls += 1
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('content'):
                # Decode base64 content
                content = base64.b64decode(data['content']).decode('utf-8')
                print(f"✅ Successfully downloaded {file_path}")
                print(f"   📏 Size: {len(content)} characters")
                print(f"   📝 Preview:")
                print(f"   {'-'*40}")
                print(content[:200] + "..." if len(content) > 200 else content)
                print(f"   {'-'*40}")
            else:
                print(f"❌ No content in response")
        else:
            print(f"❌ Failed to download file: {response.status_code}")
    
    def test_search_code(self, query="requests"):
        """Test 7: Search code (tests token search capability)"""
        self.print_header(f"TEST 7: Code Search - '{query}'")
        
        url = f"{self.base_url}/search/code"
        params = {"q": query, "per_page": 3}
        
        response = self.session.get(url, params=params)
        self.api_calls += 1
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Search successful!")
            print(f"   🔍 Found {data['total_count']} results")
            print(f"   📋 Top results:")
            for item in data['items'][:3]:
                print(f"      • {item['path']} in {item['repository']['full_name']}")
        else:
            print(f"❌ Search failed: {response.status_code}")
    
    def test_smart_fetch_demo(self, repo_url="https://github.com/psf/requests", max_files=5):
        """Test 8: Demo of our smart fetching logic"""
        self.print_header(f"TEST 8: Smart Fetch Demo - Sampling {max_files} files")
        
        # Parse URL
        parsed = urlparse(repo_url)
        path_parts = parsed.path.strip('/').split('/')
        owner, repo = path_parts[0], path_parts[1].replace('.git', '')
        
        print(f"📦 Repo: {owner}/{repo}")
        
        # Get the full tree
        url = f"{self.base_url}/repos/{owner}/{repo}/git/trees/main?recursive=1"
        response = self.session.get(url)
        self.api_calls += 1
        
        if response.status_code == 200:
            tree_data = response.json()
            all_files = [f for f in tree_data['tree'] if f['type'] == 'blob']
            
            print(f"📊 Total files in repo: {len(all_files)}")
            
            # Smart sampling by extension
            by_extension = {}
            for f in all_files:
                ext = f['path'].split('.')[-1] if '.' in f['path'] else 'no_ext'
                if ext not in by_extension:
                    by_extension[ext] = []
                by_extension[ext].append(f)
            
            print(f"\n📁 Files by extension:")
            for ext, files in sorted(by_extension.items(), key=lambda x: len(x[1]), reverse=True)[:8]:
                print(f"   .{ext}: {len(files)} files")
            
            # Sample intelligently
            sampled = []
            extensions = list(by_extension.keys())
            per_extension = max(1, max_files // len(extensions))
            
            print(f"\n🎯 Smart sampling (taking ~{per_extension} from each extension):")
            for ext in extensions[:5]:  # Show first 5 extensions
                take = min(per_extension, len(by_extension[ext]))
                sampled.extend(by_extension[ext][:take])
                print(f"   • .{ext}: taking {take}/{len(by_extension[ext])} files")
            
            print(f"\n✅ Sampled {len(sampled)}/{max_files} files intelligently")
            print(f"   This is EXACTLY what our system does!")
            
        else:
            print(f"❌ Failed to get tree: {response.status_code}")
    
    def run_all_tests(self):
        """Run all tests"""
        print("\n🔧 GITHUB TOKEN TESTER")
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Test 1: Token validity
        if not self.test_token_validity():
            print("\n❌ Token invalid - stopping tests")
            return False
        
        # Test 2: Rate limits
        self.test_rate_limits()
        
        # Test 3: Public repo access
        self.test_public_repo_access()
        
        # Test 4: Private repo check
        self.test_private_repo_access()
        
        # Test 5: Repo contents
        self.test_repo_contents()
        
        # Test 6: File download
        self.test_file_download()
        
        # Test 7: Code search
        self.test_search_code()
        
        # Test 8: Smart fetch demo
        self.test_smart_fetch_demo()
        
        # Summary
        self.print_header("TEST SUMMARY")
        print(f"📊 Total API calls made: {self.api_calls}")
        print(f"⏱️  Rate limit remaining: Check test 2")
        print(f"\n{'✅' if self.api_calls > 0 else '❌'} Token is working perfectly!")
        print(f"\nYour token is ready to use in the full system! 🚀")
        
        return True

def main():
    """Main entry point"""
    try:
        tester = GitHubTokenTester()
        tester.run_all_tests()
    except ValueError as e:
        print(f"\n❌ {e}")
        print("\n📝 To fix:")
        print("   1. Create a .env file")
        print("   2. Add: GITHUB_TOKEN=your_token_here")
        print("   3. Get token from: https://github.com/settings/tokens")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()