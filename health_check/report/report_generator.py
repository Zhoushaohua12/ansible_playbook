"""
Report generator for health check system.

Supports multiple output formats: JSON, HTML, and plain text.
Generates comprehensive health check reports with statistics and details.
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
from ..checker.base_checker import CheckResult
from ..logger.logger_config import get_logger
from ..exceptions import ReportGenerationError


class ReportGenerator:
    """Generates health check reports in various formats."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize report generator.
        
        Args:
            config: Report configuration
        """
        self.config = config or {}
        self.logger = get_logger(self.__class__.__name__)
        self.output_dir = Path(self.config.get('output_dir', 'reports')).resolve()
        self.formats = self.config.get('formats', ['json'])
        self.include_raw_output = self.config.get('include_raw_output', False)
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_report(self, host: str, os_type: str, results: List[CheckResult],
                       summary: Dict[str, Any], timestamp: Optional[datetime] = None) -> Dict[str, str]:
        """
        Generate health check report in configured formats.
        
        Args:
            host: Host name or IP
            os_type: Operating system type
            results: List of check results
            summary: Check summary statistics
            timestamp: Report timestamp
            
        Returns:
            Dictionary mapping format to file path
        """
        if not timestamp:
            timestamp = datetime.now()
        
        report_data = {
            'host': host,
            'os_type': os_type,
            'timestamp': timestamp.isoformat(),
            'summary': summary,
            'results': [result.to_dict() for result in results]
        }
        
        # Remove raw output if not configured to include it
        if not self.include_raw_output:
            for result in report_data['results']:
                result.pop('raw_output', None)
        
        generated_files = {}
        
        for format_type in self.formats:
            try:
                if format_type.lower() == 'json':
                    file_path = self._generate_json_report(report_data, host, timestamp)
                elif format_type.lower() == 'html':
                    file_path = self._generate_html_report(report_data, host, timestamp)
                elif format_type.lower() == 'text':
                    file_path = self._generate_text_report(report_data, host, timestamp)
                else:
                    self.logger.warning(f"Unsupported report format: {format_type}")
                    continue
                
                generated_files[format_type] = str(file_path)
                self.logger.info(f"Generated {format_type.upper()} report: {file_path}")
                
            except Exception as e:
                self.logger.error(f"Failed to generate {format_type} report: {e}")
                raise ReportGenerationError(f"Failed to generate {format_type} report: {e}")
        
        return generated_files
    
    def _generate_json_report(self, report_data: Dict[str, Any], host: str, timestamp: datetime) -> Path:
        """Generate JSON format report."""
        filename = f"{host}_{timestamp.strftime('%Y%m%d_%H%M%S')}_health_check.json"
        file_path = self.output_dir / filename
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            
            return file_path
            
        except Exception as e:
            raise ReportGenerationError(f"Failed to write JSON report: {e}")
    
    def _generate_html_report(self, report_data: Dict[str, Any], host: str, timestamp: datetime) -> Path:
        """Generate HTML format report."""
        filename = f"{host}_{timestamp.strftime('%Y%m%d_%H%M%S')}_health_check.html"
        file_path = self.output_dir / filename
        
        html_content = self._create_html_content(report_data)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return file_path
            
        except Exception as e:
            raise ReportGenerationError(f"Failed to write HTML report: {e}")
    
    def _generate_text_report(self, report_data: Dict[str, Any], host: str, timestamp: datetime) -> Path:
        """Generate plain text format report."""
        filename = f"{host}_{timestamp.strftime('%Y%m%d_%H%M%S')}_health_check.txt"
        file_path = self.output_dir / filename
        
        text_content = self._create_text_content(report_data)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(text_content)
            
            return file_path
            
        except Exception as e:
            raise ReportGenerationError(f"Failed to write text report: {e}")
    
    def _create_html_content(self, report_data: Dict[str, Any]) -> str:
        """Create HTML content for report."""
        host = report_data['host']
        os_type = report_data['os_type']
        timestamp = report_data['timestamp']
        summary = report_data['summary']
        results = report_data['results']
        
        # Determine overall status
        overall_status = summary.get('overall_status', 'UNKNOWN')
        status_color = {
            'PASS': '#28a745',
            'FAIL': '#dc3545',
            'WARN': '#ffc107',
            'UNKNOWN': '#6c757d'
        }.get(overall_status, '#6c757d')
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Health Check Report - {host}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #eee;
        }}
        .status-badge {{
            display: inline-block;
            padding: 10px 20px;
            border-radius: 5px;
            color: white;
            font-weight: bold;
            font-size: 18px;
            background-color: {status_color};
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }}
        .summary-item {{
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            text-align: center;
        }}
        .summary-item h3 {{
            margin: 0 0 10px 0;
            color: #495057;
        }}
        .summary-item .value {{
            font-size: 24px;
            font-weight: bold;
            color: #007bff;
        }}
        .results {{
            margin-top: 30px;
        }}
        .result-item {{
            margin-bottom: 20px;
            border: 1px solid #ddd;
            border-radius: 5px;
            overflow: hidden;
        }}
        .result-header {{
            padding: 15px;
            font-weight: bold;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .status-pass {{ background-color: #d4edda; color: #155724; }}
        .status-fail {{ background-color: #f8d7da; color: #721c24; }}
        .status-warn {{ background-color: #fff3cd; color: #856404; }}
        .status-skip {{ background-color: #e2e3e5; color: #383d41; }}
        .result-details {{
            padding: 15px;
            background-color: #f8f9fa;
        }}
        .raw-output {{
            margin-top: 10px;
            padding: 10px;
            background-color: #f1f3f4;
            border-radius: 3px;
            font-family: monospace;
            font-size: 12px;
            white-space: pre-wrap;
            max-height: 200px;
            overflow-y: auto;
        }}
        .footer {{
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            text-align: center;
            color: #6c757d;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Health Check Report</h1>
            <p><strong>Host:</strong> {host} | <strong>OS:</strong> {os_type} | <strong>Time:</strong> {timestamp}</p>
            <div class="status-badge">Overall Status: {overall_status}</div>
        </div>
        
        <div class="summary">
            <div class="summary-item">
                <h3>Total Checks</h3>
                <div class="value">{summary.get('total', 0)}</div>
            </div>
            <div class="summary-item">
                <h3>Passed</h3>
                <div class="value">{summary.get('passed', 0)}</div>
            </div>
            <div class="summary-item">
                <h3>Failed</h3>
                <div class="value">{summary.get('failed', 0)}</div>
            </div>
            <div class="summary-item">
                <h3>Warnings</h3>
                <div class="value">{summary.get('warning', 0)}</div>
            </div>
            <div class="summary-item">
                <h3>Skipped</h3>
                <div class="value">{summary.get('skipped', 0)}</div>
            </div>
        </div>
        
        <div class="results">
            <h2>Check Results</h2>
        """
        
        # Add individual check results
        for result in results:
            status_class = f"status-{result['status'].lower()}"
            
            html += f"""
            <div class="result-item">
                <div class="result-header {status_class}">
                    <span>{result['name']}</span>
                    <span>{result['status']}</span>
                </div>
                <div class="result-details">
                    <p><strong>Message:</strong> {result['message']}</p>
                    <p><strong>Timestamp:</strong> {result['timestamp']}</p>
            """
            
            # Add details if available
            if result.get('details'):
                html += "<h4>Details:</h4><ul>"
                for key, value in result['details'].items():
                    html += f"<li><strong>{key}:</strong> {value}</li>"
                html += "</ul>"
            
            # Add raw output if available
            if result.get('raw_output'):
                html += f'<div class="raw-output">{result["raw_output"]}</div>'
            
            html += "</div></div>"
        
        html += """
        </div>
        
        <div class="footer">
            <p>Generated by Health Check System</p>
        </div>
    </div>
</body>
</html>
        """
        
        return html
    
    def _create_text_content(self, report_data: Dict[str, Any]) -> str:
        """Create plain text content for report."""
        host = report_data['host']
        os_type = report_data['os_type']
        timestamp = report_data['timestamp']
        summary = report_data['summary']
        results = report_data['results']
        
        text = f"""
HEALTH CHECK REPORT
===================

Host: {host}
OS Type: {os_type}
Timestamp: {timestamp}
Overall Status: {summary.get('overall_status', 'UNKNOWN')}

SUMMARY
-------
Total Checks: {summary.get('total', 0)}
Passed: {summary.get('passed', 0)}
Failed: {summary.get('failed', 0)}
Warnings: {summary.get('warning', 0)}
Skipped: {summary.get('skipped', 0)}

CHECK RESULTS
-------------
"""
        
        # Add individual check results
        for result in results:
            text += f"""
{result['name'].upper()}
{'-' * len(result['name'])}
Status: {result['status']}
Message: {result['message']}
Timestamp: {result['timestamp']}
"""
            
            # Add details if available
            if result.get('details'):
                text += "Details:\n"
                for key, value in result['details'].items():
                    text += f"  {key}: {value}\n"
                text += "\n"
            
            # Add raw output if available
            if result.get('raw_output'):
                text += f"Raw Output:\n{result['raw_output']}\n\n"
            
            text += "\n"
        
        text += """
Generated by Health Check System
        """
        
        return text.strip()
    
    def generate_batch_report(self, reports: List[Dict[str, Any]]) -> str:
        """
        Generate a batch report for multiple hosts.
        
        Args:
            reports: List of report data dictionaries
            
        Returns:
            Path to generated batch report file
        """
        timestamp = datetime.now()
        filename = f"batch_report_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        file_path = self.output_dir / filename
        
        batch_data = {
            'timestamp': timestamp.isoformat(),
            'total_hosts': len(reports),
            'reports': reports
        }
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(batch_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Generated batch report: {file_path}")
            return str(file_path)
            
        except Exception as e:
            raise ReportGenerationError(f"Failed to write batch report: {e}")