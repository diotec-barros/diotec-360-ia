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
Aethel CLI - Command Line Interface
The professional interface to the Aethel compiler
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from diotec360.core.kernel import AethelKernel
from diotec360.core.vault import AethelVault
from diotec360.core.vault_distributed import AethelDistributedVault


class AethelCLI:
    """Professional CLI for Aethel compiler"""
    
    def __init__(self):
        self.version = "1.0.0"
        self.epoch = 2
    
    def print_banner(self):
        """Print Aethel banner"""
        print("""
╔══════════════════════════════════════════════════════════════╗
║                    AETHEL COMPILER v0.6                      ║
║          The First Language That Refuses "Maybe"             ║
╚══════════════════════════════════════════════════════════════╝
        """)
    
    def build(self, input_file, output_file=None, ai_provider="anthropic", max_attempts=3, verbose=False):
        """
        Build an Aethel source file
        
        Args:
            input_file: Path to .ae source file
            output_file: Path to output file (default: auto-generated)
            ai_provider: AI provider (anthropic, openai, ollama)
            max_attempts: Maximum compilation attempts
            verbose: Enable verbose output
        """
        if verbose:
            self.print_banner()
        
        print(f"[AETHEL] Building: {input_file}")
        
        # Read source file
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                source_code = f.read()
        except FileNotFoundError:
            print(f"[ERROR] File not found: {input_file}")
            return 1
        except Exception as e:
            print(f"[ERROR] Failed to read file: {e}")
            return 1
        
        # Auto-generate output filename if not provided
        if output_file is None:
            input_path = Path(input_file)
            output_file = f"output/{input_path.stem}.rs"
        
        # Initialize kernel
        print(f"[AETHEL] Initializing kernel (AI: {ai_provider})...")
        kernel = AethelKernel(ai_provider=ai_provider)
        
        # Compile
        print(f"[AETHEL] Compiling with formal verification...")
        result = kernel.compile(
            source_code,
            max_attempts=max_attempts,
            output_file=output_file
        )
        
        # Report results
        if result['status'] == 'SUCCESS':
            print(f"\n[SUCCESS] Compilation complete!")
            print(f"  Output: {output_file}")
            print(f"  Vault Hash: {result['vault_hash'][:16]}...")
            print(f"  Attempts: {result['attempts']}")
            print(f"  Status: MATHEMATICALLY PROVED")
            return 0
        else:
            print(f"\n[FAILED] Compilation failed: {result['message']}")
            if verbose and 'report' in result:
                print(result['report'])
            return 1
    
    def verify(self, input_file, verbose=False):
        """
        Verify an Aethel source file without generating code
        """
        print(f"[AETHEL] Verifying: {input_file}")
        
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                source_code = f.read()
        except Exception as e:
            print(f"[ERROR] Failed to read file: {e}")
            return 1
        
        from diotec360.core.parser import AethelParser
        from diotec360.core.judge import AethelJudge
        
        # Parse
        print("[AETHEL] Parsing...")
        parser = AethelParser()
        try:
            ast = parser.parse(source_code)
        except Exception as e:
            print(f"[ERROR] Parse failed: {e}")
            return 1
        
        # Verify each intent
        judge = AethelJudge(ast)
        all_proved = True
        
        for intent_name in ast.keys():
            print(f"\n[AETHEL] Verifying intent: {intent_name}")
            result = judge.verify_logic(intent_name)
            
            if result['status'] == 'PROVED':
                print(f"  Status: PROVED")
                print(f"  Message: {result['message']}")
            else:
                print(f"  Status: FAILED")
                print(f"  Message: {result['message']}")
                all_proved = False
                
                if result.get('counter_examples'):
                    print("  Counter-examples:")
                    for ce in result['counter_examples']:
                        print(f"    - {ce['condition']}: {ce['counter_example']}")
        
        if all_proved:
            print("\n[SUCCESS] All intents verified!")
            return 0
        else:
            print("\n[FAILED] Some intents failed verification")
            return 1
    
    def vault_list(self):
        """List functions in the vault"""
        vault = AethelVault()
        functions = vault.list_functions()
        
        if not functions:
            print("[VAULT] No functions stored yet")
            return 0
        
        print(f"\n[VAULT] {len(functions)} function(s) stored:\n")
        for hash_id, info in functions.items():
            print(f"  {info['intent_name']}")
            print(f"    Hash: {hash_id[:16]}...{hash_id[-8:]}")
            print(f"    Status: {info['status']}")
            print(f"    Created: {info['created_at']}")
            print()
        
        return 0
    
    def vault_export(self, function_hash, output=None):
        """Export function as bundle"""
        vault = AethelDistributedVault()
        
        try:
            bundle_path = vault.export_bundle(function_hash, output)
            print(f"\n[SUCCESS] Bundle exported: {bundle_path}")
            return 0
        except Exception as e:
            print(f"\n[ERROR] Export failed: {e}")
            return 1
    
    def vault_import(self, bundle_path, verify=True):
        """Import function bundle"""
        vault = AethelDistributedVault()
        
        try:
            function_hash = vault.import_bundle(bundle_path, verify_integrity=verify)
            print(f"\n[SUCCESS] Function imported: {function_hash[:16]}...")
            return 0
        except Exception as e:
            print(f"\n[ERROR] Import failed: {e}")
            return 1
    
    def vault_stats(self):
        """Show vault statistics"""
        vault = AethelVault()
        functions = vault.list_functions()
        
        if not functions:
            print("\n[VAULT] No functions stored yet")
            return 0
        
        print(f"\n[VAULT] Statistics:")
        print(f"  Total Functions: {len(functions)}")
        
        # Count by status
        proved = sum(1 for f in functions.values() if f['status'] == 'MATHEMATICALLY_PROVED')
        print(f"  Proved Functions: {proved}")
        
        # Calculate total storage
        total_size = 0
        for hash_id in functions.keys():
            file_path = vault.vault_path / f"{hash_id}.json"
            if file_path.exists():
                total_size += file_path.stat().st_size
        
        print(f"  Storage Used: {total_size / 1024:.2f} KB")
        print(f"  Vault Path: {vault.vault_path.absolute()}")
        print()
        
        return 0
    
    def vault_sync(self):
        """Show vault sync status"""
        vault = AethelDistributedVault()
        status = vault.sync_status()
        
        print("\n[VAULT] Synchronization Status:")
        print(f"  Total Functions: {status['total_functions']}")
        print(f"  Certified Functions: {status['certified_functions']}")
        print(f"  Available Bundles: {status['available_bundles']}")
        if status['merkle_root']:
            print(f"  Merkle Root: {status['merkle_root'][:16]}...")
        print(f"  Vault Path: {status['vault_path']}")
        print()
        
        return 0
    
    def run_bundle(self, bundle_path, input_json=None, input_file=None, use_vault=False, use_wasm=False, state_root=None, output_file=None):
        """Execute bundle in secure environment with optional state management"""
        from diotec360.core.runtime import AethelRuntime
        from diotec360.core.wasm_compiler import AethelWasmCompiler
        from diotec360.core.wasm_runtime import AethelWasmRuntime
        from diotec360.core.vault_distributed import AethelDistributedVault
        from diotec360.core.state import AethelStateManager
        import json
        
        print(f"[AETHEL] Executing bundle: {bundle_path}")
        
        # Initialize state manager if state_root provided
        state_manager = None
        if state_root:
            print(f"[AETHEL] Using state management (root: {state_root[:16]}...)")
            state_manager = AethelStateManager()
            
            # Try to load existing state
            if state_manager.load_snapshot():
                current_root = state_manager.get_state_root()
                if current_root != state_root:
                    print(f"[WARNING] State root mismatch: expected {state_root[:16]}..., got {current_root[:16]}...")
        
        # Parse input JSON
        try:
            if input_file:
                with open(input_file, 'r') as f:
                    inputs = json.load(f)
            elif input_json:
                inputs = json.loads(input_json)
            else:
                print("[ERROR] Either --input or --input-file must be provided")
                return 1
        except json.JSONDecodeError as e:
            print(f"[ERROR] Invalid input JSON: {e}")
            return 1
        except FileNotFoundError:
            print(f"[ERROR] Input file not found: {input_file}")
            return 1
        
        # Load bundle
        try:
            with open(bundle_path, 'r') as f:
                bundle = json.load(f)
        except Exception as e:
            print(f"[ERROR] Failed to load bundle: {e}")
            return 1
        
        # Execute based on mode
        try:
            if use_wasm:
                # WASM execution mode
                print("[AETHEL] Using WASM sandbox execution")
                
                # Compile to WAT
                compiler = AethelWasmCompiler(bundle)
                wat_code = compiler.compile()
                
                # Execute in WASM runtime
                runtime = AethelWasmRuntime(wat_code, gas_limit=10000)
                envelope = runtime.execute_safely(bundle['intent_name'], inputs)
            else:
                # Standard runtime execution
                vault = AethelDistributedVault() if use_vault else None
                runtime = AethelRuntime(vault=vault)
                envelope = runtime.execute_safely(bundle_path, inputs)
            
            # If state manager is active, apply state transition
            if state_manager and bundle['intent_name'] == 'transfer':
                print("\n[STATE] Applying state transition...")
                
                sender = inputs.get('sender', 'sender')
                receiver = inputs.get('receiver', 'receiver')
                amount = inputs.get('amount', 0)
                
                # Apply transfer to state
                transition = state_manager.execute_transfer(sender, receiver, amount)
                
                if transition['success']:
                    print(f"[STATE] Transition successful")
                    print(f"  Old root: {transition['old_root'][:16]}...")
                    print(f"  New root: {transition['new_root'][:16]}...")
                    
                    # Save state snapshot
                    state_manager.save_snapshot()
                    
                    # Add state info to envelope
                    if isinstance(envelope, dict):
                        envelope['state_transition'] = transition
                    else:
                        envelope_dict = envelope.to_dict()
                        envelope_dict['state_transition'] = transition
                        envelope = envelope_dict
                else:
                    print(f"[STATE] Transition failed")
            
            # Display results
            print("\n[EXECUTION ENVELOPE]")
            print(f"  Intent: {envelope.get('intent_name', 'N/A')}")
            if 'bundle_hash' in envelope:
                print(f"  Bundle Hash: {envelope['bundle_hash'][:16]}...")
            print(f"  Execution Time: {envelope['execution_time']:.4f}s")
            
            if 'gas_used' in envelope:
                print(f"  Gas Used: {envelope['gas_used']}/{envelope['gas_limit']}")
            
            print(f"  Verification: {'PASSED' if envelope.get('verification_passed') else 'FAILED'}")
            
            if 'envelope_signature' in envelope:
                print(f"  Envelope Signature: {envelope['envelope_signature'][:16]}...")
            
            if 'state_transition' in envelope:
                print(f"  State Root: {envelope['state_transition']['new_root'][:16]}...")
            
            print("\n[INPUT STATE]")
            input_state = envelope.get('input_state', inputs)
            for key, value in input_state.items():
                print(f"  {key}: {value}")
            
            print("\n[OUTPUT STATE]")
            output_state = envelope.get('output_state', {})
            for key, value in output_state.items():
                print(f"  {key}: {value}")
            
            # Save envelope if requested
            if output_file:
                with open(output_file, 'w') as f:
                    json.dump(envelope if isinstance(envelope, dict) else envelope.to_dict(), f, indent=2)
                print(f"\n[SUCCESS] Envelope saved to: {output_file}")
            
            return 0
        
        except Exception as e:
            print(f"\n[ERROR] Execution failed: {e}")
            return 1
    
    def compile_wasm(self, bundle_path, output_file=None, validate=True):
        """Compile bundle to WebAssembly"""
        from diotec360.core.wasm_compiler import AethelWasmCompiler
        import json
        
        print(f"[AETHEL] Compiling to WebAssembly: {bundle_path}")
        
        # Load bundle
        try:
            with open(bundle_path, 'r') as f:
                bundle = json.load(f)
        except Exception as e:
            print(f"[ERROR] Failed to load bundle: {e}")
            return 1
        
        # Compile to WAT
        try:
            compiler = AethelWasmCompiler(bundle)
            wat_code = compiler.compile()
            
            # Validate if requested
            if validate:
                is_valid, message = compiler.validate_wat()
                if not is_valid:
                    print(f"[ERROR] WAT validation failed: {message}")
                    return 1
            
            # Save WAT
            if output_file is None:
                output_file = f"output/{bundle['intent_name']}.wat"
            
            compiler.save_wat(output_file)
            
            # Display info
            wat_hash = compiler.get_wat_hash()
            print(f"\n[SUCCESS] WAT compilation complete")
            print(f"  Output: {output_file}")
            print(f"  WAT Hash: {wat_hash[:16]}...")
            print(f"  Size: {len(wat_code)} bytes")
            
            return 0
        
        except Exception as e:
            print(f"\n[ERROR] Compilation failed: {e}")
            return 1
        
        # Initialize runtime
        vault = AethelDistributedVault() if use_vault else None
        runtime = AethelRuntime(vault=vault)
        
        # Execute
        try:
            envelope = runtime.execute_safely(bundle_path, inputs)
            
            # Display results
            print("\n[EXECUTION ENVELOPE]")
            print(f"  Intent: {envelope.intent_name}")
            print(f"  Bundle Hash: {envelope.bundle_hash[:16]}...")
            print(f"  Execution Time: {envelope.execution_time:.4f}s")
            print(f"  Verification: {'PASSED' if envelope.verification_passed else 'FAILED'}")
            print(f"  Envelope Signature: {envelope.envelope_signature[:16]}...")
            
            print("\n[INPUT STATE]")
            for key, value in envelope.input_state.items():
                print(f"  {key}: {value}")
            
            print("\n[OUTPUT STATE]")
            for key, value in envelope.output_state.items():
                print(f"  {key}: {value}")
            
            # Save envelope if requested
            if output_file:
                with open(output_file, 'w') as f:
                    json.dump(envelope.to_dict(), f, indent=2)
                print(f"\n[SUCCESS] Envelope saved to: {output_file}")
            
            return 0
        
        except Exception as e:
            print(f"\n[ERROR] Execution failed: {e}")
            return 1
    
    def run(self, args=None):
        """Main CLI entry point"""
        parser = argparse.ArgumentParser(
            description='Aethel Compiler - The First Language That Refuses "Maybe"',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  aethel build mycode.ae                    # Build with default settings
  aethel build mycode.ae -o output.rs       # Specify output file
  aethel build mycode.ae --ai ollama        # Use local Ollama
  aethel verify mycode.ae                   # Verify without generating code
  aethel vault list                         # List functions in vault
  aethel vault stats                        # Show vault statistics

For more information: https://github.com/aethel-lang/aethel-core
            """
        )
        
        parser.add_argument('--version', action='version', version=f'Aethel v{self.version} (Epoch {self.epoch})')
        
        subparsers = parser.add_subparsers(dest='command', help='Command to execute')
        
        # Build command
        build_parser = subparsers.add_parser('build', help='Build an Aethel source file')
        build_parser.add_argument('input', help='Input .ae file')
        build_parser.add_argument('-o', '--output', help='Output file path')
        build_parser.add_argument('--ai', choices=['anthropic', 'openai', 'ollama'], default='anthropic', help='AI provider')
        build_parser.add_argument('--max-attempts', type=int, default=3, help='Maximum compilation attempts')
        build_parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
        
        # Verify command
        verify_parser = subparsers.add_parser('verify', help='Verify an Aethel source file')
        verify_parser.add_argument('input', help='Input .ae file')
        verify_parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
        
        # Vault commands
        vault_parser = subparsers.add_parser('vault', help='Vault operations')
        vault_subparsers = vault_parser.add_subparsers(dest='vault_command')
        vault_subparsers.add_parser('list', help='List functions in vault')
        vault_subparsers.add_parser('stats', help='Show vault statistics')
        
        # Export command
        export_parser = vault_subparsers.add_parser('export', help='Export function as bundle')
        export_parser.add_argument('hash', help='Function hash to export')
        export_parser.add_argument('-o', '--output', help='Output bundle file')
        
        # Import command
        import_parser = vault_subparsers.add_parser('import', help='Import function bundle')
        import_parser.add_argument('bundle', help='Bundle file to import')
        import_parser.add_argument('--no-verify', action='store_true', help='Skip integrity verification (dangerous!)')
        
        # Sync command
        vault_subparsers.add_parser('sync', help='Show vault sync status')
        
        # Run command
        run_parser = subparsers.add_parser('run', help='Execute bundle in secure environment')
        run_parser.add_argument('bundle', help='Bundle file to execute')
        run_parser.add_argument('--input', help='Input state as JSON string')
        run_parser.add_argument('--input-file', help='Input state from JSON file')
        run_parser.add_argument('--vault', help='Use vault for Merkle verification', action='store_true')
        run_parser.add_argument('--wasm', help='Use WASM sandbox execution', action='store_true')
        run_parser.add_argument('--state', help='State root hash for state management')
        run_parser.add_argument('-o', '--output', help='Save execution envelope to file')
        
        # Compile WASM command
        wasm_parser = subparsers.add_parser('compile-wasm', help='Compile bundle to WebAssembly')
        wasm_parser.add_argument('bundle', help='Bundle file to compile')
        wasm_parser.add_argument('-o', '--output', help='Output WAT file path')
        wasm_parser.add_argument('--validate', help='Validate WAT security', action='store_true', default=True)
        
        # Parse arguments
        if args is None:
            args = sys.argv[1:]
        
        parsed_args = parser.parse_args(args)
        
        # Execute command
        if parsed_args.command == 'build':
            return self.build(
                parsed_args.input,
                parsed_args.output,
                parsed_args.ai,
                parsed_args.max_attempts,
                parsed_args.verbose
            )
        elif parsed_args.command == 'verify':
            return self.verify(parsed_args.input, parsed_args.verbose)
        elif parsed_args.command == 'vault':
            if parsed_args.vault_command == 'list':
                return self.vault_list()
            elif parsed_args.vault_command == 'stats':
                return self.vault_stats()
            elif parsed_args.vault_command == 'export':
                return self.vault_export(parsed_args.hash, parsed_args.output)
            elif parsed_args.vault_command == 'import':
                return self.vault_import(parsed_args.bundle, not parsed_args.no_verify)
            elif parsed_args.vault_command == 'sync':
                return self.vault_sync()
            else:
                vault_parser.print_help()
                return 1
        elif parsed_args.command == 'run':
            return self.run_bundle(
                parsed_args.bundle,
                parsed_args.input,
                parsed_args.input_file,
                parsed_args.vault,
                parsed_args.wasm,
                parsed_args.state,
                parsed_args.output
            )
        elif parsed_args.command == 'compile-wasm':
            return self.compile_wasm(
                parsed_args.bundle,
                parsed_args.output,
                parsed_args.validate
            )
        else:
            parser.print_help()
            return 1


def main():
    """CLI entry point"""
    cli = AethelCLI()
    sys.exit(cli.run())


if __name__ == '__main__':
    main()
