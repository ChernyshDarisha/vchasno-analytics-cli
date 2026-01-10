# VCHASNO Analytics - Architecture Documentation

## Overview

VCHASNO Analytics is a serverless analytics platform built on AWS, designed for real-time document analysis with EventBridge-driven architecture and CloudWatch monitoring.

## Architecture Diagram

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Client    │────▶│  API Gateway │────▶│   Lambda    │
│(analyze CLI)│     │  REST API    │     │  Analyzer   │
└─────────────┘     └──────────────┘     └──────┬──────┘
                                                 │
                             ┌───────────────────┼───────────────────┐
                             │                   │                   │
                             ▼                   ▼                   ▼
                      ┌──────────┐        ┌──────────┐       ┌──────────┐
                      │ DynamoDB │        │    S3    │       │EventBridge│
                      │Documents │        │ Results  │       │  Events  │
                      └──────────┘        └──────────┘       └─────┬────┘
                                                                    │
                                                              ┌─────▼─────┐
                                                              │CloudWatch │
                                                              │  Metrics  │
                                                              └───────────┘
```

## Core Components

### 1. API Gateway
- **Endpoint**: `/analyze`
- **Method**: POST
- **Authentication**: API Key-based
- **Rate Limiting**: 1000 requests/minute
- **Purpose**: Entry point for document analysis requests

### 2. Lambda Functions

#### AnalyzerFunction
- **Runtime**: Python 3.11
- **Memory**: 512 MB
- **Timeout**: 60 seconds
- **Handler**: `lambda_handler.analyze_handler`
- **Environment Variables**:
  - `METRICS_NAMESPACE`: VCHASNO/Analytics
  - `RESULTS_BUCKET`: !Ref ResultsBucket
  - `DOCUMENTS_TABLE`: !Ref DocumentsTable

**Responsibilities**:
- Document validation and preprocessing
- Analysis execution
- Results storage
- Metric emission
- Event publishing

#### FunctionArn
- **Purpose**: Lambda function ARN export
- **Value**: GetAtt AnalyzerFunction.Arn

### 3. Data Storage

#### DynamoDB Table (DocumentsTable)
- **Table Name**: VCHASNO-Documents
- **Partition Key**: document_id (String)
- **Billing Mode**: PAY_PER_REQUEST
- **Point-in-Time Recovery**: Enabled
- **Stream**: NEW_AND_OLD_IMAGES

**Schema**:
```json
{
  "document_id": "string",
  "document_type": "string",
  "status": "string",
  "created_at": "timestamp",
  "analysis_results": "map",
  "metadata": "map"
}
```

#### S3 Bucket (ResultsBucket)
- **Purpose**: Store analysis results and artifacts
- **Versioning**: Enabled
- **Encryption**: AES-256 (SSE-S3)
- **Lifecycle Policy**: 
  - Move to IA after 30 days
  - Archive to Glacier after 90 days
  - Delete after 365 days

### 4. Event Processing

#### EventBridge Rule
- **Rule Name**: AnalysisCompletedRule
- **Event Pattern**:
```json
{
  "source": ["vchasno.analytics"],
  "detail-type": ["Analysis Completed"]
}
```
- **Targets**: CloudWatch Logs, SNS Topic (notifications)

### 5. Monitoring & Observability

#### CloudWatch Metrics
- **Namespace**: VCHASNO/Analytics
- **Key Metrics**:
  - `AnalysisLatency`: Processing time per document
  - `AnalysisSuccessRate`: Percentage of successful analyses
  - `DocumentsProcessed`: Total documents analyzed
  - `ErrorCount`: Number of failures

#### CloudWatch Alarms
1. **HighErrorRateAlarm**
   - Threshold: ErrorRate > 5%
   - Period: 5 minutes
   - Actions: SNS notification

2. **HighLatencyAlarm**
   - Threshold: AvgLatency > 30 seconds
   - Period: 5 minutes
   - Actions: SNS notification

## Data Flow

1. **Request Ingestion**
   - Client sends POST to `/analyze` endpoint
   - API Gateway validates API key
   - Request forwarded to Lambda

2. **Processing**
   - Lambda receives event
   - Validates document_id and document_type
   - Retrieves document from DynamoDB
   - Performs analysis
   - Stores results in S3
   - Updates DynamoDB status

3. **Event Publishing**
   - Lambda publishes event to EventBridge
   - Event contains: document_id, status, latency
   - CloudWatch captures metrics

4. **Monitoring**
   - CloudWatch tracks all metrics
   - Alarms trigger on threshold violations
   - SNS sends notifications

## Deployment

### Infrastructure as Code
- **Tool**: AWS SAM (Serverless Application Model)
- **Template**: `template.yaml`
- **Regions**: us-east-1 (primary)

### CI/CD Pipeline
- **Platform**: GitHub Actions
- **Workflow**: `.github/workflows/deploy.yml`

**Pipeline Stages**:
1. **Test**: Run unit tests with pytest
2. **Lint**: Code quality checks (black, flake8, pylint)
3. **Build**: Create Lambda deployment package
4. **Deploy-Dev**: Deploy to development (develop branch)
5. **Deploy-Prod**: Deploy to production (main branch)
6. **Notify**: Send Slack notification

### Deployment Commands
```bash
# Build
sam build

# Deploy to dev
sam deploy --config-env dev

# Deploy to prod
sam deploy --config-env prod
```

## Security

### IAM Roles
- **LambdaExecutionRole**: Minimal permissions for Lambda
  - DynamoDB: GetItem, PutItem, UpdateItem
  - S3: PutObject, GetObject
  - EventBridge: PutEvents
  - CloudWatch: PutMetricData, CreateLogStream

### API Security
- API Key authentication
- HTTPS only
- CORS enabled for specific origins
- Request throttling

### Data Security
- Encryption at rest (S3, DynamoDB)
- Encryption in transit (TLS 1.2+)
- Secrets in AWS Secrets Manager
- No sensitive data in logs

## Performance

### Targets
- **Latency**: < 1 second (p99)
- **Throughput**: 1000 req/min
- **Availability**: 99.99% uptime
- **Error Rate**: < 0.1%

### Optimization
- Lambda provisioned concurrency for cold start mitigation
- DynamoDB on-demand scaling
- S3 Transfer Acceleration
- CloudFront CDN for static assets

## Cost Optimization
- Serverless architecture (pay-per-use)
- S3 lifecycle policies
- DynamoDB on-demand billing
- Reserved CloudWatch log retention (30 days)
- Lambda memory optimization

## Disaster Recovery

### Backup Strategy
- DynamoDB PITR enabled
- S3 versioning enabled
- Cross-region replication (planned)

### Recovery Objectives
- **RTO**: < 1 hour
- **RPO**: < 5 minutes

## Future Enhancements

1. **Multi-region deployment** for global availability
2. **GraphQL API** for flexible querying
3. **ML model integration** via SageMaker
4. **Real-time streaming** with Kinesis
5. **Advanced analytics** dashboard
6. **Blockchain integration** for audit trails

## References

- [AWS Lambda Best Practices](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)
- [DynamoDB Design Patterns](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/best-practices.html)
- [EventBridge Patterns](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-event-patterns.html)

## Support

For issues or questions:
- **GitHub Issues**: https://github.com/ChernyshDarisha/vchasno-analytics-cli/issues
- **Email**: support@vchasno.com
- **Slack**: #vchasno-analytics
