"""
Tests for ReportGenerator class.
"""

import pytest
import tempfile
import json
import os
from unittest.mock import Mock, patch
from datetime import datetime
from health_check.report.report_generator import ReportGenerator
from health_check.checker.base_checker import CheckResult
from health_check.exceptions import ReportGenerationError


class TestReportGenerator:
    """Test cases for ReportGenerator."""
    
    def test_init_default_config(self):
        """Test ReportGenerator initialization with default config."""
        generator = ReportGenerator()
        
        assert generator.output_dir.name == 'reports'
        assert generator.formats == ['json']
        assert generator.include_raw_output is False
    
    def test_init_custom_config(self):
        """Test ReportGenerator initialization with custom config."""
        config = {
            'output_dir': './custom_reports',
            'formats': ['json', 'html'],
            'include_raw_output': True
        }
        
        generator = ReportGenerator(config)
        
        assert generator.output_dir.name == 'custom_reports'
        assert generator.formats == ['json', 'html']
        assert generator.include_raw_output is True
    
    def test_generate_report_json(self, sample_check_results):
        """Test JSON report generation."""
        config = {'formats': ['json'], 'include_raw_output': True}
        generator = ReportGenerator(config)
        
        host = 'test-host'
        os_type = 'linux'
        summary = {'total': 2, 'passed': 1, 'failed': 1, 'warning': 0, 'skipped': 0, 'overall_status': 'FAIL'}
        timestamp = datetime(2023, 1, 1, 12, 0, 0)
        
        report_files = generator.generate_report(host, os_type, sample_check_results, summary, timestamp)
        
        assert 'json' in report_files
        assert os.path.exists(report_files['json'])
        
        # Verify JSON content
        with open(report_files['json'], 'r') as f:
            data = json.load(f)
        
        assert data['host'] == host
        assert data['os_type'] == os_type
        assert data['timestamp'] == timestamp.isoformat()
        assert data['summary'] == summary
        assert len(data['results']) == 2
        assert data['results'][0]['name'] == 'disk_usage'
    
    def test_generate_report_html(self, sample_check_results):
        """Test HTML report generation."""
        config = {'formats': ['html'], 'include_raw_output': False}
        generator = ReportGenerator(config)
        
        host = 'test-host'
        os_type = 'linux'
        summary = {'total': 2, 'passed': 1, 'failed': 1, 'warning': 0, 'skipped': 0, 'overall_status': 'FAIL'}
        
        report_files = generator.generate_report(host, os_type, sample_check_results, summary)
        
        assert 'html' in report_files
        assert os.path.exists(report_files['html'])
        
        # Verify HTML content
        with open(report_files['html'], 'r') as f:
            html_content = f.read()
        
        assert host in html_content
        assert os_type in html_content
        assert 'disk_usage' in html_content
        assert 'memory' in html_content
        assert '<!DOCTYPE html>' in html_content
    
    def test_generate_report_text(self, sample_check_results):
        """Test text report generation."""
        config = {'formats': ['text'], 'include_raw_output': False}
        generator = ReportGenerator(config)
        
        host = 'test-host'
        os_type = 'linux'
        summary = {'total': 2, 'passed': 1, 'failed': 1, 'warning': 0, 'skipped': 0, 'overall_status': 'FAIL'}
        
        report_files = generator.generate_report(host, os_type, sample_check_results, summary)
        
        assert 'text' in report_files
        assert os.path.exists(report_files['text'])
        
        # Verify text content
        with open(report_files['text'], 'r') as f:
            text_content = f.read()
        
        assert host in text_content
        assert os_type in text_content
        assert 'disk_usage' in text_content
        assert 'memory' in text_content
        assert 'HEALTH CHECK REPORT' in text_content
    
    def test_generate_report_exclude_raw_output(self, sample_check_results):
        """Test report generation with raw output excluded."""
        config = {'formats': ['json'], 'include_raw_output': False}
        generator = ReportGenerator(config)
        
        host = 'test-host'
        os_type = 'linux'
        summary = {'total': 2, 'passed': 1, 'failed': 1, 'warning': 0, 'skipped': 0, 'overall_status': 'FAIL'}
        
        report_files = generator.generate_report(host, os_type, sample_check_results, summary)
        
        # Verify raw output is excluded
        with open(report_files['json'], 'r') as f:
            data = json.load(f)
        
        assert 'raw_output' not in data['results'][0]
        assert 'raw_output' not in data['results'][1]
    
    def test_generate_report_unsupported_format(self, sample_check_results):
        """Test report generation with unsupported format."""
        config = {'formats': ['unsupported']}
        generator = ReportGenerator(config)
        
        host = 'test-host'
        os_type = 'linux'
        summary = {'total': 2, 'passed': 1, 'failed': 1, 'warning': 0, 'skipped': 0, 'overall_status': 'FAIL'}
        
        report_files = generator.generate_report(host, os_type, sample_check_results, summary)
        
        assert len(report_files) == 0  # No files generated for unsupported format
    
    def test_generate_batch_report(self, sample_check_results):
        """Test batch report generation."""
        generator = ReportGenerator({'formats': ['json']})
        
        reports = [
            {
                'host': 'host1',
                'os_type': 'linux',
                'summary': {'total': 2, 'passed': 2, 'failed': 0, 'warning': 0, 'skipped': 0, 'overall_status': 'PASS'},
                'results': [r.to_dict() for r in sample_check_results]
            },
            {
                'host': 'host2',
                'os_type': 'aix',
                'summary': {'total': 2, 'passed': 1, 'failed': 1, 'warning': 0, 'skipped': 0, 'overall_status': 'FAIL'},
                'results': [r.to_dict() for r in sample_check_results]
            }
        ]
        
        batch_file = generator.generate_batch_report(reports)
        
        assert os.path.exists(batch_file)
        
        # Verify batch report content
        with open(batch_file, 'r') as f:
            data = json.load(f)
        
        assert data['total_hosts'] == 2
        assert len(data['reports']) == 2
        assert data['reports'][0]['host'] == 'host1'
        assert data['reports'][1]['host'] == 'host2'
    
    def test_create_html_content(self, sample_check_results):
        """Test HTML content creation."""
        generator = ReportGenerator()
        
        report_data = {
            'host': 'test-host',
            'os_type': 'linux',
            'timestamp': '2023-01-01T12:00:00',
            'summary': {'total': 2, 'passed': 1, 'failed': 1, 'warning': 0, 'skipped': 0, 'overall_status': 'FAIL'},
            'results': [r.to_dict() for r in sample_check_results]
        }
        
        html_content = generator._create_html_content(report_data)
        
        assert 'test-host' in html_content
        assert 'linux' in html_content
        assert 'disk_usage' in html_content
        assert 'memory' in html_content
        assert 'FAIL' in html_content
        assert '<!DOCTYPE html>' in html_content
        assert 'status-fail' in html_content
        assert 'status-pass' in html_content
    
    def test_create_text_content(self, sample_check_results):
        """Test text content creation."""
        generator = ReportGenerator()
        
        report_data = {
            'host': 'test-host',
            'os_type': 'linux',
            'timestamp': '2023-01-01T12:00:00',
            'summary': {'total': 2, 'passed': 1, 'failed': 1, 'warning': 0, 'skipped': 0, 'overall_status': 'FAIL'},
            'results': [r.to_dict() for r in sample_check_results]
        }
        
        text_content = generator._create_text_content(report_data)
        
        assert 'test-host' in text_content
        assert 'linux' in text_content
        assert 'HEALTH CHECK REPORT' in text_content
        assert 'disk_usage' in text_content
        assert 'memory' in text_content
        assert 'FAIL' in text_content
    
    def test_generate_report_write_failure(self, sample_check_results):
        """Test report generation when file write fails."""
        config = {'formats': ['json']}
        generator = ReportGenerator(config)
        
        host = 'test-host'
        os_type = 'linux'
        summary = {'total': 2, 'passed': 1, 'failed': 1, 'warning': 0, 'skipped': 0, 'overall_status': 'FAIL'}
        
        # Mock open to raise exception
        with patch('builtins.open', side_effect=IOError("Permission denied")):
            with pytest.raises(ReportGenerationError, match="Failed to write JSON report"):
                generator.generate_report(host, os_type, sample_check_results, summary)


@pytest.fixture
def sample_check_results():
    """Create sample check results for testing."""
    timestamp = datetime(2023, 1, 1, 12, 0, 0)
    
    result1 = CheckResult(
        name='disk_usage',
        status='PASS',
        message='Disk usage is normal',
        details={'usage': '25%'},
        raw_output='Filesystem usage output',
        timestamp=timestamp
    )
    
    result2 = CheckResult(
        name='memory',
        status='FAIL',
        message='Memory usage is high',
        details={'usage': '95%'},
        raw_output='Memory usage output',
        timestamp=timestamp
    )
    
    return [result1, result2]