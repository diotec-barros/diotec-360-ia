#!/usr/bin/env python3
"""
Copyright 2024 Dionísio Sebastião Barros / DIOTEC 360

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

"""
MOE Intelligence Layer Rollback Script

Automated rollback of MOE v2.1.0 to v1.9.0 behavior.
Disables MOE and falls back to existing layers.

Usage:
    python scripts/rollback_moe.py
    python scripts/rollback_moe.py --reason "High false positive rate"
    python scripts/rollback_moe.py --skip-backup
"""

import os
import sys
import argparse
import shutil
import subprocess
from pathlib import Path
from datetime import datetime


class MOERollback:
    """Automated MOE rollback orchestrator."""
    
    def __init__(self, reason: str = "Manual rollback", skip_backup: bool = False):
        self.reason = reason
        self.skip_backup = skip_backup
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.backup_dir = Path(f'./backups/moe_{self.timestamp}')
    
    def log(self, message: str, level: str = "INFO"):
        """Log message with timestamp."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        prefix = {
            "INFO": "ℹ️",
            "SUCCESS": "✅",
            "WARNING": "⚠️",
            "ERROR": "❌",
            "PROGRESS": "🔄"
        }.get(level, "ℹ️")
        
        print(f"[{timestamp}] {prefix} {message}")
    
    def disable_moe(self) -> bool:
        """Disable MOE via environment variable."""
        self.log("Disabling MOE Intelligence Layer...", "PROGRESS")
        
        try:
            # Update .env file
            env_file = Path('.env')
            
            if env_file.exists():
                with open(env_file, 'r') as f:
                    lines = f.readlines()
                
                # Update or add MOE_ENABLED flag
                moe_enabled_found = False
                with open(env_file, 'w') as f:
                    for line in lines:
                        if line.startswith('DIOTEC360_MOE_ENABLED'):
                            f.write('DIOTEC360_MOE_ENABLED=false\n')
                            moe_enabled_found = True
                        else:
                            f.write(line)
                    
                    if not moe_enabled_found:
                        f.write('\nDIOTEC360_MOE_ENABLED=false\n')
            else:
                with open(env_file, 'w') as f:
                    f.write('DIOTEC360_MOE_ENABLED=false\n')
            
            self.log("MOE disabled in configuration", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"Failed to disable MOE: {e}", "ERROR")
            return False
    
    def restart_application(self) -> bool:
        """Restart application to apply changes."""
        self.log("Restarting application...", "PROGRESS")
        
        try:
            # Try systemctl first
            result = subprocess.run(
                ['systemctl', 'restart', 'diotec360-judge'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.log("Application restarted via systemctl", "SUCCESS")
                return True
            
            # Try docker-compose
            result = subprocess.run(
                ['docker-compose', 'restart'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.log("Application restarted via docker-compose", "SUCCESS")
                return True
            
            # Manual restart required
            self.log("Automatic restart failed. Please restart manually.", "WARNING")
            return False
            
        except Exception as e:
            self.log(f"Failed to restart application: {e}", "WARNING")
            self.log("Please restart manually: systemctl restart diotec360-judge", "INFO")
            return False
    
    def backup_databases(self) -> bool:
        """Backup MOE databases."""
        if self.skip_backup:
            self.log("Skipping database backup (--skip-backup)", "INFO")
            return True
        
        self.log("Backing up MOE databases...", "PROGRESS")
        
        try:
            # Create backup directory
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Backup telemetry database
            telemetry_db = Path('./.diotec360_moe/telemetry.db')
            if telemetry_db.exists():
                shutil.copy2(telemetry_db, self.backup_dir / 'telemetry.db')
                self.log(f"Backed up telemetry database", "SUCCESS")
            else:
                self.log("Telemetry database not found", "WARNING")
            
            # Backup training database
            training_db = Path('./.diotec360_moe/training.db')
            if training_db.exists():
                shutil.copy2(training_db, self.backup_dir / 'training.db')
                self.log(f"Backed up training database", "SUCCESS")
            else:
                self.log("Training database not found", "WARNING")
            
            # Backup configuration files
            config_dir = Path('./config')
            if config_dir.exists():
                for config_file in config_dir.glob('moe_*.env'):
                    shutil.copy2(config_file, self.backup_dir / config_file.name)
                    self.log(f"Backed up {config_file.name}", "SUCCESS")
            
            self.log(f"Backups saved to: {self.backup_dir}", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"Failed to backup databases: {e}", "ERROR")
            return False
    
    def export_reports(self) -> bool:
        """Export MOE reports for analysis."""
        self.log("Exporting MOE reports...", "PROGRESS")
        
        try:
            reports_dir = Path('./reports')
            reports_dir.mkdir(parents=True, exist_ok=True)
            
            # Export expert performance report
            report_file = reports_dir / f'moe_rollback_analysis_{self.timestamp}.txt'
            
            with open(report_file, 'w') as f:
                f.write("=" * 80 + "\n")
                f.write("MOE INTELLIGENCE LAYER ROLLBACK REPORT\n")
                f.write("=" * 80 + "\n\n")
                f.write(f"Timestamp: {datetime.now().isoformat()}\n")
                f.write(f"Reason: {self.reason}\n")
                f.write(f"Backup Location: {self.backup_dir}\n\n")
                f.write("=" * 80 + "\n")
                f.write("ROLLBACK ACTIONS TAKEN\n")
                f.write("=" * 80 + "\n\n")
                f.write("1. MOE disabled via DIOTEC360_MOE_ENABLED=false\n")
                f.write("2. Application restarted\n")
                f.write("3. Databases backed up\n")
                f.write("4. Reports exported\n\n")
                f.write("=" * 80 + "\n")
                f.write("NEXT STEPS\n")
                f.write("=" * 80 + "\n\n")
                f.write("1. Monitor system for 10 minutes: python scripts/monitor_system.py\n")
                f.write("2. Run rollback tests: python scripts/test_moe_rollback.py\n")
                f.write("3. Compare with v1.9.0 baseline: python scripts/compare_baseline.py\n")
                f.write("4. Analyze root cause: Review telemetry and expert performance\n")
                f.write("5. Plan re-deployment: Fix issues and test in staging\n\n")
            
            self.log(f"Report saved to: {report_file}", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"Failed to export reports: {e}", "ERROR")
            return False
    
    def verify_rollback(self) -> bool:
        """Verify rollback was successful."""
        self.log("Verifying rollback...", "PROGRESS")
        
        try:
            # Check if MOE is disabled in .env
            env_file = Path('.env')
            if env_file.exists():
                with open(env_file, 'r') as f:
                    content = f.read()
                    if 'DIOTEC360_MOE_ENABLED=false' in content:
                        self.log("MOE disabled in configuration ✓", "SUCCESS")
                    else:
                        self.log("MOE not disabled in configuration", "ERROR")
                        return False
            
            # Check if backups exist
            if not self.skip_backup:
                if self.backup_dir.exists():
                    self.log("Backups created ✓", "SUCCESS")
                else:
                    self.log("Backups not found", "WARNING")
            
            self.log("Rollback verification complete", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"Failed to verify rollback: {e}", "ERROR")
            return False
    
    def execute(self) -> bool:
        """Execute complete rollback procedure."""
        self.log("=" * 80, "INFO")
        self.log("MOE INTELLIGENCE LAYER ROLLBACK", "INFO")
        self.log("=" * 80, "INFO")
        self.log(f"Reason: {self.reason}", "INFO")
        self.log("", "INFO")
        
        # Phase 1: Disable MOE
        self.log("Phase 1: Disabling MOE", "INFO")
        if not self.disable_moe():
            self.log("Rollback failed at Phase 1", "ERROR")
            return False
        
        # Phase 2: Restart application
        self.log("", "INFO")
        self.log("Phase 2: Restarting application", "INFO")
        self.restart_application()  # Non-critical, continue even if fails
        
        # Phase 3: Backup databases
        self.log("", "INFO")
        self.log("Phase 3: Backing up databases", "INFO")
        if not self.backup_databases():
            self.log("Backup failed, but continuing rollback", "WARNING")
        
        # Phase 4: Export reports
        self.log("", "INFO")
        self.log("Phase 4: Exporting reports", "INFO")
        if not self.export_reports():
            self.log("Report export failed, but continuing rollback", "WARNING")
        
        # Phase 5: Verify rollback
        self.log("", "INFO")
        self.log("Phase 5: Verifying rollback", "INFO")
        if not self.verify_rollback():
            self.log("Rollback verification failed", "ERROR")
            return False
        
        # Success
        self.log("", "INFO")
        self.log("=" * 80, "INFO")
        self.log("ROLLBACK COMPLETE", "SUCCESS")
        self.log("=" * 80, "INFO")
        self.log("", "INFO")
        self.log("Next Steps:", "INFO")
        self.log("1. Monitor system: python scripts/monitor_system.py --duration 600", "INFO")
        self.log("2. Run tests: python scripts/test_moe_rollback.py", "INFO")
        self.log("3. Compare baseline: python scripts/compare_baseline.py", "INFO")
        self.log("4. Analyze root cause: Review reports in ./reports/", "INFO")
        self.log("", "INFO")
        
        return True


def main():
    parser = argparse.ArgumentParser(
        description="Rollback MOE Intelligence Layer to v1.9.0 behavior"
    )
    parser.add_argument(
        '--reason',
        default='Manual rollback',
        help='Reason for rollback (for logging)'
    )
    parser.add_argument(
        '--skip-backup',
        action='store_true',
        help='Skip database backup (faster rollback)'
    )
    parser.add_argument(
        '--yes',
        action='store_true',
        help='Skip confirmation prompt'
    )
    
    args = parser.parse_args()
    
    # Confirmation prompt
    if not args.yes:
        print("\n⚠️  WARNING: This will disable MOE and rollback to v1.9.0 behavior")
        print(f"Reason: {args.reason}")
        response = input("\nContinue with rollback? (yes/no): ")
        if response.lower() != 'yes':
            print("Rollback cancelled.")
            sys.exit(0)
    
    # Execute rollback
    rollback = MOERollback(reason=args.reason, skip_backup=args.skip_backup)
    success = rollback.execute()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
