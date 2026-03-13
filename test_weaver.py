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

from diotec360_kernel import Diotec360Kernel
from diotec360_weaver import Diotec360Weaver


print("╔══════════════════════════════════════════════════════════════╗")
print("║   DIOTEC360 WEAVER v0.6 - COMPILADOR POLIMÓRFICO E SENSÍVEL    ║")
print("╚══════════════════════════════════════════════════════════════╝\n")

# Criar kernel e compilar uma função
kernel = Diotec360Kernel(ai_provider="anthropic", vault_path=".diotec360_vault")

code = """
intent secure_transfer(sender: Account, receiver: Account, amount: Gold) {
    guard {
        sender_balance >= amount;
        amount > 0;
        amount <= 10000;
    }
    solve {
        priority: security;
        target: blockchain;
    }
    verify {
        sender_balance < old_balance;
        receiver_balance > old_receiver_balance;
    }
}
"""

print("="*70)
print("PASSO 1: Compilar e armazenar função no cofre")
print("="*70)

result = kernel.compile(code, max_attempts=3)

if result['status'] != 'SUCCESS':
    print(f"❌ Compilação falhou: {result['message']}")
    exit(1)

function_hash = result['vault_hash']
print(f"\n✅ Função compilada e armazenada: {function_hash[:16]}...")

# Criar o Weaver
print("\n" + "="*70)
print("PASSO 2: Inicializar o Weaver")
print("="*70)

weaver = Diotec360Weaver(kernel.vault)

# Testar diferentes cenários de execução
print("\n" + "="*70)
print("PASSO 3: Testar estratégias de execução")
print("="*70)

# Cenário 1: Execução padrão (ambiente atual)
print("\n🧪 CENÁRIO 1: Ambiente atual (real)")
strategy1 = weaver.weave_execution(function_hash)

# Cenário 2: Simular bateria baixa
print("\n🧪 CENÁRIO 2: Simulação - Bateria baixa")
print("   (Modificando temporariamente as métricas para demonstração)")

# Obter ambiente real
env = weaver.probe_environment()

# Simular bateria baixa
env['battery'] = {'present': True, 'percent': 15, 'plugged': False, 'time_left_minutes': 30}
mode = weaver.determine_execution_mode(env)
print(f"\n   Modo determinado: {mode.value.upper()}")

# Cenário 3: Simular CPU livre + GPU
print("\n🧪 CENÁRIO 3: Simulação - CPU livre + GPU disponível")
env['cpu_load'] = 20
env['has_gpu'] = {'available': True, 'count': 1, 'name': 'NVIDIA RTX 4090', 'memory_free_gb': 20, 'load': 10}
mode = weaver.determine_execution_mode(env)
print(f"\n   Modo determinado: {mode.value.upper()}")

# Estimar pegada de carbono
print("\n" + "="*70)
print("PASSO 4: Estimativa de Pegada de Carbono")
print("="*70)

# Estimar para diferentes modos
runtime_seconds = 60  # 1 minuto de execução

print(f"\n🌍 Estimativas para {runtime_seconds}s de execução:\n")

from diotec360_weaver import ExecutionMode

for mode in ExecutionMode:
    test_strategy = {
        'mode': mode.value,
        'runtime_config': {'enable_gpu': mode == ExecutionMode.ULTRA_PERFORMANCE}
    }
    
    carbon = weaver.estimate_carbon_footprint(test_strategy, runtime_seconds)
    
    print(f"   {mode.value.upper()}:")
    print(f"      Consumo: {carbon['power_consumption_watts']} W")
    print(f"      Energia: {carbon['energy_kwh']:.6f} kWh")
    print(f"      CO2: {carbon['co2_grams']:.2f} g")
    print()

# Gerar relatório completo
print("="*70)
print("PASSO 5: Relatório Completo do Weaver")
print("="*70)

carbon_estimate = weaver.estimate_carbon_footprint(strategy1, 60)
report = weaver.generate_weaver_report(function_hash, strategy1, carbon_estimate)
print(report)

# Demonstrar adaptação em tempo real
print("="*70)
print("PASSO 6: Demonstração de Adaptação em Tempo Real")
print("="*70)

print("\n🔄 O Weaver adapta a execução ao contexto:")
print("\n   Cenário A: Laptop desconectado, bateria 15%")
print("   → Modo ECONOMY: 1-2 threads, sem SIMD, cache mínimo")
print("\n   Cenário B: Workstation conectada, CPU livre, GPU disponível")
print("   → Modo ULTRA_PERFORMANCE: todos os threads, GPU, cache máximo")
print("\n   Cenário C: Servidor em produção, carga média")
print("   → Modo BALANCED: threads moderados, otimizações padrão")

print("\n✅ O mesmo código Diotec360 se adapta automaticamente!")

print("\n" + "="*70)
print("🎉 TESTE DO WEAVER CONCLUÍDO")
print("="*70)

print("\n📊 RESUMO:")
print("   ✓ Detecção de hardware em tempo real")
print("   ✓ Seleção automática de modo de execução")
print("   ✓ Otimizações específicas por contexto")
print("   ✓ Estimativa de pegada de carbono")
print("   ✓ Adaptação dinâmica ao ambiente")
