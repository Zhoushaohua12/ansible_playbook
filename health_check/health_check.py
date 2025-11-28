"""
Main health check application entry point.

Provides command-line interface for running health checks on Linux/AIX systems.
"""

import argparse
import sys
import os
import yaml
from datetime import datetime
from typing import Dict, Any, List, Optional

# Add the health_check module to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.config_manager import ConfigManager
from connection.ssh_connector import SSHConnector
from checker.linux_checker import LinuxChecker
from checker.aix_checker import AIXChecker
from report.report_generator import ReportGenerator
from logger.logger_config import configure_logging, get_logger
from exceptions import HealthCheckError, ConfigurationError, ConnectionError


class HealthCheckApp:
    """Main health check application."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize health check application.
        
        Args:
            config_path: Path to configuration file
        """
        self.config_manager = ConfigManager(config_path)
        self.logger = get_logger(__name__)
        
        # Configure logging
        logging_config = self.config_manager.get_logging_config()
        configure_logging(logging_config)
        
        # Initialize report generator
        report_config = self.config_manager.get_report_config()
        self.report_generator = ReportGenerator(report_config)
    
    def run_single_host_check(self, host_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run health check on a single host.
        
        Args:
            host_config: Host configuration
            
        Returns:
            Check results dictionary
        """
        host = host_config['host']
        username = host_config['username']
        os_type = host_config.get('os_type', 'linux')
        
        self.logger.info(f"Starting health check for host: {host}")
        
        try:
            # Validate host configuration
            self.config_manager.validate_host_config(host_config)
            
            # Get SSH configuration
            ssh_config = self.config_manager.get_ssh_config()
            
            # Establish SSH connection
            with SSHConnector(host_config, ssh_config) as connector:
                # Get checker configuration
                checker_config = self.config_manager.get_checks_config(os_type)
                
                # Create appropriate checker
                if os_type.lower() == 'linux':
                    checker = LinuxChecker(connector, checker_config)
                elif os_type.lower() == 'aix':
                    checker = AIXChecker(connector, checker_config)
                else:
                    raise ConfigurationError(f"Unsupported OS type: {os_type}")
                
                # Run health checks
                results = checker.run_all_checks()
                summary = checker.get_summary()
                
                # Generate reports
                report_files = self.report_generator.generate_report(
                    host=host,
                    os_type=os_type,
                    results=results,
                    summary=summary
                )
                
                self.logger.info(f"Health check completed for {host}. Overall status: {summary.get('overall_status')}")
                
                return {
                    'host': host,
                    'os_type': os_type,
                    'timestamp': datetime.now().isoformat(),
                    'summary': summary,
                    'results': [result.to_dict() for result in results],
                    'report_files': report_files
                }
                
        except Exception as e:
            self.logger.error(f"Health check failed for {host}: {e}")
            return {
                'host': host,
                'os_type': os_type,
                'timestamp': datetime.now().isoformat(),
                'error': str(e),
                'summary': {'total': 0, 'passed': 0, 'failed': 1, 'warning': 0, 'skipped': 0, 'overall_status': 'FAIL'},
                'results': [],
                'report_files': {}
            }
    
    def run_batch_check(self, hosts_file: str) -> List[Dict[str, Any]]:
        """
        Run health check on multiple hosts.
        
        Args:
            hosts_file: Path to hosts configuration file
            
        Returns:
            List of check results
        """
        try:
            with open(hosts_file, 'r', encoding='utf-8') as f:
                hosts_data = yaml.safe_load(f)
            
            hosts = hosts_data.get('hosts', [])
            if not hosts:
                raise ConfigurationError("No hosts found in configuration file")
            
            self.logger.info(f"Starting batch health check for {len(hosts)} hosts")
            
            results = []
            for host_config in hosts:
                result = self.run_single_host_check(host_config)
                results.append(result)
            
            # Generate batch report
            batch_report_file = self.report_generator.generate_batch_report(results)
            self.logger.info(f"Batch report generated: {batch_report_file}")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Batch health check failed: {e}")
            raise HealthCheckError(f"Batch health check failed: {e}")
    
    def run_scheduled_check(self, hosts_file: str, interval: int = 3600) -> None:
        """
        Run scheduled health checks.
        
        Args:
            hosts_file: Path to hosts configuration file
            interval: Check interval in seconds (default: 1 hour)
        """
        import time
        
        self.logger.info(f"Starting scheduled health checks with interval: {interval} seconds")
        
        try:
            while True:
                self.logger.info("Running scheduled health check...")
                self.run_batch_check(hosts_file)
                self.logger.info(f"Scheduled check completed. Next check in {interval} seconds...")
                time.sleep(interval)
                
        except KeyboardInterrupt:
            self.logger.info("Scheduled health checks stopped by user")
        except Exception as e:
            self.logger.error(f"Scheduled health check failed: {e}")
            raise


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Health Check System for Linux/AIX",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check single host
  python health_check.py --host 192.168.1.100 --username admin --password secret --os-type linux
  
  # Check multiple hosts from file
  python health_check.py --batch hosts.yaml
  
  # Run scheduled checks
  python health_check.py --scheduled hosts.yaml --interval 3600
        """
    )
    
    # Single host options
    parser.add_argument('--host', help='Host IP or hostname')
    parser.add_argument('--username', help='SSH username')
    parser.add_argument('--password', help='SSH password')
    parser.add_argument('--key-file', help='SSH private key file')
    parser.add_argument('--port', type=int, default=22, help='SSH port (default: 22)')
    parser.add_argument('--os-type', choices=['linux', 'aix'], default='linux', help='Operating system type')
    
    # Batch options
    parser.add_argument('--batch', help='YAML file with multiple host configurations')
    
    # Scheduled check options
    parser.add_argument('--scheduled', help='Run scheduled checks using hosts file')
    parser.add_argument('--interval', type=int, default=3600, help='Check interval in seconds for scheduled mode')
    
    # General options
    parser.add_argument('--config', help='Path to configuration file')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    parser.add_argument('--quiet', '-q', action='store_true', help='Suppress console output')
    
    args = parser.parse_args()
    
    # Validate arguments
    if not any([args.host, args.batch, args.scheduled]):
        parser.error("One of --host, --batch, or --scheduled must be specified")
    
    if args.host and not args.username:
        parser.error("--username is required when using --host")
    
    if args.verbose and args.quiet:
        parser.error("Cannot specify both --verbose and --quiet")
    
    try:
        # Initialize application
        app = HealthCheckApp(args.config)
        
        # Override logging level if specified
        if args.verbose:
            logging_config = app.config_manager.get_logging_config()
            logging_config['level'] = 'DEBUG'
            configure_logging(logging_config)
        elif args.quiet:
            logging_config = app.config_manager.get_logging_config()
            logging_config['console'] = False
            configure_logging(logging_config)
        
        # Run appropriate mode
        if args.scheduled:
            app.run_scheduled_check(args.scheduled, args.interval)
        elif args.batch:
            results = app.run_batch_check(args.batch)
            print(f"Batch check completed for {len(results)} hosts")
        else:
            # Single host mode
            host_config = {
                'host': args.host,
                'username': args.username,
                'password': args.password,
                'key_file': args.key_file,
                'port': args.port,
                'os_type': args.os_type
            }
            
            result = app.run_single_host_check(host_config)
            
            # Print summary
            summary = result['summary']
            print(f"Health check completed for {args.host}")
            print(f"Overall status: {summary.get('overall_status')}")
            print(f"Total checks: {summary.get('total')}")
            print(f"Passed: {summary.get('passed')}")
            print(f"Failed: {summary.get('failed')}")
            print(f"Warnings: {summary.get('warning')}")
            
            if result.get('report_files'):
                print("\nGenerated reports:")
                for format_type, file_path in result['report_files'].items():
                    print(f"  {format_type.upper()}: {file_path}")
    
    except KeyboardInterrupt:
        print("\nHealth check interrupted by user")
        sys.exit(1)
    except HealthCheckError as e:
        print(f"Health check error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()