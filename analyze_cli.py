#!/usr/bin/env python3
"""
VCHASNO Analytics CLI Script
Performs document analysis and sends data to Lambda /analyze endpoint
"""

import argparse
import json
import sys
from datetime import datetime
import requests


class VCHASNOAnalyticsCLI:
    def __init__(self, endpoint_url):
        self.endpoint_url = endpoint_url
        
    def analyze_document(self, doc_id, doc_type):
        """Analyze a document and send to Lambda endpoint"""
        payload = {
            "document_id": doc_id,
            "document_type": doc_type,
            "timestamp": datetime.utcnow().isoformat(),
            "source": "cli"
        }
        
        try:
            response = requests.post(
                f"{self.endpoint_url}/analyze",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error analyzing document: {e}", file=sys.stderr)
            return None
    
    def batch_analyze(self, doc_ids, doc_type):
        """Analyze multiple documents"""
        results = []
        for doc_id in doc_ids:
            print(f"Analyzing document {doc_id}...")
            result = self.analyze_document(doc_id, doc_type)
            if result:
                results.append(result)
        return results
    
    def get_stats(self):
        """Get analytics statistics"""
        try:
            response = requests.get(f"{self.endpoint_url}/stats")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching stats: {e}", file=sys.stderr)
            return None


def main():
    parser = argparse.ArgumentParser(
        description="VCHASNO Analytics CLI - Document Analysis Tool"
    )
    parser.add_argument(
        "--endpoint",
        default="https://api.vchasno.com",
        help="Lambda API endpoint URL"
    )
    parser.add_argument(
        "--action",
        choices=["analyze", "batch", "stats"],
        required=True,
        help="Action to perform"
    )
    parser.add_argument(
        "--doc-id",
        help="Document ID to analyze"
    )
    parser.add_argument(
        "--doc-type",
        default="contract",
        help="Document type (contract, compliance, etc.)"
    )
    parser.add_argument(
        "--batch-file",
        help="JSON file with list of document IDs for batch processing"
    )
    
    args = parser.parse_args()
    
    cli = VCHASNOAnalyticsCLI(args.endpoint)
    
    if args.action == "analyze":
        if not args.doc_id:
            print("Error: --doc-id required for analyze action", file=sys.stderr)
            sys.exit(1)
        result = cli.analyze_document(args.doc_id, args.doc_type)
        if result:
            print(json.dumps(result, indent=2))
    
    elif args.action == "batch":
        if not args.batch_file:
            print("Error: --batch-file required for batch action", file=sys.stderr)
            sys.exit(1)
        with open(args.batch_file) as f:
            doc_ids = json.load(f)
        results = cli.batch_analyze(doc_ids, args.doc_type)
        print(json.dumps(results, indent=2))
    
    elif args.action == "stats":
        stats = cli.get_stats()
        if stats:
            print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
