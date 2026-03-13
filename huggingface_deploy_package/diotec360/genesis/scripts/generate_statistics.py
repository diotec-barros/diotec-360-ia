#!/usr/bin/env python3
"""
Aethel Genesis Statistics Generator

Calculates comprehensive codebase metrics including:
- Total line counts by category
- Test file and assertion counts
- Invariant extraction from verify blocks
- Performance metrics from benchmarks
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict


class StatisticsGenerator:
    """Generates comprehensive statistics for Aethel codebase."""
    
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        
        # Directories to exclude
        self.exclude_dirs = {
            '.git', '__pycache__', '.hypothesis', 'node_modules',
            '.venv', 'venv', '.env', '.aethel_state', '.aethel_vault',
            '.aethel_moe', '.aethel_sentinel', '.aethel_vigilance',
            '.demo_audit', 'frontend', '.kiro', '.github',
            '.aethel_state_nodeA', '.aethel_state_nodeB',
            '.aethel_vault_nodeA', '.aethel_vault_nodeB',
            '.aethel_sentinel_nodeA', '.aethel_sentinel_nodeB'
        }
    
    def should_exclude_path(self, path: Path) -> bool:
        """Check if path should be excluded."""
        parts = path.parts
        return any(excluded in parts for excluded in self.exclude_dirs)
    
    def count_lines_by_category(self) -> Dict[str, Dict[str, int]]:
        """Count lines of code by category."""
        print("Counting lines by category...")
        
        categories = {
            'core_engine': ['aethel/core'],
            'trading': ['aethel/bot', 'aethel/lib/trading'],
            'ai': ['aethel/ai', 'aethel/moe'],
            'consensus': ['aethel/consensus'],
            'lattice': ['aethel/lattice', 'aethel/mesh'],
            'commercial': ['aethel/bridge', 'aethel/api'],
            'stdlib': ['aethel/stdlib'],
            'plugins': ['aethel/plugins'],
            'tests': [],  # Will be identified by filename pattern
            'demos': [],  # Will be identified by filename pattern
            'benchmarks': []  # Will be identified by filename pattern
        }
        
        stats = defaultdict(lambda: {'files': 0, 'total_lines': 0, 'code_lines': 0, 'comment_lines': 0})
        
        # Scan all Python files
        for py_file in self.root_dir.rglob('*.py'):
            if self.should_exclude_path(py_file):
                continue
            
            relative_path = py_file.relative_to(self.root_dir)
            path_str = str(relative_path).replace('\\', '/')
            
            # Determine category
            category = None
            
            # Check filename patterns first
            if py_file.name.startswith('test_'):
                category = 'tests'
            elif py_file.name.startswith('demo_'):
                category = 'demos'
            elif py_file.name.startswith('benchmark_') or 'benchmarks' in py_file.parts:
                category = 'benchmarks'
            else:
                # Check directory-based categories
                for cat_name, cat_dirs in categories.items():
                    if any(cat_dir in path_str for cat_dir in cat_dirs):
                        category = cat_name
                        break
            
            if category:
                total, code, comments = self._count_file_lines(py_file)
                stats[category]['files'] += 1
                stats[category]['total_lines'] += total
                stats[category]['code_lines'] += code
                stats[category]['comment_lines'] += comments
        
        # Also count .ae files
        for ae_file in self.root_dir.rglob('*.ae'):
            if self.should_exclude_path(ae_file):
                continue
            
            relative_path = ae_file.relative_to(self.root_dir)
            path_str = str(relative_path).replace('\\', '/')
            
            # Categorize .ae files
            if 'aethel/lib/trading' in path_str:
                category = 'trading'
            elif 'aethel/examples' in path_str or 'docs/examples' in path_str:
                category = 'examples'
            else:
                category = 'other'
            
            total, code, comments = self._count_file_lines(ae_file)
            stats[category]['files'] += 1
            stats[category]['total_lines'] += total
            stats[category]['code_lines'] += code
            stats[category]['comment_lines'] += comments
        
        return dict(stats)
    
    def _count_file_lines(self, file_path: Path) -> Tuple[int, int, int]:
        """Count lines in a file. Returns (total, code, comments)."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            total = len(lines)
            code = 0
            comments = 0
            
            for line in lines:
                stripped = line.strip()
                if not stripped:
                    continue
                if stripped.startswith('#') or stripped.startswith('//'):
                    comments += 1
                else:
                    code += 1
            
            return total, code, comments
        except Exception as e:
            print(f"Warning: Could not read {file_path}: {e}", file=sys.stderr)
            return 0, 0, 0

    def count_test_files_and_assertions(self) -> Dict[str, int]:
        """Count test files and assertions."""
        print("Counting test files and assertions...")
        
        stats = {
            'unit_test_files': 0,
            'property_test_files': 0,
            'integration_test_files': 0,
            'total_test_files': 0,
            'total_assertions': 0,
            'property_tests': 0
        }
        
        # Patterns to identify assertions
        assertion_patterns = [
            r'\bassert\s+',
            r'\.assert',
            r'self\.assert\w+',
            r'@given\(',
            r'@example\('
        ]
        
        # Scan test files
        for test_file in self.root_dir.rglob('test_*.py'):
            if self.should_exclude_path(test_file):
                continue
            
            stats['total_test_files'] += 1
            
            try:
                with open(test_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Categorize test type
                if 'property' in test_file.name or '@given' in content:
                    stats['property_test_files'] += 1
                elif 'integration' in test_file.name or 'end_to_end' in test_file.name:
                    stats['integration_test_files'] += 1
                else:
                    stats['unit_test_files'] += 1
                
                # Count assertions
                for pattern in assertion_patterns:
                    matches = re.findall(pattern, content)
                    stats['total_assertions'] += len(matches)
                
                # Count property tests (@given decorators)
                property_matches = re.findall(r'@given\(', content)
                stats['property_tests'] += len(property_matches)
                
            except Exception as e:
                print(f"Warning: Could not read {test_file}: {e}", file=sys.stderr)
        
        return stats
    
    def extract_invariants(self) -> Dict[str, List[str]]:
        """Extract invariants from verify blocks in .ae files and Python code."""
        print("Extracting invariants...")
        
        invariants = {
            'conservation_laws': [],
            'trading_invariants': [],
            'consensus_properties': [],
            'other_invariants': []
        }
        
        # Scan .ae files for verify blocks
        for ae_file in self.root_dir.rglob('*.ae'):
            if self.should_exclude_path(ae_file):
                continue
            
            try:
                with open(ae_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Extract verify blocks
                verify_blocks = re.findall(r'verify\s*\{([^}]+)\}', content, re.DOTALL)
                
                for block in verify_blocks:
                    # Extract individual assertions
                    assertions = [line.strip() for line in block.split('\n') if line.strip() and not line.strip().startswith('//')]
                    
                    # Categorize based on file location
                    path_str = str(ae_file).replace('\\', '/')
                    if 'trading' in path_str:
                        invariants['trading_invariants'].extend(assertions)
                    else:
                        invariants['conservation_laws'].extend(assertions)
                
            except Exception as e:
                print(f"Warning: Could not read {ae_file}: {e}", file=sys.stderr)
        
        # Scan Python files for verify patterns
        for py_file in self.root_dir.rglob('*.py'):
            if self.should_exclude_path(py_file):
                continue
            
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Look for conservation checks
                if 'conservation' in py_file.name.lower():
                    conservation_checks = re.findall(r'#\s*Invariant:\s*(.+)', content)
                    invariants['conservation_laws'].extend(conservation_checks)
                
                # Look for consensus properties
                if 'consensus' in str(py_file):
                    consensus_checks = re.findall(r'#\s*Property:\s*(.+)', content)
                    invariants['consensus_properties'].extend(consensus_checks)
                
            except Exception as e:
                print(f"Warning: Could not read {py_file}: {e}", file=sys.stderr)
        
        return invariants
    
    def collect_performance_metrics(self) -> Dict[str, float]:
        """Collect performance metrics from benchmark files."""
        print("Collecting performance metrics...")
        
        metrics = {
            'proof_generation_ms': None,
            'parallel_execution_ms': None,
            'consensus_finality_s': None,
            'trade_execution_ms': None,
            'throughput_tps': None
        }
        
        # Scan benchmark files
        for benchmark_file in self.root_dir.rglob('benchmark_*.py'):
            if self.should_exclude_path(benchmark_file):
                continue
            
            try:
                with open(benchmark_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Extract performance numbers from comments or docstrings
                # Look for patterns like "# Average: 100ms" or "Throughput: 1000 TPS"
                
                if 'proof' in benchmark_file.name:
                    match = re.search(r'(\d+\.?\d*)\s*ms', content)
                    if match and metrics['proof_generation_ms'] is None:
                        metrics['proof_generation_ms'] = float(match.group(1))
                
                if 'parallel' in benchmark_file.name:
                    match = re.search(r'(\d+\.?\d*)\s*ms', content)
                    if match and metrics['parallel_execution_ms'] is None:
                        metrics['parallel_execution_ms'] = float(match.group(1))
                
                if 'consensus' in benchmark_file.name:
                    match = re.search(r'(\d+\.?\d*)\s*s(?:ec)?', content)
                    if match and metrics['consensus_finality_s'] is None:
                        metrics['consensus_finality_s'] = float(match.group(1))
                
                if 'throughput' in benchmark_file.name:
                    match = re.search(r'(\d+\.?\d*)\s*(?:TPS|tps|transactions)', content)
                    if match and metrics['throughput_tps'] is None:
                        metrics['throughput_tps'] = float(match.group(1))
                
            except Exception as e:
                print(f"Warning: Could not read {benchmark_file}: {e}", file=sys.stderr)
        
        return metrics
    
    def generate_statistics(self) -> Dict:
        """Generate all statistics."""
        print("Generating comprehensive statistics...")
        print()
        
        stats = {
            'lines_of_code': self.count_lines_by_category(),
            'test_coverage': self.count_test_files_and_assertions(),
            'invariants': self.extract_invariants(),
            'performance': self.collect_performance_metrics()
        }
        
        return stats
    
    def format_markdown(self, stats: Dict) -> str:
        """Format statistics as markdown document."""
        lines = []
        
        lines.append("# AETHEL v5.0 - STATISTICS")
        lines.append("")
        lines.append("*Generated automatically by Genesis Statistics Generator*")
        lines.append("")
        
        # Lines of Code Section
        lines.append("## Lines of Code")
        lines.append("")
        
        loc_stats = stats['lines_of_code']
        total_files = sum(cat['files'] for cat in loc_stats.values())
        total_lines = sum(cat['total_lines'] for cat in loc_stats.values())
        total_code = sum(cat['code_lines'] for cat in loc_stats.values())
        
        lines.append(f"**Total Files**: {total_files}")
        lines.append(f"**Total Lines**: {total_lines:,}")
        lines.append(f"**Code Lines**: {total_code:,}")
        lines.append("")
        
        lines.append("### By Category")
        lines.append("")
        lines.append("| Category | Files | Total Lines | Code Lines |")
        lines.append("|----------|-------|-------------|------------|")
        
        for category in sorted(loc_stats.keys()):
            cat_stats = loc_stats[category]
            lines.append(f"| {category.replace('_', ' ').title()} | {cat_stats['files']} | {cat_stats['total_lines']:,} | {cat_stats['code_lines']:,} |")
        
        lines.append("")
        
        # Test Coverage Section
        lines.append("## Test Coverage")
        lines.append("")
        
        test_stats = stats['test_coverage']
        lines.append(f"**Total Test Files**: {test_stats['total_test_files']}")
        lines.append(f"- Unit Tests: {test_stats['unit_test_files']}")
        lines.append(f"- Property Tests: {test_stats['property_test_files']}")
        lines.append(f"- Integration Tests: {test_stats['integration_test_files']}")
        lines.append("")
        lines.append(f"**Total Assertions**: {test_stats['total_assertions']:,}")
        lines.append(f"**Property Tests**: {test_stats['property_tests']}")
        lines.append("")
        
        # Invariants Section
        lines.append("## Invariants & Properties")
        lines.append("")
        
        invariants = stats['invariants']
        total_invariants = sum(len(inv_list) for inv_list in invariants.values())
        
        lines.append(f"**Total Invariants**: {total_invariants}")
        lines.append("")
        
        for inv_type, inv_list in invariants.items():
            if inv_list:
                lines.append(f"### {inv_type.replace('_', ' ').title()}")
                lines.append(f"**Count**: {len(inv_list)}")
                lines.append("")
                for i, inv in enumerate(inv_list[:10], 1):  # Show first 10
                    lines.append(f"{i}. {inv[:100]}")
                if len(inv_list) > 10:
                    lines.append(f"... and {len(inv_list) - 10} more")
                lines.append("")
        
        # Performance Metrics Section
        lines.append("## Performance Metrics")
        lines.append("")
        
        perf = stats['performance']
        
        if perf['proof_generation_ms']:
            lines.append(f"**Proof Generation**: {perf['proof_generation_ms']:.2f} ms")
        if perf['parallel_execution_ms']:
            lines.append(f"**Parallel Execution**: {perf['parallel_execution_ms']:.2f} ms")
        if perf['consensus_finality_s']:
            lines.append(f"**Consensus Finality**: {perf['consensus_finality_s']:.2f} s")
        if perf['trade_execution_ms']:
            lines.append(f"**Trade Execution**: {perf['trade_execution_ms']:.2f} ms")
        if perf['throughput_tps']:
            lines.append(f"**Throughput**: {perf['throughput_tps']:.0f} TPS")
        
        if not any(perf.values()):
            lines.append("*Performance metrics not yet collected from benchmarks*")
        
        lines.append("")
        
        # Summary Section
        lines.append("## Summary")
        lines.append("")
        lines.append(f"Aethel v5.0 consists of **{total_code:,} lines of code** across **{total_files} files**, ")
        lines.append(f"protected by **{test_stats['total_test_files']} test files** with **{test_stats['total_assertions']:,} assertions** ")
        lines.append(f"and **{total_invariants} mathematical invariants**.")
        lines.append("")
        
        return '\n'.join(lines)
    
    def save_statistics(self, output_path: Path):
        """Generate and save statistics to file."""
        stats = self.generate_statistics()
        markdown = self.format_markdown(stats)
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown)
        
        print()
        print(f"Statistics saved to: {output_path}")
        
        # Print summary
        loc_stats = stats['lines_of_code']
        total_code = sum(cat['code_lines'] for cat in loc_stats.values())
        test_stats = stats['test_coverage']
        invariants = stats['invariants']
        total_invariants = sum(len(inv_list) for inv_list in invariants.values())
        
        print(f"Total code lines: {total_code:,}")
        print(f"Total test files: {test_stats['total_test_files']}")
        print(f"Total assertions: {test_stats['total_assertions']:,}")
        print(f"Total invariants: {total_invariants}")


def main():
    """Main entry point."""
    # Determine root directory (project root)
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent.parent.parent  # Go up to project root
    
    # Output path
    output_path = root_dir / 'aethel' / 'genesis' / 'STATISTICS.md'
    
    print(f"Root directory: {root_dir}")
    print(f"Output path: {output_path}")
    print()
    
    # Generate statistics
    generator = StatisticsGenerator(root_dir)
    generator.save_statistics(output_path)
    
    print("\n✓ Statistics generation complete!")


if __name__ == '__main__':
    main()
