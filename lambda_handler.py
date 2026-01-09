"""
AWS Lambda Handler for VCHASNO /analyze Endpoint
Processes document analysis requests from DynamoDB Streams via EventBridge
"""

import json
import os
import boto3
from datetime import datetime
import logging

# Initialize AWS clients
dynamodb = boto3.client('dynamodb')
cloudwatch = boto3.client('cloudwatch')
s3 = boto3.client('s3')

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Environment variables
METRICS_NAMESPACE = os.environ.get('METRICS_NAMESPACE', 'VCHASNO/Analytics')
RESULTS_BUCKET = os.environ.get('RESULTS_BUCKET', 'vchasno-analysis-results')


def lambda_handler(event, context):
    """
    Main Lambda handler for /analyze endpoint
    Processes document analysis requests and stores results
    """
    try:
        logger.info(f"Received event: {json.dumps(event)}")
        
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        
        # Extract document parameters
        document_id = body.get('document_id')
        document_type = body.get('document_type', 'contract')
        source = body.get('source', 'unknown')
        
        if not document_id:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'document_id is required'
                })
            }
        
        # Perform analysis
        analysis_result = analyze_document(document_id, document_type)
        
        # Store results in S3
        result_key = f"analysis/{document_id}/{datetime.utcnow().isoformat()}.json"
        s3.put_object(
            Bucket=RESULTS_BUCKET,
            Key=result_key,
            Body=json.dumps(analysis_result),
            ContentType='application/json'
        )
        
        # Send metrics to CloudWatch
        send_metrics(document_type, analysis_result, source)
        
        # Return success response
        response_body = {
            'document_id': document_id,
            'analysis_id': analysis_result['analysis_id'],
            'status': 'completed',
            'result_location': f"s3://{RESULTS_BUCKET}/{result_key}",
            'metrics': {
                'generation_rate': analysis_result['metrics']['docs_per_hour'],
                'latency_p50': analysis_result['metrics']['latency_p50'],
                'latency_p95': analysis_result['metrics']['latency_p95'],
                'latency_p99': analysis_result['metrics']['latency_p99']
            }
        }
        
        logger.info(f"Analysis completed: {response_body}")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(response_body)
        }
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        
        # Send error metric
        cloudwatch.put_metric_data(
            Namespace=METRICS_NAMESPACE,
            MetricData=[
                {
                    'MetricName': 'AnalysisErrors',
                    'Value': 1,
                    'Unit': 'Count',
                    'Timestamp': datetime.utcnow()
                }
            ]
        )
        
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            })
        }


def analyze_document(document_id, document_type):
    """Analyze document and generate metrics"""
    start_time = datetime.utcnow()
    
    # Simulate document analysis (replace with actual analysis logic)
    import time
    import random
    
    time.sleep(random.uniform(0.05, 0.2))  # Simulate processing time
    
    # Generate analysis results
    analysis_id = f"AN-{document_id}-{int(datetime.utcnow().timestamp())}"
    
    result = {
        'analysis_id': analysis_id,
        'document_id': document_id,
        'document_type': document_type,
        'timestamp': start_time.isoformat(),
        'compliance_score': random.uniform(85, 99),
        'validation_passed': random.choice([True, True, True, False]),
        'metrics': {
            'docs_per_hour': random.randint(500, 2000),
            'docs_per_day': random.randint(10000, 45000),
            'latency_p50': random.uniform(0.1, 0.3),
            'latency_p95': random.uniform(0.4, 0.8),
            'latency_p99': random.uniform(0.9, 1.5)
        },
        'key_findings': [
            'Document structure compliant',
            'All required fields present',
            'Signatures valid'
        ]
    }
    
    return result


def send_metrics(document_type, analysis_result, source):
    """Send custom metrics to CloudWatch"""
    try:
        metrics_data = [
            {
                'MetricName': 'DocumentGenera<response clipped><NOTE>To save on context only part of this function call's response was sent to you. Use the read_page tool to see the full response. However, this might not be necessary.</NOTE>
