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

import psutil
import platform
from datetime import datetime
from enum import Enum


class ExecutionMode(Enum):
    """Modos de execução disponíveis"""
    ULTRA_PERFORMANCE = "ultra_performance"
    PERFORMANCE = "performance"
    BALANCED = "balanced"
    ECONOMY = "economy"
    CRITICAL_BATTERY = "critical_battery"


class AethelWeaver:
    """
    O Tecelão - Compilador Polimórfico e Sensível ao Contexto.
    
    Adapta a execução do código ao estado do hardware em tempo real:
    - Bateria baixa → Modo econômico
    - CPU livre → Paralelização máxima
    - GPU disponível → Aceleração CUDA
    - Rede lenta → Execução local
    """
    
    def __init__(self, vault):
        self.vault = vault
        self.carbon_budget = None  # Orçamento de carbono (opcional)
        
        print("🧵 Weaver inicializado - Compilador Polimórfico ativo")
    
    def probe_environment(self):
        """
        Detecta o 'clima' do sistema em tempo real.
        
        Retorna métricas de hardware, energia e recursos disponíveis.
        """
        stats = {
            'timestamp': datetime.now().isoformat(),
            'os': platform.system(),
            'architecture': platform.machine(),
            'cpu_count': psutil.cpu_count(logical=False),
            'cpu_threads': psutil.cpu_count(logical=True),
            'cpu_load': psutil.cpu_percent(interval=0.1),
            'memory_available_gb': psutil.virtual_memory().available / (1024**3),
            'memory_percent': psutil.virtual_memory().percent,
            'has_gpu': self._detect_gpu(),
            'battery': self._get_battery_info(),
            'disk_io': psutil.disk_io_counters() if hasattr(psutil, 'disk_io_counters') else None,
            'network_io': psutil.net_io_counters() if hasattr(psutil, 'net_io_counters') else None
        }
        
        return stats
    
    def _detect_gpu(self):
        """
        Detecta se há GPU disponível.
        """
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            if gpus:
                return {
                    'available': True,
                    'count': len(gpus),
                    'name': gpus[0].name if gpus else None,
                    'memory_free_gb': gpus[0].memoryFree / 1024 if gpus else 0,
                    'load': gpus[0].load * 100 if gpus else 0
                }
        except ImportError:
            pass
        
        return {'available': False}
    
    def _get_battery_info(self):
        """
        Obtém informações da bateria (se disponível).
        """
        battery = psutil.sensors_battery()
        
        if battery:
            return {
                'present': True,
                'percent': battery.percent,
                'plugged': battery.power_plugged,
                'time_left_minutes': battery.secsleft / 60 if battery.secsleft > 0 else None
            }
        
        return {'present': False, 'percent': 100, 'plugged': True}
    
    def determine_execution_mode(self, env_stats):
        """
        Decide o modo de execução baseado no ambiente.
        
        Estratégia de decisão:
        1. Bateria crítica → CRITICAL_BATTERY
        2. Bateria baixa → ECONOMY
        3. CPU livre + GPU → ULTRA_PERFORMANCE
        4. CPU livre → PERFORMANCE
        5. Padrão → BALANCED
        """
        battery = env_stats['battery']
        cpu_load = env_stats['cpu_load']
        has_gpu = env_stats['has_gpu']['available']
        
        # Bateria crítica
        if battery['present'] and not battery['plugged'] and battery['percent'] < 10:
            return ExecutionMode.CRITICAL_BATTERY
        
        # Modo econômico
        if battery['present'] and not battery['plugged'] and battery['percent'] < 20:
            return ExecutionMode.ECONOMY
        
        # Ultra performance (GPU + CPU livre)
        if has_gpu and cpu_load < 30:
            return ExecutionMode.ULTRA_PERFORMANCE
        
        # Performance (CPU livre)
        if cpu_load < 50:
            return ExecutionMode.PERFORMANCE
        
        # Balanceado (padrão)
        return ExecutionMode.BALANCED
    
    def weave_execution(self, function_hash, context=None):
        """
        A decisão suprema: como rodar essa lógica?
        
        Retorna estratégia de execução otimizada para o contexto atual.
        """
        print(f"\n🧵 Weaver: Analisando ambiente para função {function_hash[:16]}...")
        
        # 1. Probar ambiente
        env = self.probe_environment()
        
        # 2. Buscar artefato no cofre
        artifact = self.vault.fetch(function_hash)
        
        if not artifact:
            raise Exception(f"❌ Função {function_hash} não encontrada no Cofre!")
        
        # 3. Determinar modo de execução
        mode = self.determine_execution_mode(env)
        
        # 4. Gerar estratégia de execução
        strategy = self._generate_execution_strategy(artifact, env, mode, context)
        
        # 5. Exibir decisão
        self._display_weaving_decision(env, mode, strategy)
        
        return strategy
    
    def _generate_execution_strategy(self, artifact, env, mode, context):
        """
        Gera estratégia de execução baseada no modo e ambiente.
        """
        strategy = {
            'function_hash': artifact['full_hash'],
            'intent_name': artifact['intent_name'],
            'mode': mode.value,
            'timestamp': datetime.now().isoformat(),
            'environment': {
                'os': env['os'],
                'cpu_load': env['cpu_load'],
                'battery_percent': env['battery']['percent'],
                'memory_available_gb': env['memory_available_gb']
            },
            'optimizations': [],
            'compilation_flags': [],
            'runtime_config': {}
        }
        
        # Aplicar otimizações baseadas no modo
        if mode == ExecutionMode.CRITICAL_BATTERY:
            strategy['optimizations'] = [
                'disable_parallelism',
                'reduce_memory_footprint',
                'minimize_io',
                'lower_cpu_frequency'
            ]
            strategy['compilation_flags'] = ['-Os', '--optimize-size']
            strategy['runtime_config'] = {
                'max_threads': 1,
                'enable_simd': False,
                'cache_size': 'minimal'
            }
        
        elif mode == ExecutionMode.ECONOMY:
            strategy['optimizations'] = [
                'limit_parallelism',
                'reduce_memory_usage',
                'batch_io_operations'
            ]
            strategy['compilation_flags'] = ['-O2', '--balance-speed-size']
            strategy['runtime_config'] = {
                'max_threads': 2,
                'enable_simd': True,
                'cache_size': 'small'
            }
        
        elif mode == ExecutionMode.BALANCED:
            strategy['optimizations'] = [
                'moderate_parallelism',
                'standard_memory',
                'adaptive_io'
            ]
            strategy['compilation_flags'] = ['-O2', '--optimize-balanced']
            strategy['runtime_config'] = {
                'max_threads': env['cpu_count'],
                'enable_simd': True,
                'cache_size': 'medium'
            }
        
        elif mode == ExecutionMode.PERFORMANCE:
            strategy['optimizations'] = [
                'aggressive_parallelism',
                'prefetch_data',
                'inline_functions',
                'loop_unrolling'
            ]
            strategy['compilation_flags'] = ['-O3', '--optimize-speed']
            strategy['runtime_config'] = {
                'max_threads': env['cpu_threads'],
                'enable_simd': True,
                'cache_size': 'large'
            }
        
        elif mode == ExecutionMode.ULTRA_PERFORMANCE:
            strategy['optimizations'] = [
                'maximum_parallelism',
                'gpu_acceleration',
                'aggressive_prefetch',
                'vectorization',
                'cache_optimization'
            ]
            strategy['compilation_flags'] = ['-O3', '--optimize-aggressive', '--enable-cuda']
            strategy['runtime_config'] = {
                'max_threads': env['cpu_threads'],
                'enable_simd': True,
                'enable_gpu': True,
                'cache_size': 'maximum'
            }
        
        # Adicionar contexto customizado se fornecido
        if context:
            strategy['custom_context'] = context
        
        return strategy
    
    def _display_weaving_decision(self, env, mode, strategy):
        """
        Exibe a decisão do Weaver de forma visual.
        """
        print(f"\n{'='*70}")
        print(f"🧵 WEAVER EXECUTION STRATEGY")
        print(f"{'='*70}")
        
        print(f"\n📊 ENVIRONMENT SNAPSHOT:")
        print(f"   OS: {env['os']} ({env['architecture']})")
        print(f"   CPU: {env['cpu_count']} cores, {env['cpu_threads']} threads ({env['cpu_load']:.1f}% load)")
        print(f"   Memory: {env['memory_available_gb']:.2f} GB available ({env['memory_percent']:.1f}% used)")
        
        battery = env['battery']
        if battery['present']:
            status = "🔌 Plugged" if battery['plugged'] else "🔋 Battery"
            print(f"   Power: {status} ({battery['percent']:.0f}%)")
        
        gpu = env['has_gpu']
        if gpu['available']:
            print(f"   GPU: {gpu['name']} ({gpu['memory_free_gb']:.2f} GB free, {gpu['load']:.1f}% load)")
        
        print(f"\n⚙️  EXECUTION MODE: {mode.value.upper()}")
        
        print(f"\n🎯 OPTIMIZATIONS:")
        for opt in strategy['optimizations']:
            print(f"   ✓ {opt}")
        
        print(f"\n🔧 COMPILATION FLAGS:")
        print(f"   {' '.join(strategy['compilation_flags'])}")
        
        print(f"\n⚡ RUNTIME CONFIG:")
        for key, value in strategy['runtime_config'].items():
            print(f"   {key}: {value}")
        
        print(f"\n{'='*70}")
    
    def estimate_carbon_footprint(self, strategy, estimated_runtime_seconds):
        """
        Estima a pegada de carbono da execução.
        
        Baseado em:
        - Modo de execução
        - Tempo estimado
        - Uso de GPU
        - Região geográfica (grid de energia)
        """
        # Consumo base por modo (Watts)
        power_consumption = {
            ExecutionMode.CRITICAL_BATTERY: 5,
            ExecutionMode.ECONOMY: 15,
            ExecutionMode.BALANCED: 45,
            ExecutionMode.PERFORMANCE: 95,
            ExecutionMode.ULTRA_PERFORMANCE: 250
        }
        
        mode = ExecutionMode(strategy['mode'])
        watts = power_consumption[mode]
        
        # Adicionar GPU se habilitado
        if strategy['runtime_config'].get('enable_gpu'):
            watts += 150  # GPU típica consome ~150W
        
        # Calcular energia (kWh)
        kwh = (watts * estimated_runtime_seconds) / (1000 * 3600)
        
        # Fator de carbono médio global: ~475g CO2/kWh
        carbon_intensity = 475  # g CO2/kWh
        co2_grams = kwh * carbon_intensity
        
        return {
            'estimated_runtime_seconds': estimated_runtime_seconds,
            'power_consumption_watts': watts,
            'energy_kwh': kwh,
            'co2_grams': co2_grams,
            'mode': mode.value
        }
    
    def generate_weaver_report(self, function_hash, strategy, carbon_estimate=None):
        """
        Gera relatório completo da decisão do Weaver.
        """
        artifact = self.vault.fetch(function_hash)
        
        report = f"""
╔══════════════════════════════════════════════════════════════╗
║           AETHEL WEAVER EXECUTION REPORT v0.6                ║
╚══════════════════════════════════════════════════════════════╝

Function: {artifact['intent_name']}
Hash: {function_hash[:16]}...{function_hash[-8:]}
Timestamp: {strategy['timestamp']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

EXECUTION MODE: {strategy['mode'].upper()}

Environment:
  OS: {strategy['environment']['os']}
  CPU Load: {strategy['environment']['cpu_load']:.1f}%
  Battery: {strategy['environment']['battery_percent']:.0f}%
  Memory Available: {strategy['environment']['memory_available_gb']:.2f} GB

Optimizations Applied:
"""
        for opt in strategy['optimizations']:
            report += f"  ✓ {opt}\n"
        
        report += f"\nCompilation Flags:\n  {' '.join(strategy['compilation_flags'])}\n"
        
        if carbon_estimate:
            report += f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            report += f"\n🌍 CARBON FOOTPRINT ESTIMATE:\n"
            report += f"  Power Consumption: {carbon_estimate['power_consumption_watts']} W\n"
            report += f"  Energy: {carbon_estimate['energy_kwh']:.6f} kWh\n"
            report += f"  CO2 Emissions: {carbon_estimate['co2_grams']:.2f} g\n"
        
        report += f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        report += f"\n🧵 Execution strategy optimized for current hardware context\n"
        report += f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        
        return report
