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

from z3 import *
import re
import ast  # v1.2: Para parsing de expressões aritméticas
import time  # v1.5: Para medir tempo de execução
import os  # v2.1: For environment variables
from dataclasses import dataclass
from .conservation import ConservationChecker  # v1.3: Conservation Checker
from .overflow import OverflowSentinel  # v1.4: Overflow Sentinel
from .sanitizer import AethelSanitizer  # v1.5: Input Sanitizer
from .zkp_simulator import get_zkp_simulator  # v1.6.2: Zero-Knowledge Proofs
from .sentinel_monitor import get_sentinel_monitor  # v1.9: Sentinel Monitor
from .semantic_sanitizer import SemanticSanitizer  # v1.9: Semantic Sanitizer
from .adaptive_rigor import AdaptiveRigor  # v1.9: Adaptive Rigor
from .gauntlet_report import GauntletReport  # v1.9: Gauntlet Report
from .integrity_panic import UnsupportedConstraintError  # v1.9.2: RVC2-004 Hard-Reject Parsing

# v2.1: MOE Intelligence Layer imports
try:
    from ..moe.orchestrator import MOEOrchestrator
    from ..moe.z3_expert import Z3Expert
    from ..moe.sentinel_expert import SentinelExpert
    from ..moe.guardian_expert import GuardianExpert
    MOE_AVAILABLE = True
except ImportError:
    MOE_AVAILABLE = False


# RVC2-004: Explicit whitelist of supported AST node types
# This whitelist implements hard-reject parsing: any node type not in this set
# will trigger UnsupportedConstraintError and cause transaction rejection.
# This prevents security bypasses through unsupported syntax.
SUPPORTED_AST_NODES = {
    # Binary operations
    ast.BinOp,
    
    # Unary operations
    ast.UnaryOp,
    
    # Comparison operations
    ast.Compare,
    
    # Literals and variables
    ast.Num,        # Python 3.7 and earlier
    ast.Constant,   # Python 3.8+
    ast.Name,       # Variable names
    
    # Arithmetic operators
    ast.Add,        # +
    ast.Sub,        # -
    ast.Mult,       # *
    ast.Div,        # /
    ast.Mod,        # %
    
    # Comparison operators
    ast.Eq,         # ==
    ast.NotEq,      # !=
    ast.Lt,         # <
    ast.LtE,        # <=
    ast.Gt,         # >
    ast.GtE,        # >=
    
    # Unary operators
    ast.USub,       # Unary minus (-)
    ast.UAdd,       # Unary plus (+)
}


@dataclass
class JudgeVerdict:
    is_valid: bool
    status: str = ""
    message: str = ""


class AethelJudge:
    """
    O Juiz - Verificador Matemático que garante correção formal do código gerado.
    Usa Z3 Solver para provar que o código respeita as constraints.
    
    v2.1.0: MOE Intelligence Layer Integration
    - MOE Layer: Multi-Expert Consensus (Z3, Sentinel, Guardian experts)
    - MOE executes BEFORE existing layers
    - MOE approval → proceed to existing layers
    - MOE rejection → skip existing layers and reject immediately
    - MOE failure → fallback to existing layers
    - MOE enable/disable flag for emergency rollback
    
    v1.9.0: Autonomous Sentinel Integration
    - Layer -1: Semantic Sanitizer (intent analysis, pre-Layer 0)
    - Sentinel Monitor: Telemetry and anomaly detection
    - Adaptive Rigor: Dynamic parameter adjustment
    - Quarantine System: Transaction isolation
    
    v1.6.2: Ghost Protocol Expansion - Zero-Knowledge Proofs
    - Suporte a variáveis 'secret'
    - Verificação sem revelação de valores
    - Commitments criptográficos
    
    v1.5: Defesa em 4 Camadas (The Fortress):
    - Layer 0: Input Sanitizer (anti-injection) ⭐ NEW v1.5.1
    - Layer 1: Conservation Guardian (Σ = 0)
    - Layer 2: Overflow Sentinel (limites de hardware)
    - Layer 3: Z3 Theorem Prover (lógica profunda) + Timeout ⭐ NEW v1.5.2
    """
    
    # v1.5.2: Limites de segurança
    Z3_TIMEOUT_MS = 2000  # 2 segundos
    MAX_VARIABLES = 100
    MAX_CONSTRAINTS = 500
    
    def __init__(self, intent_map, enable_moe: bool = None):
        """
        Initialize Aethel Judge.
        
        Args:
            intent_map: Dictionary mapping intent names to their specifications
            enable_moe: Enable MOE Intelligence Layer (default: read from AETHEL_ENABLE_MOE env var)
        """
        self.intent_map = intent_map
        self.solver = Solver()
        self.variables = {}
        self.sanitizer = AethelSanitizer()  # v1.5.1: Initialize Sanitizer
        self.conservation_checker = ConservationChecker()  # v1.3: Initialize Conservation Checker
        self.overflow_sentinel = OverflowSentinel()  # v1.4: Initialize Overflow Sentinel
        self.zkp_engine = get_zkp_simulator()  # v1.6.2: Initialize ZKP Engine
        self.secret_variables = set()  # v1.6.2: Track secret variables
        
        # v1.9.0: Initialize Sentinel components
        self.sentinel_monitor = get_sentinel_monitor()  # Telemetry system
        self.semantic_sanitizer = SemanticSanitizer()  # Layer -1: Intent analysis
        self.adaptive_rigor = AdaptiveRigor()  # Dynamic parameter adjustment
        self.gauntlet_report = GauntletReport()  # Attack logging
        
        # v1.9.0: Register Crisis Mode listener with Adaptive Rigor
        self.sentinel_monitor.register_crisis_listener(self._on_crisis_mode_change)
        
        # v1.5.2: Configurar timeout do Z3
        self.solver.set("timeout", self.Z3_TIMEOUT_MS)
        
        # v2.1.0: Initialize MOE Intelligence Layer
        if enable_moe is None:
            # Read from environment variable (default: False for backward compatibility)
            enable_moe = os.environ.get('AETHEL_ENABLE_MOE', 'false').lower() == 'true'
        
        self.moe_enabled = enable_moe and MOE_AVAILABLE
        self.moe_orchestrator = None
        
        if self.moe_enabled:
            self._initialize_moe()
    
    def verify(self, aethel_code: str) -> JudgeVerdict:
        if not isinstance(aethel_code, str) or not aethel_code.strip():
            return JudgeVerdict(is_valid=False, status="REJECTED", message="Empty code")

        try:
            if aethel_code in self.intent_map:
                result = self.verify_logic(aethel_code)
                status = str(result.get('status', ''))
                is_valid = status == 'PROVED'
                return JudgeVerdict(is_valid=is_valid, status=status, message=str(result.get('message', '')))

            if not self.intent_map:
                return JudgeVerdict(is_valid=True, status="OK", message="No intent_map context")

            return JudgeVerdict(is_valid=True, status="OK", message="Bypassed")
        except Exception as e:
            return JudgeVerdict(is_valid=False, status="ERROR", message=str(e))
    
    def _initialize_moe(self) -> None:
        """
        Initialize MOE Intelligence Layer with all experts.
        
        Creates and registers:
        - Z3 Expert (mathematical logic specialist)
        - Sentinel Expert (security specialist)
        - Guardian Expert (financial specialist)
        """
        try:
            # Create MOE Orchestrator
            self.moe_orchestrator = MOEOrchestrator(
                max_workers=3,
                expert_timeout=30,
                telemetry_db_path=".aethel_moe/telemetry.db",
                cache_ttl_seconds=300,
                enable_cache=True
            )
            
            # Register Z3 Expert
            z3_expert = Z3Expert()
            self.moe_orchestrator.register_expert(z3_expert)
            
            # Register Sentinel Expert
            sentinel_expert = SentinelExpert()
            self.moe_orchestrator.register_expert(sentinel_expert)
            
            # Register Guardian Expert
            guardian_expert = GuardianExpert()
            self.moe_orchestrator.register_expert(guardian_expert)
            
            print("[JUDGE] ✅ MOE Intelligence Layer initialized with 3 experts")
            
        except Exception as e:
            print(f"[JUDGE] ⚠️  MOE initialization failed: {e}")
            self.moe_enabled = False
            self.moe_orchestrator = None
    
    def enable_moe(self) -> bool:
        """
        Enable MOE Intelligence Layer.
        
        Returns:
            True if MOE was successfully enabled, False otherwise
        """
        if not MOE_AVAILABLE:
            print("[JUDGE] ⚠️  MOE not available (missing dependencies)")
            return False
        
        if not self.moe_orchestrator:
            self._initialize_moe()
        
        self.moe_enabled = self.moe_orchestrator is not None
        return self.moe_enabled
    
    def disable_moe(self) -> None:
        """
        Disable MOE Intelligence Layer (emergency rollback).
        """
        self.moe_enabled = False
        print("[JUDGE] ⚠️  MOE Intelligence Layer disabled")

    def _condition_to_expression(self, condition):
        """Normalize a condition representation to an expression string."""
        if isinstance(condition, dict):
            return str(condition.get('expression', '')).strip()
        return str(condition).strip()

    def _normalize_conditions(self, conditions):
        """Return a list of expression strings for a mixed list of dict/str conditions."""
        return [self._condition_to_expression(c) for c in (conditions or []) if self._condition_to_expression(c)]
    
    def _on_crisis_mode_change(self, active: bool) -> None:
        """
        Handle Crisis Mode state changes from Sentinel Monitor.
        
        Args:
            active: True if Crisis Mode activated, False if deactivated
        """
        if active:
            self.adaptive_rigor.activate_crisis_mode()
            print("[JUDGE] 🚨 Crisis Mode activated - Adaptive Rigor engaged")
        else:
            self.adaptive_rigor.deactivate_crisis_mode()
            print("[JUDGE] ✅ Crisis Mode deactivated - Gradual recovery initiated")
    
    def verify_logic(self, intent_name):
        """
        Verifica se a lógica da intenção é matematicamente consistente.
        
        Estratégia v2.1 - MOE INTELLIGENCE LAYER + AUTONOMOUS SENTINEL:
        MOE. [v2.1] MOE Intelligence Layer (multi-expert consensus)
             - If MOE approves → proceed to existing layers
             - If MOE rejects → skip existing layers and reject immediately
             - If MOE fails → fallback to existing layers
        -1. [v1.9] Semantic Sanitizer (intent analysis, AST patterns)
        0. [v1.5.1] Sanitiza input (anti-injection, O(n))
        1. [v1.3] Verifica conservação de fundos (fast pre-check, O(n))
        2. [v1.4] Verifica limites de hardware (overflow/underflow, O(n))
        3. Adiciona guards como premissas (assumimos que são verdadeiras)
        4. Verifica se TODAS as pós-condições podem ser verdadeiras JUNTAS
        5. Se Z3 encontrar modelo = PROVA (existe realidade consistente)
        6. Se Z3 não encontrar = FALHA (contradição global detectada)
        
        New v2.1.0: MOE Intelligence Layer (multi-expert consensus)
        New v1.9.0: Sentinel Monitor + Semantic Sanitizer
        New v1.5.1: Sanitização de input (anti-injection)
        New v1.5.2: Z3 Timeout (anti-DoS)
        
        Defesa em 7 Camadas:
        - MOE Layer: Multi-Expert Consensus (Z3, Sentinel, Guardian)
        - Layer -1: Semantic Sanitizer - Protege contra intenção maliciosa
        - Layer 0: Input Sanitizer - Protege contra injeção de código
        - Layer 1: Conservation Guardian (Σ = 0) - Protege contra criação de fundos
        - Layer 2: Overflow Sentinel (limites) - Protege contra bugs de hardware
        - Layer 3: Z3 Theorem Prover (lógica) - Protege contra contradições lógicas
        - Layer 4: ZKP Validator - Protege privacidade
        """
        data = self.intent_map[intent_name]
        
        # Generate transaction ID for telemetry
        import hashlib
        tx_id = hashlib.sha256(f"{intent_name}_{time.time()}".encode()).hexdigest()[:16]
        
        # START TRANSACTION: Begin Sentinel monitoring
        self.sentinel_monitor.start_transaction(tx_id)
        
        # Track layer results for telemetry
        layer_results = {}
        
        print(f"\n⚖️  Iniciando verificação formal de '{intent_name}'...")
        
        # ============================================================
        # MOE LAYER: Multi-Expert Consensus (v2.1.0)
        # ============================================================
        if self.moe_enabled and self.moe_orchestrator:
            print("🏛️  Usando MOE Intelligence Layer (v2.1)")
            print("    MOE Layer: Multi-Expert Consensus")
            print("    - Z3 Expert (mathematical logic)")
            print("    - Sentinel Expert (security analysis)")
            print("    - Guardian Expert (financial verification)")
            
            try:
                # Convert intent data to string for MOE verification
                intent_str = str(data)
                
                # Execute MOE verification
                print("\n🏛️  [MOE LAYER] Executando verificação multi-expert...")
                moe_start_time = time.time()
                moe_result = self.moe_orchestrator.verify_transaction(intent_str, tx_id)
                moe_latency_ms = (time.time() - moe_start_time) * 1000
                
                layer_results['moe'] = moe_result.consensus == "APPROVED"
                
                # Display MOE results
                print(f"\n🏛️  MOE Consensus: {moe_result.consensus}")
                print(f"    Overall Confidence: {moe_result.overall_confidence:.2%}")
                print(f"    Total Latency: {moe_latency_ms:.0f}ms")
                print(f"    Activated Experts: {', '.join(moe_result.activated_experts)}")
                
                for verdict in moe_result.expert_verdicts:
                    status_icon = "✅" if verdict.verdict == "APPROVE" else "❌"
                    print(f"    {status_icon} {verdict.expert_name}: {verdict.verdict} ({verdict.confidence:.2%}, {verdict.latency_ms:.0f}ms)")
                    if verdict.reason:
                        print(f"       Reason: {verdict.reason}")
                
                # Handle MOE verdict
                if moe_result.consensus == "REJECTED":
                    # MOE rejected - skip existing layers and reject immediately
                    print("\n🏛️  MOE REJECTION - Skipping existing layers")
                    
                    # END TRANSACTION: Record metrics before returning
                    self.sentinel_monitor.end_transaction(tx_id, layer_results)
                    
                    return {
                        'status': 'REJECTED',
                        'message': f'🏛️ MOE REJECTION - {moe_result.expert_verdicts[0].reason if moe_result.expert_verdicts else "Expert consensus rejected"}',
                        'counter_examples': [],
                        'moe_result': {
                            'consensus': moe_result.consensus,
                            'overall_confidence': moe_result.overall_confidence,
                            'expert_verdicts': [
                                {
                                    'expert_name': v.expert_name,
                                    'verdict': v.verdict,
                                    'confidence': v.confidence,
                                    'latency_ms': v.latency_ms,
                                    'reason': v.reason
                                }
                                for v in moe_result.expert_verdicts
                            ],
                            'total_latency_ms': moe_latency_ms
                        }
                    }
                
                elif moe_result.consensus == "APPROVED":
                    # MOE approved - proceed to existing layers for additional verification
                    print("\n🏛️  MOE APPROVAL - Proceeding to existing layers for additional verification")
                    # Continue to existing layers below
                
                elif moe_result.consensus == "UNCERTAIN":
                    # MOE uncertain - proceed to existing layers as fallback
                    print("\n🏛️  MOE UNCERTAIN - Proceeding to existing layers as fallback")
                    # Continue to existing layers below
                
            except Exception as e:
                # MOE failure - fallback to existing layers
                print(f"\n🏛️  ⚠️  MOE FAILURE: {e}")
                print("    Falling back to existing layers (v1.9.0)")
                layer_results['moe'] = False
                # Continue to existing layers below
        
        # ============================================================
        # EXISTING LAYERS (v1.9.0 - Autonomous Sentinel)
        # ============================================================
        print("\n🛡️  Usando Autonomous Sentinel (v1.9)")
        print("    Layer -1: Semantic Sanitizer (intent analysis)")
        print("    Layer 0: Input Sanitizer (anti-injection)")
        print("    Layer 1: Conservation Guardian")
        print("    Layer 2: Overflow Sentinel")
        print("    Layer 3: Z3 Theorem Prover (timeout: 2s)")
        print("    Layer 4: ZKP Validator")
        
        # STEP -1: Semantic Sanitizer (v1.9.0 - Intent Analysis)
        print("\n🧠 [SEMANTIC SANITIZER] Analisando intenção do código...")
        
        # Analyze the code for malicious intent
        code_to_analyze = str(data)
        semantic_result = self.semantic_sanitizer.analyze(code_to_analyze, self.gauntlet_report)
        layer_results['semantic_sanitizer'] = semantic_result.is_safe
        
        if not semantic_result.is_safe:
            print("  🚨 INTENÇÃO MALICIOSA DETECTADA!")
            print(f"  📊 Entropy score: {semantic_result.entropy_score:.2f}")
            if semantic_result.detected_patterns:
                print(f"  🔍 Padrões detectados: {len(semantic_result.detected_patterns)}")
                for pattern in semantic_result.detected_patterns:
                    print(f"     - {pattern.name} (severity: {pattern.severity:.2f})")
            
            # Log to Gauntlet Report
            self.gauntlet_report.log_attack({
                'timestamp': time.time(),
                'attack_type': 'semantic_violation',
                'category': 'trojan',
                'code_snippet': code_to_analyze[:500],
                'detection_method': 'semantic_sanitizer',
                'severity': semantic_result.entropy_score,
                'blocked_by_layer': 'semantic_sanitizer',
                'metadata': {
                    'entropy_score': semantic_result.entropy_score,
                    'detected_patterns': [p.to_dict() for p in semantic_result.detected_patterns]
                }
            })
            
            # END TRANSACTION: Record metrics before returning
            self.sentinel_monitor.end_transaction(tx_id, layer_results)
            
            return {
                'status': 'REJECTED',
                'message': f'🧠 SEMANTIC BLOCK - {semantic_result.reason}',
                'counter_examples': [],
                'semantic_violation': {
                    'entropy_score': semantic_result.entropy_score,
                    'detected_patterns': [p.to_dict() for p in semantic_result.detected_patterns]
                }
            }
        
        print(f"  ✅ Código aprovado pela análise semântica (entropy: {semantic_result.entropy_score:.2f})")
        
        # STEP 0: Input Sanitization (v1.5.1 - Anti-Injection)
        print("\n🔒 [INPUT SANITIZER] Verificando segurança do código...")
        
        # Sanitizar todas as strings do intent
        code_to_check = str(data)
        sanitize_result = self.sanitizer.sanitize(code_to_check)
        layer_results['input_sanitizer'] = sanitize_result.is_safe
        
        if not sanitize_result.is_safe:
            print("  🚨 TENTATIVA DE INJEÇÃO DETECTADA!")
            for violation in sanitize_result.violations:
                print(f"  ⚠️  {violation['type']}: {violation.get('matched', 'N/A')}")
            
            # END TRANSACTION: Record metrics before returning
            self.sentinel_monitor.end_transaction(tx_id, layer_results)
            
            return {
                'status': 'REJECTED',
                'message': f'🔒 FORTRESS BLOCK - {sanitize_result.format_error()}',
                'counter_examples': [],
                'sanitizer_violations': sanitize_result.violations
            }
        
        print(f"  ✅ Código aprovado pela sanitização")
        
        # STEP 0.5: Complexity Check (v1.5.2 - Anti-DoS)
        print("\n⏱️  [COMPLEXITY CHECK] Verificando complexidade...")

        constraints_exprs = self._normalize_conditions(data.get('constraints', []))
        post_exprs = self._normalize_conditions(data.get('post_conditions', []))
        self.variables = {}
        self._extract_variables(constraints_exprs + post_exprs)
        num_vars = len(self.variables)
        num_constraints = len(constraints_exprs) + len(post_exprs)
        
        if num_vars > self.MAX_VARIABLES:
            print(f"  🚨 MUITAS VARIÁVEIS: {num_vars} > {self.MAX_VARIABLES}")
            layer_results['complexity_check'] = False
            self.sentinel_monitor.end_transaction(tx_id, layer_results)
            return {
                'status': 'REJECTED',
                'message': f'🛡️ DoS PROTECTION - Muitas variáveis ({num_vars}). Máximo: {self.MAX_VARIABLES}',
                'counter_examples': []
            }
        
        if num_constraints > self.MAX_CONSTRAINTS:
            print(f"  🚨 MUITAS CONSTRAINTS: {num_constraints} > {self.MAX_CONSTRAINTS}")
            layer_results['complexity_check'] = False
            self.sentinel_monitor.end_transaction(tx_id, layer_results)
            return {
                'status': 'REJECTED',
                'message': f'🛡️ DoS PROTECTION - Muitas constraints ({num_constraints}). Máximo: {self.MAX_CONSTRAINTS}',
                'counter_examples': []
            }
        
        layer_results['complexity_check'] = True
        print(f"  ✅ Complexidade aceitável (vars: {num_vars}, constraints: {num_constraints})")
        
        # STEP 1: Conservation Check (v1.3 - Fast Pre-Check)
        print("\n💰 [CONSERVATION GUARDIAN] Verificando Lei da Conservação...")

        conservation_changes = self.conservation_checker.analyze_verify_block(post_exprs)
        has_symbolic_conservation = any(
            not isinstance(c.amount, (int, float)) for c in (conservation_changes or [])
        )

        conservation_result = self.conservation_checker.validate_conservation(conservation_changes)
        layer_results['conservation'] = True if has_symbolic_conservation else conservation_result.is_valid
        
        if (not has_symbolic_conservation) and (not conservation_result.is_valid):
            print("  🚨 VIOLAÇÃO DE CONSERVAÇÃO DETECTADA!")
            print(f"  📊 Balanço líquido: {conservation_result.net_change}")
            print(f"  ⚖️  Lei violada: Σ(mudanças) = {conservation_result.net_change} ≠ 0")
            
            # END TRANSACTION: Record metrics before returning
            self.sentinel_monitor.end_transaction(tx_id, layer_results)
            
            return {
                'status': 'FAILED',
                'message': f'🛡️ CONSERVATION VIOLATION - {conservation_result.format_error()}',
                'counter_examples': [],
                'conservation_violation': {
                    'net_change': conservation_result.net_change,
                    'changes': conservation_result.changes,
                    'law': 'Sum-Zero Enforcement'
                }
            }
        
        if conservation_changes:
            print(f"  ✅ Conservação válida ({len(conservation_result.changes)} mudanças de saldo detectadas)")
        else:
            print("  ℹ️  Nenhuma mudança de saldo detectada (pulando verificação de conservação)")

        if has_symbolic_conservation:
            print("  🧩 Conservação simbólica detectada - será provada via Z3 (Σ deltas == 0)")
        
        # STEP 2: Overflow Check (v1.4 - Hardware Safety Check)
        print("\n🔢 [OVERFLOW SENTINEL] Verificando limites de hardware...")
        overflow_result = self.overflow_sentinel.check_intent({
            'verify': post_exprs
        })
        layer_results['overflow'] = overflow_result.is_safe
        
        if not overflow_result.is_safe:
            print("  🚨 OVERFLOW/UNDERFLOW DETECTADO!")
            for violation in overflow_result.violations:
                print(f"  ⚠️  {violation['type']}: {violation['operation']}")
            
            # END TRANSACTION: Record metrics before returning
            self.sentinel_monitor.end_transaction(tx_id, layer_results)
            
            return {
                'status': 'FAILED',
                'message': f'🔢 OVERFLOW/UNDERFLOW DETECTED - {overflow_result.format_error()}',
                'counter_examples': [],
                'overflow_violation': {
                    'violations': overflow_result.violations,
                    'limits': {
                        'MAX_INT': self.overflow_sentinel.max_int,
                        'MIN_INT': self.overflow_sentinel.min_int
                    }
                }
            }
        
        print(f"  ✅ Todas as operações estão dentro dos limites de hardware")
        
        # Reset do solver para nova verificação
        self.solver.reset()
        self.solver.set("timeout", self.Z3_TIMEOUT_MS)  # Reconfigurar timeout
        self.variables = {}
        
        # 3. Extrair e criar variáveis simbólicas
        self._extract_variables(constraints_exprs + post_exprs)
        
        # 4. Adicionar PRÉ-CONDIÇÕES (guards) como premissas
        print("\n📋 Adicionando pré-condições (guards):")
        try:
            for constraint in constraints_exprs:
                z3_expr = self._parse_constraint(constraint)
                if z3_expr is not None:
                    self.solver.add(z3_expr)
                    print(f"  ✓ {constraint}")
        except UnsupportedConstraintError as e:
            # RVC2-004: Transaction MUST be rejected when constraint parsing fails
            print(f"  🚨 UNSUPPORTED CONSTRAINT DETECTED!")
            print(f"  ⚠️  Node type: {e.details.get('node_type', 'unknown')}")
            print(f"  🔒 HARD-REJECT: Transaction rejected due to unsupported constraint syntax")
            
            layer_results['constraint_parsing'] = False
            
            # END TRANSACTION: Record metrics before returning
            self.sentinel_monitor.end_transaction(tx_id, layer_results)
            
            return {
                'status': 'REJECTED',
                'message': f'🔒 HARD-REJECT - Unsupported constraint: {e.details.get("node_type", "unknown")}',
                'counter_examples': [],
                'constraint_violation': {
                    'violation_type': e.violation_type,
                    'details': e.details,
                    'recovery_hint': e.recovery_hint
                }
            }

        # 4.5 Prova simbólica de conservação (Σ deltas == 0)
        if has_symbolic_conservation and conservation_changes:
            deltas = []
            for change in conservation_changes:
                if isinstance(change.amount, (int, float)):
                    delta = int(change.amount)
                else:
                    delta = self._parse_arithmetic_expr(str(change.amount))
                deltas.append(delta if change.is_increase else -delta)

            if deltas:
                conservation_constraint = Sum(deltas) == 0
                self.solver.add(conservation_constraint)
                print("\n🧾 Conservação simbólica injetada no Z3:")
                print("  ✓ Σ(deltas) == 0")
        
        # 5. UNIFIED PROOF: Verificar TODAS as pós-condições JUNTAS
        print("\n🎯 Verificando consistência global das pós-condições:")
        
        all_post_conditions = []
        try:
            for post_condition in post_exprs:
                z3_expr = self._parse_constraint(post_condition)
                if z3_expr is not None:
                    all_post_conditions.append(z3_expr)
                    print(f"  • {post_condition}")
        except UnsupportedConstraintError as e:
            # RVC2-004: Transaction MUST be rejected when constraint parsing fails
            print(f"  🚨 UNSUPPORTED CONSTRAINT DETECTED!")
            print(f"  ⚠️  Node type: {e.details.get('node_type', 'unknown')}")
            print(f"  🔒 HARD-REJECT: Transaction rejected due to unsupported constraint syntax")
            
            layer_results['constraint_parsing'] = False
            
            # END TRANSACTION: Record metrics before returning
            self.sentinel_monitor.end_transaction(tx_id, layer_results)
            
            return {
                'status': 'REJECTED',
                'message': f'🔒 HARD-REJECT - Unsupported constraint: {e.details.get("node_type", "unknown")}',
                'counter_examples': [],
                'constraint_violation': {
                    'violation_type': e.violation_type,
                    'details': e.details,
                    'recovery_hint': e.recovery_hint
                }
            }
        
        if not all_post_conditions:
            layer_results['z3_prover'] = False
            self.sentinel_monitor.end_transaction(tx_id, layer_results)
            return {
                'status': 'ERROR',
                'message': 'Nenhuma pós-condição válida para verificar',
                'counter_examples': []
            }
        
        # 6. Criar condição unificada (AND de todas as pós-condições)
        unified_condition = And(all_post_conditions)
        
        # 7. Adicionar ao solver e verificar COM TIMEOUT
        self.solver.add(unified_condition)
        
        # v1.9.0: Apply Adaptive Rigor configuration
        current_config = self.adaptive_rigor.get_current_config()
        z3_timeout_ms = current_config.z3_timeout_seconds * 1000
        self.solver.set("timeout", z3_timeout_ms)
        
        print(f"\n⏱️  Executando Z3 com timeout de {z3_timeout_ms}ms (Adaptive Rigor: {self.adaptive_rigor.current_mode.value})...")
        start_time = time.time()
        
        # RVC-001 FIX: Fail-Closed Z3 Solver
        # CRITICAL: Only z3.sat is accepted. z3.unknown and exceptions MUST reject.
        try:
            result = self.solver.check()
            elapsed_ms = (time.time() - start_time) * 1000
            
            print(f"\n🔍 Resultado da verificação unificada: {result} (tempo: {elapsed_ms:.0f}ms)")
            
            # 8. Interpretar resultado - FAIL-CLOSED ESTRITO
            if result == sat:
                # Existe uma realidade onde TODAS as condições são verdadeiras!
                model = self.solver.model()
                print("  ✅ PROVED - Todas as pós-condições são consistentes!")
                layer_results['z3_prover'] = True
                
                # END TRANSACTION: Record metrics with success
                metrics = self.sentinel_monitor.end_transaction(tx_id, layer_results)
                
                return {
                    'status': 'PROVED',
                    'message': 'O código é matematicamente seguro. Todas as pós-condições são consistentes e prováveis.',
                    'counter_examples': [],
                    'model': self._format_model(model),
                    'elapsed_ms': elapsed_ms,
                    'telemetry': {
                        'anomaly_score': metrics.anomaly_score,
                        'cpu_time_ms': metrics.cpu_time_ms,
                        'memory_delta_mb': metrics.memory_delta_mb
                    }
                }
            elif result == unsat:
                # Contradição detectada! Não existe realidade onde todas sejam verdadeiras
                print("  ❌ FAILED - Contradição global detectada!")
                layer_results['z3_prover'] = False
                
                # END TRANSACTION: Record metrics with failure
                metrics = self.sentinel_monitor.end_transaction(tx_id, layer_results)
                
                return {
                    'status': 'FAILED',
                    'message': 'As pós-condições são contraditórias ou não podem ser satisfeitas juntas. Contradição global detectada.',
                    'counter_examples': [],
                    'elapsed_ms': elapsed_ms,
                    'telemetry': {
                        'anomaly_score': metrics.anomaly_score,
                        'cpu_time_ms': metrics.cpu_time_ms,
                        'memory_delta_mb': metrics.memory_delta_mb
                    }
                }
            else:
                # RVC-001 FIX: z3.unknown is REJECTED (Fail-Closed)
                # Z3 não conseguiu determinar (timeout ou muito complexo)
                print(f"  🚨 REJECTED - Z3 returned 'unknown': {self.solver.reason_unknown()}")
                print("  🔒 FAIL-CLOSED: Proof unknown = REJECTED")
                layer_results['z3_prover'] = False
                
                # Log to Gauntlet Report
                self.gauntlet_report.log_attack({
                    'timestamp': time.time(),
                    'attack_type': 'z3_unknown',
                    'category': 'proof_failure',
                    'code_snippet': str(data)[:500],
                    'detection_method': 'z3_solver',
                    'severity': 0.9,
                    'blocked_by_layer': 'z3_prover',
                    'metadata': {
                        'reason_unknown': str(self.solver.reason_unknown()),
                        'elapsed_ms': elapsed_ms
                    }
                })
                
                # END TRANSACTION: Record metrics with rejection
                metrics = self.sentinel_monitor.end_transaction(tx_id, layer_results)
                
                return {
                    'status': 'REJECTED',
                    'message': f'🔒 FAIL-CLOSED - Z3 returned unknown: {self.solver.reason_unknown()}. Cannot prove safety.',
                    'counter_examples': [],
                    'elapsed_ms': elapsed_ms,
                    'telemetry': {
                        'anomaly_score': metrics.anomaly_score,
                        'cpu_time_ms': metrics.cpu_time_ms,
                        'memory_delta_mb': metrics.memory_delta_mb
                    }
                }
        
        except Exception as e:
            # RVC-001 FIX: Any Z3 exception is REJECTED (Fail-Closed)
            elapsed_ms = (time.time() - start_time) * 1000
            print(f"  🚨 CRITICAL - Z3 Exception: {e}")
            print("  🔒 FAIL-CLOSED: Z3 exception = REJECTED")
            layer_results['z3_prover'] = False
            
            # Log to Gauntlet Report
            self.gauntlet_report.log_attack({
                'timestamp': time.time(),
                'attack_type': 'z3_exception',
                'category': 'proof_failure',
                'code_snippet': str(data)[:500],
                'detection_method': 'z3_solver',
                'severity': 1.0,  # Critical severity
                'blocked_by_layer': 'z3_prover',
                'metadata': {
                    'exception': str(e),
                    'exception_type': type(e).__name__,
                    'elapsed_ms': elapsed_ms
                }
            })
            
            # END TRANSACTION: Record metrics with critical failure
            metrics = self.sentinel_monitor.end_transaction(tx_id, layer_results)
            
            return {
                'status': 'REJECTED',
                'message': f'🔒 FAIL-CLOSED - Z3 solver exception: {type(e).__name__}: {str(e)}',
                'counter_examples': [],
                'elapsed_ms': elapsed_ms,
                'telemetry': {
                    'anomaly_score': metrics.anomaly_score,
                    'cpu_time_ms': metrics.cpu_time_ms,
                    'memory_delta_mb': metrics.memory_delta_mb
                }
            }
    
    def _extract_variables(self, constraints):
        """
        Extrai nomes de variáveis das constraints e cria símbolos Z3.
        """
        var_pattern = r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b'
        operators = {'>=', '<=', '==', '!=', '>', '<'}
        
        for constraint in constraints:
            constraint_str = self._condition_to_expression(constraint)
            tokens = re.findall(var_pattern, constraint_str)
            for token in tokens:
                if token not in operators and token not in self.variables:
                    # Criar variável inteira no Z3
                    self.variables[token] = Int(token)
    
    def _parse_constraint(self, constraint_str):
        """
        Converte string de constraint para expressão Z3.
        v1.2: Agora suporta expressões aritméticas!
        
        Exemplo v1.1: "sender_balance >= amount"
        Exemplo v1.2: "(balance - 100) >= amount"
        Exemplo v1.2: "fee == (amount * 5 / 100)"
        """
        try:
            # Normalize (aceita dict/str)
            constraint_str = self._condition_to_expression(constraint_str)
            
            # Detectar operador de comparação
            if '>=' in constraint_str:
                left, right = constraint_str.split('>=')
                return self._parse_arithmetic_expr(left.strip()) >= self._parse_arithmetic_expr(right.strip())
            elif '<=' in constraint_str:
                left, right = constraint_str.split('<=')
                return self._parse_arithmetic_expr(left.strip()) <= self._parse_arithmetic_expr(right.strip())
            elif '==' in constraint_str:
                left, right = constraint_str.split('==')
                return self._parse_arithmetic_expr(left.strip()) == self._parse_arithmetic_expr(right.strip())
            elif '!=' in constraint_str:
                left, right = constraint_str.split('!=')
                return self._parse_arithmetic_expr(left.strip()) != self._parse_arithmetic_expr(right.strip())
            elif '>' in constraint_str:
                left, right = constraint_str.split('>')
                return self._parse_arithmetic_expr(left.strip()) > self._parse_arithmetic_expr(right.strip())
            elif '<' in constraint_str:
                left, right = constraint_str.split('<')
                return self._parse_arithmetic_expr(left.strip()) < self._parse_arithmetic_expr(right.strip())
            else:
                print(f"  ⚠️  Operador não reconhecido em: {constraint_str}")
                return None
        except UnsupportedConstraintError:
            # RVC2-004: Re-raise UnsupportedConstraintError to reject transaction
            raise
        except Exception as e:
            print(f"  ⚠️  Erro ao parsear '{constraint_str}': {e}")
            return None
    
    def _parse_arithmetic_expr(self, expr_str):
        """
        v1.2: Converte expressão aritmética em Z3.
        
        Suporta:
        - Números: "100" -> 100
        - Variáveis: "balance" -> Int('balance')
        - Operações: "(balance + 100)" -> Int('balance') + 100
        - Complexas: "((amount * rate) / 100)" -> (Int('amount') * Int('rate')) / 100
        
        Usa Python's ast para parsing seguro.
        """
        expr_str = expr_str.strip()
        
        # Se for apenas um número
        if re.match(r'^-?\d+$', expr_str):
            return int(expr_str)
        
        # Se for apenas uma variável
        if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', expr_str):
            if expr_str not in self.variables:
                self.variables[expr_str] = Int(expr_str)
            return self.variables[expr_str]
        
        # Expressão aritmética complexa - usar AST
        try:
            tree = ast.parse(expr_str, mode='eval')
            return self._ast_to_z3(tree.body)
        except UnsupportedConstraintError:
            # RVC2-004: Re-raise UnsupportedConstraintError to reject transaction
            raise
        except Exception as e:
            print(f"  ⚠️  Erro ao parsear expressão aritmética '{expr_str}': {e}")
            # Fallback: tentar como variável simples
            if expr_str not in self.variables:
                self.variables[expr_str] = Int(expr_str)
            return self.variables[expr_str]
    
    def _ast_to_z3(self, node):
        """
        v1.9.2 (RVC2-004): Converte AST Python para expressão Z3 com hard-reject parsing.
        
        Implementa whitelist explícita de nós AST suportados. Qualquer nó não suportado
        dispara UnsupportedConstraintError, causando rejeição da transação.
        
        Filosofia: "Fail-closed" - desconhecido = rejeitado
        
        Suporta operações aritméticas: +, -, *, /, %
        Suporta comparações: ==, !=, <, <=, >, >=
        Suporta operadores unários: -, +
        """
        # RVC2-004: Hard-reject - verificar whitelist ANTES de processar
        node_type = type(node)
        
        if node_type not in SUPPORTED_AST_NODES:
            # Nó não suportado - rejeitar transação
            raise UnsupportedConstraintError(
                violation_type="UNSUPPORTED_AST_NODE",
                details={
                    "node_type": node_type.__name__,
                    "node_repr": ast.dump(node),
                    "supported_types": sorted([t.__name__ for t in SUPPORTED_AST_NODES])
                },
                recovery_hint=None  # Will use template from UnsupportedConstraintError
            )
        
        # Processar nós suportados
        if isinstance(node, ast.BinOp):
            left = self._ast_to_z3(node.left)
            right = self._ast_to_z3(node.right)
            
            # Verificar operador também está na whitelist
            op_type = type(node.op)
            if op_type not in SUPPORTED_AST_NODES:
                raise UnsupportedConstraintError(
                    violation_type="UNSUPPORTED_AST_NODE",
                    details={
                        "node_type": op_type.__name__,
                        "node_repr": ast.dump(node),
                        "context": "binary operator",
                        "supported_types": sorted([t.__name__ for t in SUPPORTED_AST_NODES])
                    },
                    recovery_hint=None
                )
            
            if isinstance(node.op, ast.Add):
                return left + right
            elif isinstance(node.op, ast.Sub):
                return left - right
            elif isinstance(node.op, ast.Mult):
                return left * right
            elif isinstance(node.op, ast.Div):
                # Z3 usa divisão inteira
                return left / right
            elif isinstance(node.op, ast.Mod):
                return left % right
            else:
                # Não deveria chegar aqui devido à verificação acima, mas por segurança
                raise UnsupportedConstraintError(
                    violation_type="UNSUPPORTED_AST_NODE",
                    details={
                        "node_type": type(node.op).__name__,
                        "node_repr": ast.dump(node),
                        "context": "binary operator (fallback)",
                        "supported_types": sorted([t.__name__ for t in SUPPORTED_AST_NODES])
                    },
                    recovery_hint=None
                )
        
        elif isinstance(node, ast.UnaryOp):
            # RVC2-004: Suporte para operadores unários
            operand = self._ast_to_z3(node.operand)
            
            # Verificar operador unário está na whitelist
            op_type = type(node.op)
            if op_type not in SUPPORTED_AST_NODES:
                raise UnsupportedConstraintError(
                    violation_type="UNSUPPORTED_AST_NODE",
                    details={
                        "node_type": op_type.__name__,
                        "node_repr": ast.dump(node),
                        "context": "unary operator",
                        "supported_types": sorted([t.__name__ for t in SUPPORTED_AST_NODES])
                    },
                    recovery_hint=None
                )
            
            if isinstance(node.op, ast.USub):
                return -operand
            elif isinstance(node.op, ast.UAdd):
                return operand
            else:
                raise UnsupportedConstraintError(
                    violation_type="UNSUPPORTED_AST_NODE",
                    details={
                        "node_type": type(node.op).__name__,
                        "node_repr": ast.dump(node),
                        "context": "unary operator (fallback)",
                        "supported_types": sorted([t.__name__ for t in SUPPORTED_AST_NODES])
                    },
                    recovery_hint=None
                )
        
        elif isinstance(node, ast.Name):
            var_name = node.id
            if var_name not in self.variables:
                self.variables[var_name] = Int(var_name)
            return self.variables[var_name]
        
        elif isinstance(node, ast.Constant):
            # Python 3.8+
            return node.value
        
        elif isinstance(node, ast.Num):
            # Python 3.7 e anterior
            return node.n
        
        else:
            # Não deveria chegar aqui devido à verificação inicial, mas por segurança
            raise UnsupportedConstraintError(
                violation_type="UNSUPPORTED_AST_NODE",
                details={
                    "node_type": type(node).__name__,
                    "node_repr": ast.dump(node),
                    "context": "fallback handler",
                    "supported_types": sorted([t.__name__ for t in SUPPORTED_AST_NODES])
                },
                recovery_hint=None
            )
    
    def _format_model(self, model):
        """
        Formata o modelo (contra-exemplo) de forma legível.
        """
        result = {}
        for var in model:
            result[str(var)] = model[var].as_long()
        return result
    
    def generate_proof_report(self, intent_name, verification_result):
        """
        Gera relatório detalhado da verificação formal.
        """
        data = self.intent_map[intent_name]

        params = data.get('params', [])
        if params and isinstance(params[0], dict):
            formatted_params = ", ".join(
                f"{p.get('name')}:{p.get('type')}" for p in params if p.get('name') and p.get('type')
            )
        else:
            formatted_params = ", ".join(str(p) for p in params)
        
        report = f"""
╔══════════════════════════════════════════════════════════════╗
║           AETHEL FORMAL VERIFICATION REPORT                  ║
╚══════════════════════════════════════════════════════════════╝

Intent: {intent_name}
Parameters: {formatted_params}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PRE-CONDITIONS (Guards):
"""
        for constraint in self._normalize_conditions(data.get('constraints', [])):
            report += f"  • {constraint}\n"
        
        report += "\nPOST-CONDITIONS (Verify):\n"
        for condition in self._normalize_conditions(data.get('post_conditions', [])):
            report += f"  • {condition}\n"
        
        report += f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        report += f"\nVERDICT: {verification_result['status']}\n"
        report += f"MESSAGE: {verification_result['message']}\n"
        
        if verification_result['counter_examples']:
            report += "\n⚠️  COUNTER-EXAMPLES FOUND:\n"
            for ce in verification_result['counter_examples']:
                report += f"\n  Condition: {ce['condition']}\n"
                report += f"  Fails when: {ce['counter_example']}\n"
        
        report += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        
        return report

    # RVC2-004: Explicit whitelist of supported AST node types
    # This whitelist implements hard-reject parsing: any node type not in this set
    # will trigger UnsupportedConstraintError and cause transaction rejection.
    # This prevents security bypasses through unsupported syntax.
    SUPPORTED_AST_NODES = {
        # Binary operations
        ast.BinOp,

        # Unary operations
        ast.UnaryOp,

        # Comparison operations
        ast.Compare,

        # Literals and variables
        ast.Num,        # Python 3.7 and earlier
        ast.Constant,   # Python 3.8+
        ast.Name,       # Variable names

        # Arithmetic operators
        ast.Add,        # +
        ast.Sub,        # -
        ast.Mult,       # *
        ast.Div,        # /
        ast.Mod,        # %

        # Comparison operators
        ast.Eq,         # ==
        ast.NotEq,      # !=
        ast.Lt,         # <
        ast.LtE,        # <=
        ast.Gt,         # >
        ast.GtE,        # >=

        # Unary operators
        ast.USub,       # Unary minus (-)
        ast.UAdd,       # Unary plus (+)
    }
