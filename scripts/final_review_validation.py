#!/usr/bin/env python3
"""
Final Review Validation Script for Open Source Preparation
Validates all documentation, links, badges, and strategic messaging
"""

import os
import re
import json
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Result of a validation check"""
    category: str
    check: str
    passed: bool
    message: str
    severity: str = "error"  # error, warning, info


class FinalReviewValidator:
    """Comprehensive validator for final review"""
    
    def __init__(self, repo_root: Path = None):
        self.repo_root = repo_root or Path.cwd()
        self.results: List[ValidationResult] = []
        
    def add_result(self, category: str, check: str, passed: bool, 
                   message: str, severity: str = "error"):
        """Add a validation result"""
        self.results.append(ValidationResult(
            category=category,
            check=check,
            passed=passed,
            message=message,
            severity=severity
        ))
    
    def validate_all(self) -> Dict:
        """Run all validation checks"""
        print("🔍 Starting Final Review Validation...\n")
        
        self.validate_documentation_consistency()
        self.validate_links()
        self.validate_badges()
        self.validate_strategic_messaging()
        self.validate_community_readiness()
        
        return self.generate_report()
    
    def validate_documentation_consistency(self):
        """Validate documentation for consistency and quality"""
        print("📚 Validating documentation consistency...")
        
        # Check core documentation files exist
        core_docs = [
            "README.md", "LICENSE", "CONTRIBUTING.md", 
            "CODE_OF_CONDUCT.md", "SECURITY.md", "GOVERNANCE.md",
            "TRADEMARK.md", "CHANGELOG.md", "ROADMAP.md", "MIGRATION.md"
        ]
        
        for doc in core_docs:
            path = self.repo_root / doc
            if path.exists():
                self.add_result(
                    "Documentation", f"{doc} exists", True,
                    f"✓ {doc} found", "info"
                )
                # Check file is not empty
                if path.stat().st_size == 0:
                    self.add_result(
                        "Documentation", f"{doc} content", False,
                        f"✗ {doc} is empty", "error"
                    )
            else:
                self.add_result(
                    "Documentation", f"{doc} exists", False,
                    f"✗ {doc} not found", "error"
                )
        
        # Check docs/ directory structure
        docs_dirs = [
            "docs/getting-started",
            "docs/language-reference",
            "docs/api-reference",
            "docs/examples",
            "docs/advanced",
            "docs/commercial",
            "docs/architecture"
        ]
        
        for dir_path in docs_dirs:
            full_path = self.repo_root / dir_path
            if full_path.exists() and full_path.is_dir():
                # Check if directory has content
                files = list(full_path.glob("*.md"))
                if files:
                    self.add_result(
                        "Documentation", f"{dir_path} structure", True,
                        f"✓ {dir_path} has {len(files)} files", "info"
                    )
                else:
                    self.add_result(
                        "Documentation", f"{dir_path} content", False,
                        f"✗ {dir_path} is empty", "warning"
                    )
            else:
                self.add_result(
                    "Documentation", f"{dir_path} exists", False,
                    f"✗ {dir_path} not found", "error"
                )
    
    def validate_links(self):
        """Validate all internal links in markdown files"""
        print("🔗 Validating internal links...")
        
        md_files = list(self.repo_root.glob("*.md"))
        md_files.extend(self.repo_root.glob("docs/**/*.md"))
        
        link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
        broken_links = []
        
        for md_file in md_files:
            try:
                content = md_file.read_text(encoding='utf-8')
                links = link_pattern.findall(content)
                
                for link_text, link_url in links:
                    # Skip external links
                    if link_url.startswith(('http://', 'https://', 'mailto:', '#')):
                        continue
                    
                    # Resolve relative path
                    link_path = (md_file.parent / link_url).resolve()
                    
                    if not link_path.exists():
                        broken_links.append({
                            'file': str(md_file.relative_to(self.repo_root)),
                            'link': link_url,
                            'text': link_text
                        })
            except Exception as e:
                self.add_result(
                    "Links", f"Read {md_file.name}", False,
                    f"✗ Error reading {md_file.name}: {e}", "warning"
                )
        
        if broken_links:
            for broken in broken_links[:10]:  # Show first 10
                self.add_result(
                    "Links", "Internal link validation", False,
                    f"✗ Broken link in {broken['file']}: {broken['link']}", "error"
                )
            if len(broken_links) > 10:
                self.add_result(
                    "Links", "Additional broken links", False,
                    f"✗ {len(broken_links) - 10} more broken links found", "error"
                )
        else:
            self.add_result(
                "Links", "Internal link validation", True,
                f"✓ All internal links valid (checked {len(md_files)} files)", "info"
            )
    
    def validate_badges(self):
        """Validate README badges"""
        print("🏅 Validating README badges...")
        
        readme_path = self.repo_root / "README.md"
        if not readme_path.exists():
            self.add_result(
                "Badges", "README exists", False,
                "✗ README.md not found", "error"
            )
            return
        
        content = readme_path.read_text(encoding='utf-8')
        
        # Check for badge patterns
        badge_patterns = {
            'License': r'!\[License\]',
            'Version': r'!\[Version\]',
            'Build': r'!\[Build.*?\]|!\[CI.*?\]',
        }
        
        for badge_name, pattern in badge_patterns.items():
            if re.search(pattern, content, re.IGNORECASE):
                self.add_result(
                    "Badges", f"{badge_name} badge", True,
                    f"✓ {badge_name} badge found", "info"
                )
            else:
                self.add_result(
                    "Badges", f"{badge_name} badge", False,
                    f"✗ {badge_name} badge missing", "warning"
                )
    
    def validate_strategic_messaging(self):
        """Validate strategic positioning and messaging"""
        print("🎯 Validating strategic messaging...")
        
        readme_path = self.repo_root / "README.md"
        if not readme_path.exists():
            return
        
        content = readme_path.read_text(encoding='utf-8').lower()
        
        # Check for key strategic phrases
        strategic_phrases = {
            'TCP/IP of money': r'tcp/ip of money',
            'Trust through transparency': r'trust.*transparency|transparency.*trust',
            'Protocol standard': r'protocol.*standard|standard.*protocol',
            'Mathematical proofs': r'mathematical.*proof|proof.*mathematical',
            'Conservation laws': r'conservation.*law',
        }
        
        for phrase_name, pattern in strategic_phrases.items():
            if re.search(pattern, content, re.IGNORECASE):
                self.add_result(
                    "Strategic Messaging", phrase_name, True,
                    f"✓ '{phrase_name}' messaging present", "info"
                )
            else:
                self.add_result(
                    "Strategic Messaging", phrase_name, False,
                    f"⚠ '{phrase_name}' messaging not found", "warning"
                )
        
        # Check for clear open/commercial separation
        if 'commercial' in content or 'enterprise' in content:
            self.add_result(
                "Strategic Messaging", "Commercial separation", True,
                "✓ Commercial offerings mentioned", "info"
            )
        else:
            self.add_result(
                "Strategic Messaging", "Commercial separation", False,
                "⚠ Commercial offerings not clearly mentioned", "warning"
            )
    
    def validate_community_readiness(self):
        """Validate community infrastructure readiness"""
        print("👥 Validating community readiness...")
        
        # Check GitHub templates
        github_paths = [
            ".github/ISSUE_TEMPLATE",
            ".github/PULL_REQUEST_TEMPLATE.md",
            ".github/workflows"
        ]
        
        for path_str in github_paths:
            path = self.repo_root / path_str
            if path.exists():
                if path.is_dir():
                    files = list(path.iterdir())
                    self.add_result(
                        "Community", f"{path_str} exists", True,
                        f"✓ {path_str} has {len(files)} items", "info"
                    )
                else:
                    self.add_result(
                        "Community", f"{path_str} exists", True,
                        f"✓ {path_str} found", "info"
                    )
            else:
                self.add_result(
                    "Community", f"{path_str} exists", False,
                    f"✗ {path_str} not found", "error"
                )
        
        # Check for examples
        examples_path = self.repo_root / "examples"
        if examples_path.exists():
            ae_files = list(examples_path.glob("**/*.ae"))
            py_files = list(examples_path.glob("**/*.py"))
            total = len(ae_files) + len(py_files)
            self.add_result(
                "Community", "Examples available", True,
                f"✓ {total} example files found", "info"
            )
        else:
            self.add_result(
                "Community", "Examples directory", False,
                "✗ examples/ directory not found", "warning"
            )
    
    def generate_report(self) -> Dict:
        """Generate final validation report"""
        print("\n" + "="*70)
        print("📊 FINAL REVIEW VALIDATION REPORT")
        print("="*70 + "\n")
        
        # Group results by category
        by_category = {}
        for result in self.results:
            if result.category not in by_category:
                by_category[result.category] = []
            by_category[result.category].append(result)
        
        # Count totals
        total_checks = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        failed = sum(1 for r in self.results if not r.passed)
        errors = sum(1 for r in self.results if not r.passed and r.severity == "error")
        warnings = sum(1 for r in self.results if not r.passed and r.severity == "warning")
        
        # Print summary by category
        for category, results in sorted(by_category.items()):
            cat_passed = sum(1 for r in results if r.passed)
            cat_total = len(results)
            print(f"\n{category}: {cat_passed}/{cat_total} checks passed")
            print("-" * 70)
            
            for result in results:
                if not result.passed or result.severity == "info":
                    print(f"  {result.message}")
        
        # Overall summary
        print("\n" + "="*70)
        print("OVERALL SUMMARY")
        print("="*70)
        print(f"Total Checks: {total_checks}")
        print(f"✓ Passed: {passed}")
        print(f"✗ Failed: {failed}")
        print(f"  - Errors: {errors}")
        print(f"  - Warnings: {warnings}")
        
        # Determine overall status
        if errors == 0 and warnings == 0:
            status = "EXCELLENT"
            emoji = "🎉"
        elif errors == 0:
            status = "GOOD"
            emoji = "✅"
        elif errors <= 3:
            status = "NEEDS ATTENTION"
            emoji = "⚠️"
        else:
            status = "CRITICAL ISSUES"
            emoji = "❌"
        
        print(f"\nOverall Status: {emoji} {status}")
        print("="*70 + "\n")
        
        return {
            'total_checks': total_checks,
            'passed': passed,
            'failed': failed,
            'errors': errors,
            'warnings': warnings,
            'status': status,
            'by_category': {
                cat: {
                    'total': len(results),
                    'passed': sum(1 for r in results if r.passed),
                    'failed': sum(1 for r in results if not r.passed)
                }
                for cat, results in by_category.items()
            }
        }


def main():
    """Main execution"""
    validator = FinalReviewValidator()
    report = validator.validate_all()
    
    # Save report to file
    report_path = Path("TASK_18_FINAL_REVIEW_REPORT.md")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# Final Review Validation Report\n\n")
        f.write(f"**Status**: {report['status']}\n\n")
        f.write(f"**Total Checks**: {report['total_checks']}\n")
        f.write(f"**Passed**: {report['passed']}\n")
        f.write(f"**Failed**: {report['failed']}\n")
        f.write(f"- Errors: {report['errors']}\n")
        f.write(f"- Warnings: {report['warnings']}\n\n")
        
        f.write("## Results by Category\n\n")
        for category, stats in report['by_category'].items():
            f.write(f"### {category}\n")
            f.write(f"- Total: {stats['total']}\n")
            f.write(f"- Passed: {stats['passed']}\n")
            f.write(f"- Failed: {stats['failed']}\n\n")
    
    print(f"📄 Detailed report saved to: {report_path}")
    
    return 0 if report['errors'] == 0 else 1


if __name__ == "__main__":
    exit(main())
