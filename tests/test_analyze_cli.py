"""Tests for VCHASNO Analytics CLI"""
import pytest
import json
from unittest.mock import Mock, patch, mock_open
from analyze_cli import VCHASNOAnalyticsCLI
import sys


@pytest.fixture
def cli():
    """Create CLI instance for testing"""
    return VCHASNOAnalyticsCLI("https://test-api.vchasno.com")


class TestVCHASNOAnalyticsCLI:
    """Test suite for VCHASNO Analytics CLI"""
    
    def test_init(self, cli):
        """Test CLI initialization"""
        assert cli.endpoint_url == "https://test-api.vchasno.com"
    
    @patch('analyze_cli.requests.post')
    def test_analyze_document_success(self, mock_post, cli):
        """Test successful document analysis"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "status": "success",
            "document_id": "doc-123",
            "analysis_complete": True
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        result = cli.analyze_document("doc-123", "contract")
        
        assert result["status"] == "success"
        assert result["document_id"] == "doc-123"
        mock_post.assert_called_once()
    
    @patch('analyze_cli.requests.post')
    def test_analyze_document_failure(self, mock_post, cli):
        """Test document analysis failure"""
        mock_post.side_effect = Exception("API Error")
        
        result = cli.analyze_document("doc-456", "compliance")
        
        assert result is None
    
    @patch('analyze_cli.requests.post')
    def test_batch_analyze(self, mock_post, cli):
        """Test batch document analysis"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "status": "success",
            "document_id": "test"
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        doc_ids = ["doc-1", "doc-2", "doc-3"]
        results = cli.batch_analyze(doc_ids, "contract")
        
        assert len(results) == 3
        assert mock_post.call_count == 3
    
    @patch('analyze_cli.requests.get')
    def test_get_stats_success(self, mock_get, cli):
        """Test fetching analytics stats"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "total_documents": 1500,
            "analyzed_today": 42,
            "success_rate": 99.5
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        stats = cli.get_stats()
        
        assert stats["total_documents"] == 1500
        assert stats["success_rate"] == 99.5
    
    @patch('analyze_cli.requests.get')
    def test_get_stats_failure(self, mock_get, cli):
        """Test stats fetching failure"""
        mock_get.side_effect = Exception("Connection error")
        
        stats = cli.get_stats()
        
        assert stats is None


class TestCLIMain:
    """Test suite for CLI main function"""
    
    @patch('analyze_cli.VCHASNOAnalyticsCLI')
    @patch('sys.argv', ['prog', '--action', 'analyze', '--doc-id', 'doc-789', '--doc-type', 'contract'])
    def test_main_analyze_action(self, mock_cli_class):
        """Test main function with analyze action"""
        from analyze_cli import main
        
        mock_cli_instance = Mock()
        mock_cli_instance.analyze_document.return_value = {"status": "success"}
        mock_cli_class.return_value = mock_cli_instance
        
        main()
        
        mock_cli_instance.analyze_document.assert_called_once_with('doc-789', 'contract')
    
    @patch('analyze_cli.VCHASNOAnalyticsCLI')
    @patch('sys.argv', ['prog', '--action', 'stats'])
    def test_main_stats_action(self, mock_cli_class):
        """Test main function with stats action"""
        from analyze_cli import main
        
        mock_cli_instance = Mock()
        mock_cli_instance.get_stats.return_value = {"total": 100}
        mock_cli_class.return_value = mock_cli_instance
        
        main()
        
        mock_cli_instance.get_stats.assert_called_once()


# Integration tests
class TestIntegration:
    """Integration tests"""
    
    @patch('analyze_cli.requests.post')
    def test_end_to_end_workflow(self, mock_post):
        """Test complete analysis workflow"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "status": "success",
            "document_id": "doc-integration",
            "analysis_results": {
                "risk_score": 0.15,
                "compliance_check": "passed"
            }
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        cli = VCHASNOAnalyticsCLI("https://api.vchasno.com")
        result = cli.analyze_document("doc-integration", "contract")
        
        assert result["status"] == "success"
        assert "analysis_results" in result
        assert result["analysis_results"]["risk_score"] == 0.15
