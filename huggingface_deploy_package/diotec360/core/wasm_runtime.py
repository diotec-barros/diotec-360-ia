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
Aethel WASM Runtime - The Isolated Sanctuary
Executes WASM bytecode in isolated sandbox with gas metering

Security Features:
- Isolated linear memory
- No host access
- Gas metering (DoS protection)
- Deterministic execution
- Runtime verification

Philosophy: "Isolation is not paranoia. It's mathematics."
"""

import hashlib
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path


class GasExhaustedException(Exception):
    """Raised when gas limit is exceeded"""
    pass


class SandboxViolationException(Exception):
    """Raised when sandbox security is violated"""
    pass


class AethelWasmRuntime:
    """
    Executes WASM modules in isolated sandbox.
    
    The runtime provides:
    - Isolated linear memory (no host access)
    - Gas metering (prevents infinite loops)
    - Deterministic execution
    - Runtime verification
    - Complete audit trail
    """
    
    def __init__(self, wat_code: str, gas_limit: int = 10000):
        self.wat_code = wat_code
        self.gas_limit = gas_limit
        self.gas_used = 0
        self.audit_trail = []
        self.memory = bytearray(65536)  # 64KB isolated memory
        self.panic_mode = False
    
    def _log(self, level: str, message: str):
        """Add entry to audit trail"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'message': message,
            'gas_used': self.gas_used
        }
        self.audit_trail.append(entry)
        
        icon = {
            'INFO': '📋',
            'SUCCESS': '✅',
            'WARNING': '⚠️',
            'ERROR': '❌',
            'PANIC': '🚨',
            'GAS': '⛽'
        }.get(level, '•')
        
        print(f"{icon} [{level}] {message}")
    
    def _consume_gas(self, amount: int):
        """
        Consume gas for operation.
        
        Raises GasExhaustedException if limit exceeded.
        """
        self.gas_used += amount
        
        if self.gas_used > self.gas_limit:
            self._log('PANIC', f"Gas exhausted: {self.gas_used}/{self.gas_limit}")
            raise GasExhaustedException(f"Gas limit exceeded: {self.gas_used}/{self.gas_limit}")
    
    def _validate_sandbox(self):
        """
        Validate WAT code doesn't violate sandbox.
        
        Checks for:
        - Import statements (host access)
        - Syscalls
        - Dynamic calls
        - Memory violations
        """
        self._log('INFO', "Validating sandbox security...")
        
        # Check for dangerous patterns
        dangerous_patterns = [
            'import',
            'call_indirect',
            'memory.grow',
            'syscall',
            'host',
            'extern'
        ]
        
        for pattern in dangerous_patterns:
            if pattern in self.wat_code.lower():
                self._log('PANIC', f"Sandbox violation: {pattern} detected")
                raise SandboxViolationException(f"Sandbox violation: {pattern} detected in WAT code")
        
        self._log('SUCCESS', "Sandbox validation passed")
    
    def _simulate_wasm_execution(self, intent_name: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulate WASM execution.
        
        In production, this would use wasmtime/wasmer.
        For Phase 2, we simulate the execution with gas metering.
        """
        self._log('INFO', f"Executing WASM function: {intent_name}")
        self._log('GAS', f"Gas limit: {self.gas_limit}")
        
        # Initialize output state
        output_state = inputs.copy()
        
        # Simulate execution based on intent
        if intent_name == 'transfer':
            # Gas cost for transfer operation
            self._consume_gas(100)  # Load parameters
            
            sender_balance = inputs.get('sender_balance', 0)
            receiver_balance = inputs.get('receiver_balance', 0)
            amount = inputs.get('amount', 0)
            
            # Guard checks (gas cost)
            self._consume_gas(50)  # Guard: sender_balance >= amount
            if sender_balance < amount:
                self._log('PANIC', f"Guard violation: sender_balance ({sender_balance}) < amount ({amount})")
                raise SandboxViolationException("Guard violation in WASM execution")
            
            self._consume_gas(50)  # Guard: amount > 0
            if amount <= 0:
                self._log('PANIC', f"Guard violation: amount ({amount}) <= 0")
                raise SandboxViolationException("Guard violation in WASM execution")
            
            # Execute transfer (gas cost)
            self._consume_gas(100)  # Arithmetic operations
            output_state['sender_balance'] = sender_balance - amount
            output_state['receiver_balance'] = receiver_balance + amount
            
            self._log('SUCCESS', f"Transfer executed: {amount} units")
            self._log('INFO', f"  Sender: {sender_balance} -> {output_state['sender_balance']}")
            self._log('INFO', f"  Receiver: {receiver_balance} -> {output_state['receiver_balance']}")
        
        elif intent_name == 'vote':
            # Gas cost for vote operation
            self._consume_gas(100)  # Load parameters
            
            votes = inputs.get('votes', 0)
            old_votes = votes  # Snapshot
            
            # Guard checks
            self._consume_gas(50)  # Guard: votes >= 0
            if votes < 0:
                self._log('PANIC', f"Guard violation: votes ({votes}) < 0")
                raise SandboxViolationException("Guard violation in WASM execution")
            
            # Execute vote (gas cost)
            self._consume_gas(50)  # Arithmetic operation
            output_state['votes'] = votes + 1
            
            # Post-condition check (The Second Wall)
            self._consume_gas(50)  # Post-condition verification
            if output_state['votes'] != old_votes + 1:
                self._log('PANIC', f"Post-condition violation: votes should be {old_votes + 1}, got {output_state['votes']}")
                raise SandboxViolationException("Post-condition violation in WASM execution")
            
            self._log('SUCCESS', f"Vote recorded: {old_votes} -> {output_state['votes']}")
        
        elif intent_name == 'check_balance':
            # Gas cost for balance check
            self._consume_gas(100)  # Load parameters
            
            account_balance = inputs.get('account_balance', 0)
            minimum = inputs.get('minimum', 0)
            
            # Guard checks
            self._consume_gas(50)
            if account_balance < 0:
                self._log('PANIC', f"Guard violation: account_balance ({account_balance}) < 0")
                raise SandboxViolationException("Guard violation in WASM execution")
            
            # Execute check
            self._consume_gas(50)
            output_state['balance_check_passed'] = account_balance >= minimum
            
            self._log('SUCCESS', f"Balance check: {account_balance} >= {minimum} = {output_state['balance_check_passed']}")
        
        else:
            # Generic execution
            self._consume_gas(100)
            output_state['executed'] = True
            self._log('WARNING', f"Generic execution for intent: {intent_name}")
        
        self._log('GAS', f"Gas used: {self.gas_used}/{self.gas_limit}")
        
        return output_state
    
    def execute_safely(self, intent_name: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute WASM module in isolated sandbox.
        
        Process:
        1. Validate sandbox security
        2. Initialize gas metering
        3. Execute with isolation
        4. Verify post-conditions
        5. Return execution envelope
        
        Returns:
            Execution envelope with results and audit trail
        
        Raises:
            GasExhaustedException if gas limit exceeded
            SandboxViolationException if security violated
        """
        print("\n" + "="*70)
        print("🌐 AETHEL WASM RUNTIME - THE ISOLATED SANCTUARY")
        print("    WebAssembly Sandbox Execution")
        print("="*70 + "\n")
        
        self.audit_trail = []
        self.gas_used = 0
        start_time = datetime.now()
        
        try:
            # 1. Validate sandbox
            self._validate_sandbox()
            
            # 2. Log input state
            self._log('INFO', f"Input state: {inputs}")
            
            # 3. Execute in sandbox
            output_state = self._simulate_wasm_execution(intent_name, inputs)
            
            # 4. Generate execution envelope
            execution_time = (datetime.now() - start_time).total_seconds()
            
            envelope = {
                'intent_name': intent_name,
                'input_state': inputs,
                'output_state': output_state,
                'execution_time': execution_time,
                'gas_used': self.gas_used,
                'gas_limit': self.gas_limit,
                'verification_passed': True,
                'audit_trail': self.audit_trail.copy(),
                'wat_hash': hashlib.sha256(self.wat_code.encode()).hexdigest()
            }
            
            # 5. Seal envelope
            envelope_string = str(envelope['input_state']) + str(envelope['output_state'])
            envelope['envelope_signature'] = hashlib.sha256(envelope_string.encode()).hexdigest()
            
            self._log('SUCCESS', f"Execution complete in {execution_time:.4f}s")
            self._log('SUCCESS', f"Envelope sealed: {envelope['envelope_signature'][:16]}...")
            
            print("\n" + "="*70)
            print("✅ WASM EXECUTION SUCCESSFUL - SANDBOX SEALED")
            print("="*70 + "\n")
            
            return envelope
        
        except GasExhaustedException as e:
            print("\n" + "="*70)
            print("⛽ GAS EXHAUSTED - EXECUTION TERMINATED")
            print(f"   Reason: {e}")
            print("="*70 + "\n")
            raise
        
        except SandboxViolationException as e:
            print("\n" + "="*70)
            print("🚨 SANDBOX VIOLATION - EXECUTION BLOCKED")
            print(f"   Reason: {e}")
            print("="*70 + "\n")
            raise
        
        except Exception as e:
            self._log('PANIC', f"Unexpected error: {e}")
            print("\n" + "="*70)
            print("🚨 EXECUTION FAILED - SANCTUARY COMPROMISED")
            print(f"   Reason: {e}")
            print("="*70 + "\n")
            raise


class WasmCompilationError(Exception):
    """Raised when WAT to WASM compilation fails"""
    pass


def compile_wat_to_wasm(wat_code: str, output_path: Optional[str] = None) -> bytes:
    """
    Compile WAT to WASM bytecode.
    
    In production, this would use wat2wasm from WABT toolkit.
    For Phase 2, we simulate the compilation.
    
    Args:
        wat_code: WebAssembly Text code
        output_path: Optional path to save WASM file
    
    Returns:
        WASM bytecode as bytes
    """
    print(f"\n🔧 [WAT2WASM] Compiling WAT to WASM...")
    
    # Simulate WASM compilation
    # In production: subprocess.run(['wat2wasm', wat_file, '-o', wasm_file])
    
    # WASM magic number and version
    wasm_header = bytes([0x00, 0x61, 0x73, 0x6D, 0x01, 0x00, 0x00, 0x00])
    
    # Simulated WASM bytecode (placeholder)
    wasm_bytecode = wasm_header + wat_code.encode()
    
    if output_path:
        with open(output_path, 'wb') as f:
            f.write(wasm_bytecode)
        print(f"💾 [WAT2WASM] WASM saved to: {output_path}")
    
    print(f"✅ [WAT2WASM] Compilation successful")
    print(f"   WASM size: {len(wasm_bytecode)} bytes")
    
    return wasm_bytecode
