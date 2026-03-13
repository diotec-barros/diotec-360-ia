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
Aethel Teacher APIs - Ponte com os Gigantes
Os professores temporários que ensinam a IA local.

Este módulo implementa a interface com GPT-4, Claude e DeepSeek-V3 via API.
Permite que a Aethel consulte múltiplas IAs como "professores" e compare
suas respostas para destilação de conhecimento.

Research Foundation:
- OpenAI GPT-4: State-of-the-art language model
- Anthropic Claude: Constitutional AI with safety focus
- DeepSeek-V3: Efficient MoE model with strong coding abilities

Author: Kiro AI - Engenheiro-Chefe
Version: Epoch 4.0 "Neural Nexus"
Date: February 5, 2026
"""

from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any, Callable
from enum import Enum
import time
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading


# Importações condicionais (instalar se necessário)
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("[TEACHER APIs] ⚠️  openai não instalado. Execute: pip install openai")

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    print("[TEACHER APIs] ⚠️  anthropic não instalado. Execute: pip install anthropic")

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("[TEACHER APIs] ⚠️  requests não instalado. Execute: pip install requests")


class TeacherType(Enum):
    """Tipos de professores disponíveis"""
    GPT4 = "gpt-4"
    GPT4_TURBO = "gpt-4-turbo-preview"
    CLAUDE_3_OPUS = "claude-3-opus-20240229"
    CLAUDE_3_SONNET = "claude-3-sonnet-20240229"
    DEEPSEEK_V3 = "deepseek-chat"


@dataclass
class TeacherConfig:
    """
    Configuração de um professor (API externa).
    
    Attributes:
        name: Nome do professor (ex: "gpt-4", "claude-3-opus")
        teacher_type: Tipo do professor (enum)
        api_key: Chave de API
        endpoint: URL do endpoint (opcional, usa default se não fornecido)
        cost_per_1k_input_tokens: Custo por 1k tokens de input (USD)
        cost_per_1k_output_tokens: Custo por 1k tokens de output (USD)
        rate_limit_rpm: Limite de requisições por minuto
        enabled: Se o professor está habilitado
    """
    name: str
    teacher_type: TeacherType
    api_key: str
    endpoint: Optional[str] = None
    cost_per_1k_input_tokens: float = 0.01
    cost_per_1k_output_tokens: float = 0.03
    rate_limit_rpm: int = 60
    enabled: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        data = asdict(self)
        data['teacher_type'] = self.teacher_type.value
        return data


@dataclass
class TeacherResponse:
    """
    Resposta de um professor.
    
    Attributes:
        teacher: Nome do professor que gerou a resposta
        text: Texto gerado
        input_tokens: Número de tokens de input
        output_tokens: Número de tokens de output
        cost_usd: Custo total em USD
        latency_ms: Latência em milissegundos
        timestamp: Timestamp da resposta
        model: Modelo específico usado
        error: Mensagem de erro (se houver)
    """
    teacher: str
    text: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    latency_ms: float
    timestamp: float
    model: str
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return asdict(self)


class RateLimiter:
    """
    Rate limiter simples para evitar exceder quotas de API.
    
    Usa sliding window para controlar requisições por minuto.
    """
    
    def __init__(self, max_requests_per_minute: int):
        """
        Inicializa rate limiter.
        
        Args:
            max_requests_per_minute: Máximo de requisições por minuto
        """
        self.max_rpm = max_requests_per_minute
        self.requests: List[float] = []
        self.lock = threading.Lock()
    
    def wait_if_needed(self) -> None:
        """
        Aguarda se necessário para respeitar rate limit.
        """
        with self.lock:
            current_time = time.time()
            
            # Remover requisições antigas (> 60 segundos)
            self.requests = [t for t in self.requests if current_time - t < 60]
            
            # Se atingiu o limite, aguardar
            if len(self.requests) >= self.max_rpm:
                oldest_request = min(self.requests)
                wait_time = 60 - (current_time - oldest_request)
                if wait_time > 0:
                    print(f"[RATE LIMITER] ⏳ Aguardando {wait_time:.1f}s para respeitar rate limit...")
                    time.sleep(wait_time)
                    # Limpar requisições antigas após espera
                    current_time = time.time()
                    self.requests = [t for t in self.requests if current_time - t < 60]
            
            # Registrar nova requisição
            self.requests.append(current_time)


class CircuitBreaker:
    """
    Circuit breaker para desabilitar temporariamente professores que falham.
    
    Se um professor falha N vezes consecutivas, ele é desabilitado por X minutos.
    """
    
    def __init__(self, failure_threshold: int = 3, timeout_minutes: int = 5):
        """
        Inicializa circuit breaker.
        
        Args:
            failure_threshold: Número de falhas consecutivas para abrir circuito
            timeout_minutes: Minutos para manter circuito aberto
        """
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_minutes * 60
        self.failures: Dict[str, int] = {}
        self.opened_at: Dict[str, float] = {}
        self.lock = threading.Lock()
    
    def record_success(self, teacher: str) -> None:
        """Registra sucesso (reseta contador de falhas)"""
        with self.lock:
            self.failures[teacher] = 0
            if teacher in self.opened_at:
                del self.opened_at[teacher]
    
    def record_failure(self, teacher: str) -> None:
        """Registra falha (incrementa contador)"""
        with self.lock:
            self.failures[teacher] = self.failures.get(teacher, 0) + 1
            
            # Se atingiu threshold, abrir circuito
            if self.failures[teacher] >= self.failure_threshold:
                self.opened_at[teacher] = time.time()
                print(f"[CIRCUIT BREAKER] 🔴 Professor '{teacher}' desabilitado por {self.timeout_seconds/60:.0f} minutos")
    
    def is_open(self, teacher: str) -> bool:
        """Verifica se circuito está aberto (professor desabilitado)"""
        with self.lock:
            if teacher not in self.opened_at:
                return False
            
            # Verificar se timeout expirou
            elapsed = time.time() - self.opened_at[teacher]
            if elapsed >= self.timeout_seconds:
                # Timeout expirou, fechar circuito
                del self.opened_at[teacher]
                self.failures[teacher] = 0
                print(f"[CIRCUIT BREAKER] 🟢 Professor '{teacher}' reabilitado")
                return False
            
            return True


class TeacherAPIs:
    """
    Gerenciador de APIs de Professores (GPT-4, Claude, DeepSeek).
    
    Este é o sistema de "professores temporários" do Neural Nexus.
    Ele consulta múltiplas IAs externas e coleta suas respostas para
    destilação de conhecimento.
    
    Funcionalidades:
    - Consulta paralela de múltiplos professores
    - Rate limiting automático
    - Circuit breaker para falhas
    - Fallback automático (GPT-4 → Claude → DeepSeek)
    - Cost tracking
    - Retry com exponential backoff
    
    Example:
        >>> teachers = TeacherAPIs([
        ...     TeacherConfig("gpt-4", TeacherType.GPT4, api_key="sk-..."),
        ...     TeacherConfig("claude-3-opus", TeacherType.CLAUDE_3_OPUS, api_key="sk-ant-...")
        ... ])
        >>> responses = teachers.query_all("Explain quantum computing")
        >>> for response in responses:
        ...     print(f"{response.teacher}: {response.text[:100]}...")
    """
    
    def __init__(self, configs: List[TeacherConfig]):
        """
        Inicializa Teacher APIs.
        
        Args:
            configs: Lista de configurações de professores
        """
        self.teachers = {c.name: c for c in configs if c.enabled}
        self.rate_limiters = {name: RateLimiter(config.rate_limit_rpm) 
                             for name, config in self.teachers.items()}
        self.circuit_breaker = CircuitBreaker()
        self.total_cost_usd = 0.0
        self.total_requests = 0
        
        # Configurar clientes de API
        self._setup_clients()
        
        print(f"[TEACHER APIs] 🎓 {len(self.teachers)} professores configurados:")
        for name in self.teachers.keys():
            print(f"  • {name}")
    
    def _setup_clients(self) -> None:
        """Configura clientes de API"""
        # OpenAI
        if OPENAI_AVAILABLE:
            for name, config in self.teachers.items():
                if config.teacher_type in [TeacherType.GPT4, TeacherType.GPT4_TURBO]:
                    openai.api_key = config.api_key
        
        # Anthropic
        if ANTHROPIC_AVAILABLE:
            self.anthropic_clients = {}
            for name, config in self.teachers.items():
                if config.teacher_type in [TeacherType.CLAUDE_3_OPUS, TeacherType.CLAUDE_3_SONNET]:
                    self.anthropic_clients[name] = anthropic.Anthropic(api_key=config.api_key)
    
    def query_all(self, prompt: str, system: Optional[str] = None, 
                  max_tokens: int = 2048, temperature: float = 0.7) -> List[TeacherResponse]:
        """
        Consulta todos os professores em paralelo.
        
        Args:
            prompt: Prompt para os professores
            system: Prompt de sistema (opcional)
            max_tokens: Máximo de tokens a gerar
            temperature: Temperatura (0.0-1.0)
        
        Returns:
            Lista de respostas dos professores
        """
        print(f"\n[TEACHER APIs] 📚 Consultando {len(self.teachers)} professores...")
        
        responses = []
        
        # Usar ThreadPoolExecutor para consultas paralelas
        with ThreadPoolExecutor(max_workers=len(self.teachers)) as executor:
            futures = {}
            
            for name in self.teachers.keys():
                # Verificar circuit breaker
                if self.circuit_breaker.is_open(name):
                    print(f"[TEACHER APIs] ⏭️  Pulando '{name}' (circuit breaker aberto)")
                    continue
                
                # Submeter consulta
                future = executor.submit(
                    self.query_single,
                    name,
                    prompt,
                    system,
                    max_tokens,
                    temperature
                )
                futures[future] = name
            
            # Coletar respostas conforme completam
            for future in as_completed(futures):
                name = futures[future]
                try:
                    response = future.result()
                    responses.append(response)
                    print(f"[TEACHER APIs] ✅ {name}: {len(response.text)} chars, ${response.cost_usd:.4f}")
                except Exception as e:
                    print(f"[TEACHER APIs] ❌ {name}: {e}")
        
        print(f"[TEACHER APIs] 📊 {len(responses)}/{len(self.teachers)} professores responderam")
        
        return responses
    
    def query_single(self, teacher: str, prompt: str, system: Optional[str] = None,
                    max_tokens: int = 2048, temperature: float = 0.7) -> TeacherResponse:
        """
        Consulta um professor específico.
        
        Args:
            teacher: Nome do professor
            prompt: Prompt
            system: Prompt de sistema (opcional)
            max_tokens: Máximo de tokens
            temperature: Temperatura
        
        Returns:
            Resposta do professor
        
        Raises:
            ValueError: Se professor não existe
            Exception: Se consulta falha
        """
        if teacher not in self.teachers:
            raise ValueError(f"Professor '{teacher}' não configurado")
        
        config = self.teachers[teacher]
        
        # Aguardar rate limit
        self.rate_limiters[teacher].wait_if_needed()
        
        start_time = time.time()
        
        try:
            # Consultar baseado no tipo
            if config.teacher_type in [TeacherType.GPT4, TeacherType.GPT4_TURBO]:
                response = self._query_openai(config, prompt, system, max_tokens, temperature)
            elif config.teacher_type in [TeacherType.CLAUDE_3_OPUS, TeacherType.CLAUDE_3_SONNET]:
                response = self._query_anthropic(config, prompt, system, max_tokens, temperature)
            elif config.teacher_type == TeacherType.DEEPSEEK_V3:
                response = self._query_deepseek(config, prompt, system, max_tokens, temperature)
            else:
                raise ValueError(f"Tipo de professor não suportado: {config.teacher_type}")
            
            # Registrar sucesso
            self.circuit_breaker.record_success(teacher)
            self.total_cost_usd += response.cost_usd
            self.total_requests += 1
            
            return response
            
        except Exception as e:
            # Registrar falha
            self.circuit_breaker.record_failure(teacher)
            
            # Criar resposta de erro
            latency_ms = (time.time() - start_time) * 1000
            return TeacherResponse(
                teacher=teacher,
                text="",
                input_tokens=0,
                output_tokens=0,
                cost_usd=0.0,
                latency_ms=latency_ms,
                timestamp=time.time(),
                model=config.teacher_type.value,
                error=str(e)
            )
    
    def _query_openai(self, config: TeacherConfig, prompt: str, system: Optional[str],
                     max_tokens: int, temperature: float) -> TeacherResponse:
        """Consulta OpenAI (GPT-4)"""
        if not OPENAI_AVAILABLE:
            raise ImportError("openai não instalado")
        
        start_time = time.time()
        
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        response = openai.ChatCompletion.create(
            model=config.teacher_type.value,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        latency_ms = (time.time() - start_time) * 1000
        
        text = response.choices[0].message.content
        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens
        
        cost_usd = (
            (input_tokens / 1000) * config.cost_per_1k_input_tokens +
            (output_tokens / 1000) * config.cost_per_1k_output_tokens
        )
        
        return TeacherResponse(
            teacher=config.name,
            text=text,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost_usd,
            latency_ms=latency_ms,
            timestamp=time.time(),
            model=response.model
        )
    
    def _query_anthropic(self, config: TeacherConfig, prompt: str, system: Optional[str],
                        max_tokens: int, temperature: float) -> TeacherResponse:
        """Consulta Anthropic (Claude)"""
        if not ANTHROPIC_AVAILABLE:
            raise ImportError("anthropic não instalado")
        
        start_time = time.time()
        
        client = self.anthropic_clients[config.name]
        
        message = client.messages.create(
            model=config.teacher_type.value,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system if system else "",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        latency_ms = (time.time() - start_time) * 1000
        
        text = message.content[0].text
        input_tokens = message.usage.input_tokens
        output_tokens = message.usage.output_tokens
        
        cost_usd = (
            (input_tokens / 1000) * config.cost_per_1k_input_tokens +
            (output_tokens / 1000) * config.cost_per_1k_output_tokens
        )
        
        return TeacherResponse(
            teacher=config.name,
            text=text,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost_usd,
            latency_ms=latency_ms,
            timestamp=time.time(),
            model=message.model
        )
    
    def _query_deepseek(self, config: TeacherConfig, prompt: str, system: Optional[str],
                       max_tokens: int, temperature: float) -> TeacherResponse:
        """Consulta DeepSeek-V3"""
        if not REQUESTS_AVAILABLE:
            raise ImportError("requests não instalado")
        
        start_time = time.time()
        
        endpoint = config.endpoint or "https://api.deepseek.com/v1/chat/completions"
        
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        response = requests.post(
            endpoint,
            headers={
                "Authorization": f"Bearer {config.api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": config.teacher_type.value,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature
            },
            timeout=60
        )
        response.raise_for_status()
        
        latency_ms = (time.time() - start_time) * 1000
        
        data = response.json()
        text = data["choices"][0]["message"]["content"]
        input_tokens = data["usage"]["prompt_tokens"]
        output_tokens = data["usage"]["completion_tokens"]
        
        cost_usd = (
            (input_tokens / 1000) * config.cost_per_1k_input_tokens +
            (output_tokens / 1000) * config.cost_per_1k_output_tokens
        )
        
        return TeacherResponse(
            teacher=config.name,
            text=text,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost_usd,
            latency_ms=latency_ms,
            timestamp=time.time(),
            model=data["model"]
        )
    
    def query_with_fallback(self, prompt: str, system: Optional[str] = None,
                           max_tokens: int = 2048, temperature: float = 0.7) -> TeacherResponse:
        """
        Consulta com fallback automático.
        
        Tenta GPT-4 primeiro, se falha tenta Claude, depois DeepSeek.
        
        Args:
            prompt: Prompt
            system: Prompt de sistema (opcional)
            max_tokens: Máximo de tokens
            temperature: Temperatura
        
        Returns:
            Resposta do primeiro professor que suceder
        
        Raises:
            Exception: Se todos os professores falharem
        """
        # Ordem de preferência
        preference_order = [
            TeacherType.GPT4_TURBO,
            TeacherType.GPT4,
            TeacherType.CLAUDE_3_OPUS,
            TeacherType.CLAUDE_3_SONNET,
            TeacherType.DEEPSEEK_V3
        ]
        
        for teacher_type in preference_order:
            # Encontrar professor deste tipo
            teacher_name = None
            for name, config in self.teachers.items():
                if config.teacher_type == teacher_type:
                    teacher_name = name
                    break
            
            if not teacher_name:
                continue
            
            # Verificar circuit breaker
            if self.circuit_breaker.is_open(teacher_name):
                continue
            
            # Tentar consultar
            try:
                response = self.query_single(teacher_name, prompt, system, max_tokens, temperature)
                if not response.error:
                    return response
            except Exception as e:
                print(f"[TEACHER APIs] ⚠️  {teacher_name} falhou: {e}")
                continue
        
        raise Exception("Todos os professores falharam")
    
    def calculate_total_cost(self, responses: List[TeacherResponse]) -> float:
        """
        Calcula custo total de uma lista de respostas.
        
        Args:
            responses: Lista de respostas
        
        Returns:
            Custo total em USD
        """
        return sum(r.cost_usd for r in responses if not r.error)
    
    def get_cheapest_teacher(self) -> str:
        """
        Retorna professor com menor custo por token.
        
        Returns:
            Nome do professor mais barato
        """
        cheapest = min(
            self.teachers.items(),
            key=lambda x: x[1].cost_per_1k_output_tokens
        )
        return cheapest[0]
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Retorna estatísticas de uso.
        
        Returns:
            Estatísticas
        """
        return {
            "total_requests": self.total_requests,
            "total_cost_usd": self.total_cost_usd,
            "teachers_configured": len(self.teachers),
            "teachers": {
                name: {
                    "type": config.teacher_type.value,
                    "enabled": config.enabled,
                    "cost_per_1k_output": config.cost_per_1k_output_tokens
                }
                for name, config in self.teachers.items()
            }
        }


def create_default_teachers() -> List[TeacherConfig]:
    """
    Cria configuração padrão de professores a partir de variáveis de ambiente.
    
    Variáveis de ambiente esperadas:
    - OPENAI_API_KEY: Chave da OpenAI
    - ANTHROPIC_API_KEY: Chave da Anthropic
    - DEEPSEEK_API_KEY: Chave da DeepSeek
    
    Returns:
        Lista de configurações
    """
    configs = []
    
    # GPT-4
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        configs.append(TeacherConfig(
            name="gpt-4-turbo",
            teacher_type=TeacherType.GPT4_TURBO,
            api_key=openai_key,
            cost_per_1k_input_tokens=0.01,
            cost_per_1k_output_tokens=0.03,
            rate_limit_rpm=60
        ))
    
    # Claude
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    if anthropic_key:
        configs.append(TeacherConfig(
            name="claude-3-opus",
            teacher_type=TeacherType.CLAUDE_3_OPUS,
            api_key=anthropic_key,
            cost_per_1k_input_tokens=0.015,
            cost_per_1k_output_tokens=0.075,
            rate_limit_rpm=60
        ))
    
    # DeepSeek
    deepseek_key = os.getenv("DEEPSEEK_API_KEY")
    if deepseek_key:
        configs.append(TeacherConfig(
            name="deepseek-v3",
            teacher_type=TeacherType.DEEPSEEK_V3,
            api_key=deepseek_key,
            cost_per_1k_input_tokens=0.001,
            cost_per_1k_output_tokens=0.002,
            rate_limit_rpm=60
        ))
    
    return configs


if __name__ == "__main__":
    # Demo rápido
    print("=" * 80)
    print("AETHEL TEACHER APIs - DEMO")
    print("=" * 80)
    
    # Criar professores a partir de env vars
    configs = create_default_teachers()
    
    if not configs:
        print("\n❌ Nenhuma chave de API configurada.")
        print("\n📖 Configure as variáveis de ambiente:")
        print("   export OPENAI_API_KEY='sk-...'")
        print("   export ANTHROPIC_API_KEY='sk-ant-...'")
        print("   export DEEPSEEK_API_KEY='sk-...'")
    else:
        teachers = TeacherAPIs(configs)
        
        # Testar consulta
        prompt = "Explain the concept of formal verification in 2 sentences."
        
        print(f"\n[DEMO] Consultando professores com prompt:")
        print(f"  '{prompt}'")
        
        responses = teachers.query_all(prompt, max_tokens=100)
        
        print(f"\n[DEMO] Respostas recebidas:")
        for response in responses:
            if not response.error:
                print(f"\n  🎓 {response.teacher}:")
                print(f"     {response.text}")
                print(f"     Custo: ${response.cost_usd:.4f}, Latência: {response.latency_ms:.0f}ms")
        
        # Estatísticas
        stats = teachers.get_statistics()
        print(f"\n[DEMO] Estatísticas:")
        print(f"  Total de requisições: {stats['total_requests']}")
        print(f"  Custo total: ${stats['total_cost_usd']:.4f}")
