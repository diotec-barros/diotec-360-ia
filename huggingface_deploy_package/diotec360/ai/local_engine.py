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
Aethel Local Engine - Interface com Ollama
O cérebro local que pensa sem internet.

Este módulo implementa a interface com Ollama para execução local de modelos de IA.
Permite que a Aethel execute DeepSeek-Coder, Llama, e outros modelos localmente,
sem dependência de APIs externas.

Research Foundation:
- Ollama: Local LLM runtime (https://ollama.ai)
- DeepSeek-Coder: Efficient coding model (https://github.com/deepseek-ai/DeepSeek-Coder)
- LoRA: Low-Rank Adaptation for efficient fine-tuning

Author: Kiro AI - Engenheiro-Chefe
Version: Epoch 4.0 "Neural Nexus"
Date: February 5, 2026
"""

from dataclasses import dataclass, field, asdict
from typing import List, Optional, Iterator, Dict, Any
import time
import requests
import json
from pathlib import Path


@dataclass
class OllamaModel:
    """
    Representa um modelo de IA disponível no Ollama.
    
    Attributes:
        name: Nome do modelo (ex: "deepseek-coder:7b", "llama3:8b")
        size_gb: Tamanho do modelo em gigabytes
        parameters: Número de parâmetros (ex: 7B, 70B)
        context_length: Tamanho máximo do contexto em tokens
        installed: Se o modelo está instalado localmente
        family: Família do modelo (deepseek, llama, mistral, etc.)
        modified_at: Timestamp da última modificação
    """
    name: str
    size_gb: float = 0.0
    parameters: int = 0
    context_length: int = 4096
    installed: bool = False
    family: str = "unknown"
    modified_at: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return asdict(self)


@dataclass
class LocalInferenceRequest:
    """
    Requisição de inferência local.
    
    Attributes:
        prompt: Texto de entrada para o modelo
        model: Nome do modelo a usar
        temperature: Controla aleatoriedade (0.0 = determinístico, 1.0 = criativo)
        max_tokens: Número máximo de tokens a gerar
        stream: Se deve retornar resposta em streaming
        system: Prompt de sistema (opcional)
        context: Contexto anterior para continuação (opcional)
    """
    prompt: str
    model: str
    temperature: float = 0.7
    max_tokens: int = 2048
    stream: bool = False
    system: Optional[str] = None
    context: Optional[List[int]] = None


@dataclass
class LocalInferenceResponse:
    """
    Resposta de inferência local.
    
    Attributes:
        text: Texto gerado pelo modelo
        model: Nome do modelo usado
        tokens_generated: Número de tokens gerados
        latency_ms: Latência total em milissegundos
        tokens_per_second: Throughput (tokens/segundo)
        context: Contexto para continuação (opcional)
        done: Se a geração está completa
    """
    text: str
    model: str
    tokens_generated: int
    latency_ms: float
    tokens_per_second: float
    context: Optional[List[int]] = None
    done: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return asdict(self)


class OllamaNotAvailableError(Exception):
    """Exceção quando Ollama não está disponível"""
    pass


class ModelNotFoundError(Exception):
    """Exceção quando modelo não está instalado"""
    pass


class LocalEngine:
    """
    Motor de Inteligência Local - Interface com Ollama.
    
    Este é o cérebro local da Aethel. Ele permite executar modelos de IA
    localmente sem dependência de APIs externas. Suporta:
    
    - DeepSeek-Coder (7B, 33B)
    - Llama 3 (8B, 70B)
    - Mistral (7B)
    - CodeLlama (7B, 13B, 34B)
    
    O Local Engine é a base para:
    1. Destilação Autônoma (aprender com GPT-4/Claude)
    2. Inference Sharding (distribuir modelo pela rede P2P)
    3. Offline Intelligence (IA 100% local para empresas)
    
    Example:
        >>> engine = LocalEngine()
        >>> if engine.check_ollama_available():
        ...     models = engine.list_models()
        ...     request = LocalInferenceRequest(
        ...         prompt="Write a function to calculate fibonacci",
        ...         model="deepseek-coder:7b"
        ...     )
        ...     response = engine.generate(request)
        ...     print(response.text)
    """
    
    def __init__(self, ollama_host: str = "http://localhost:11434"):
        """
        Inicializa o Local Engine.
        
        Args:
            ollama_host: URL do servidor Ollama (default: localhost:11434)
        """
        self.ollama_host = ollama_host.rstrip('/')
        self.available_models: List[OllamaModel] = []
        self._cache: Dict[str, Any] = {}
        
        # Tentar detectar Ollama na inicialização
        try:
            self.check_ollama_available()
        except OllamaNotAvailableError:
            print("[LOCAL ENGINE] ⚠️  Ollama não detectado. Instale: https://ollama.ai")
    
    def check_ollama_available(self) -> bool:
        """
        Verifica se Ollama está rodando.
        
        Returns:
            True se Ollama está disponível, False caso contrário
            
        Raises:
            OllamaNotAvailableError: Se Ollama não está disponível
        """
        try:
            response = requests.get(f"{self.ollama_host}/api/tags", timeout=2)
            if response.status_code == 200:
                print("[LOCAL ENGINE] ✅ Ollama detectado e rodando")
                return True
            else:
                raise OllamaNotAvailableError(
                    f"Ollama respondeu com status {response.status_code}"
                )
        except requests.exceptions.RequestException as e:
            raise OllamaNotAvailableError(
                f"Ollama não está rodando. Instale em: https://ollama.ai\n"
                f"Erro: {e}"
            )
    
    def list_models(self) -> List[OllamaModel]:
        """
        Lista todos os modelos instalados no Ollama.
        
        Returns:
            Lista de modelos disponíveis
            
        Example:
            >>> engine = LocalEngine()
            >>> models = engine.list_models()
            >>> for model in models:
            ...     print(f"{model.name} - {model.size_gb:.1f}GB")
        """
        try:
            response = requests.get(f"{self.ollama_host}/api/tags", timeout=5)
            response.raise_for_status()
            
            data = response.json()
            models = []
            
            for model_data in data.get('models', []):
                # Extrair informações do modelo
                name = model_data.get('name', 'unknown')
                size_bytes = model_data.get('size', 0)
                size_gb = size_bytes / (1024 ** 3)
                modified_at = model_data.get('modified_at')
                
                # Extrair família do modelo
                family = name.split(':')[0] if ':' in name else name
                
                # Estimar parâmetros baseado no tamanho
                # Aproximação: 1B parâmetros ≈ 2GB (FP16)
                parameters = int((size_gb / 2) * 1_000_000_000)
                
                model = OllamaModel(
                    name=name,
                    size_gb=size_gb,
                    parameters=parameters,
                    installed=True,
                    family=family,
                    modified_at=modified_at
                )
                models.append(model)
            
            self.available_models = models
            
            print(f"[LOCAL ENGINE] 📚 {len(models)} modelos instalados:")
            for model in models:
                print(f"  • {model.name} ({model.size_gb:.1f}GB, ~{model.parameters/1e9:.1f}B params)")
            
            return models
            
        except requests.exceptions.RequestException as e:
            raise OllamaNotAvailableError(f"Erro ao listar modelos: {e}")
    
    def generate(self, request: LocalInferenceRequest) -> LocalInferenceResponse:
        """
        Gera resposta usando modelo local.
        
        Args:
            request: Requisição de inferência
            
        Returns:
            Resposta do modelo com texto gerado e métricas
            
        Raises:
            ModelNotFoundError: Se modelo não está instalado
            OllamaNotAvailableError: Se Ollama não está disponível
            
        Example:
            >>> request = LocalInferenceRequest(
            ...     prompt="Explain quantum computing",
            ...     model="llama3:8b",
            ...     temperature=0.7
            ... )
            >>> response = engine.generate(request)
            >>> print(f"Generated {response.tokens_generated} tokens in {response.latency_ms:.0f}ms")
        """
        start_time = time.time()
        
        # Verificar se modelo está instalado
        if not self._is_model_installed(request.model):
            raise ModelNotFoundError(
                f"Modelo '{request.model}' não está instalado. "
                f"Instale com: ollama pull {request.model}"
            )
        
        # Preparar payload
        payload = {
            "model": request.model,
            "prompt": request.prompt,
            "stream": False,  # Não usar streaming neste método
            "options": {
                "temperature": request.temperature,
                "num_predict": request.max_tokens
            }
        }
        
        if request.system:
            payload["system"] = request.system
        
        if request.context:
            payload["context"] = request.context
        
        try:
            # Fazer requisição para Ollama
            response = requests.post(
                f"{self.ollama_host}/api/generate",
                json=payload,
                timeout=120  # 2 minutos timeout
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Calcular métricas
            end_time = time.time()
            latency_ms = (end_time - start_time) * 1000
            
            # Extrair resposta
            text = data.get('response', '')
            context = data.get('context', [])
            done = data.get('done', True)
            
            # Estimar tokens gerados (aproximação: 1 token ≈ 4 caracteres)
            tokens_generated = len(text) // 4
            tokens_per_second = tokens_generated / (latency_ms / 1000) if latency_ms > 0 else 0
            
            return LocalInferenceResponse(
                text=text,
                model=request.model,
                tokens_generated=tokens_generated,
                latency_ms=latency_ms,
                tokens_per_second=tokens_per_second,
                context=context,
                done=done
            )
            
        except requests.exceptions.Timeout:
            raise OllamaNotAvailableError(
                f"Timeout ao gerar resposta com modelo '{request.model}'. "
                f"Modelo pode ser muito grande ou prompt muito complexo."
            )
        except requests.exceptions.RequestException as e:
            raise OllamaNotAvailableError(f"Erro ao gerar resposta: {e}")
    
    def stream_generate(self, request: LocalInferenceRequest) -> Iterator[str]:
        """
        Gera resposta com streaming para UX responsiva.
        
        Args:
            request: Requisição de inferência (stream será forçado para True)
            
        Yields:
            Tokens gerados incrementalmente
            
        Example:
            >>> request = LocalInferenceRequest(
            ...     prompt="Write a story",
            ...     model="llama3:8b"
            ... )
            >>> for token in engine.stream_generate(request):
            ...     print(token, end='', flush=True)
        """
        # Verificar se modelo está instalado
        if not self._is_model_installed(request.model):
            raise ModelNotFoundError(
                f"Modelo '{request.model}' não está instalado. "
                f"Instale com: ollama pull {request.model}"
            )
        
        # Preparar payload
        payload = {
            "model": request.model,
            "prompt": request.prompt,
            "stream": True,  # Forçar streaming
            "options": {
                "temperature": request.temperature,
                "num_predict": request.max_tokens
            }
        }
        
        if request.system:
            payload["system"] = request.system
        
        if request.context:
            payload["context"] = request.context
        
        try:
            # Fazer requisição com streaming
            response = requests.post(
                f"{self.ollama_host}/api/generate",
                json=payload,
                stream=True,
                timeout=120
            )
            response.raise_for_status()
            
            # Processar stream
            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    token = data.get('response', '')
                    if token:
                        yield token
                    
                    # Verificar se terminou
                    if data.get('done', False):
                        break
                        
        except requests.exceptions.RequestException as e:
            raise OllamaNotAvailableError(f"Erro no streaming: {e}")
    
    def pull_model(self, model_name: str) -> None:
        """
        Baixa e instala novo modelo.
        
        Args:
            model_name: Nome do modelo (ex: "deepseek-coder:7b")
            
        Example:
            >>> engine.pull_model("deepseek-coder:7b")
            [LOCAL ENGINE] 📥 Baixando deepseek-coder:7b...
            [LOCAL ENGINE] ✅ Modelo instalado com sucesso
        """
        print(f"[LOCAL ENGINE] 📥 Baixando {model_name}...")
        
        try:
            response = requests.post(
                f"{self.ollama_host}/api/pull",
                json={"name": model_name},
                stream=True,
                timeout=3600  # 1 hora para download
            )
            response.raise_for_status()
            
            # Processar progresso
            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    status = data.get('status', '')
                    
                    if 'pulling' in status.lower():
                        # Mostrar progresso
                        total = data.get('total', 0)
                        completed = data.get('completed', 0)
                        if total > 0:
                            percent = (completed / total) * 100
                            print(f"[LOCAL ENGINE] 📊 Progresso: {percent:.1f}%", end='\r')
                    
                    if data.get('status') == 'success':
                        print(f"\n[LOCAL ENGINE] ✅ Modelo {model_name} instalado com sucesso")
                        break
                        
        except requests.exceptions.RequestException as e:
            raise OllamaNotAvailableError(f"Erro ao baixar modelo: {e}")
    
    def get_model_info(self, model_name: str) -> OllamaModel:
        """
        Retorna informações sobre modelo específico.
        
        Args:
            model_name: Nome do modelo
            
        Returns:
            Informações do modelo
            
        Raises:
            ModelNotFoundError: Se modelo não está instalado
        """
        # Atualizar lista de modelos
        self.list_models()
        
        # Buscar modelo
        for model in self.available_models:
            if model.name == model_name:
                return model
        
        raise ModelNotFoundError(f"Modelo '{model_name}' não encontrado")
    
    def _is_model_installed(self, model_name: str) -> bool:
        """
        Verifica se modelo está instalado.
        
        Args:
            model_name: Nome do modelo
            
        Returns:
            True se instalado, False caso contrário
        """
        # Atualizar lista se vazia
        if not self.available_models:
            try:
                self.list_models()
            except:
                return False
        
        # Verificar se modelo está na lista
        return any(m.name == model_name for m in self.available_models)
    
    def get_recommended_models(self) -> Dict[str, str]:
        """
        Retorna modelos recomendados para diferentes casos de uso.
        
        Returns:
            Dicionário com recomendações
        """
        return {
            "coding": "deepseek-coder:7b",
            "general": "llama3:8b",
            "fast": "mistral:7b",
            "powerful": "llama3:70b",
            "code_large": "deepseek-coder:33b"
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Retorna estatísticas do Local Engine.
        
        Returns:
            Estatísticas de uso
        """
        return {
            "ollama_available": self.check_ollama_available(),
            "models_installed": len(self.available_models),
            "total_size_gb": sum(m.size_gb for m in self.available_models),
            "models": [m.to_dict() for m in self.available_models]
        }


# Singleton instance
_local_engine: Optional[LocalEngine] = None


def get_local_engine() -> LocalEngine:
    """
    Retorna instância singleton do Local Engine.
    
    Returns:
        LocalEngine singleton
    """
    global _local_engine
    if _local_engine is None:
        _local_engine = LocalEngine()
    return _local_engine


if __name__ == "__main__":
    # Demo rápido
    print("=" * 80)
    print("AETHEL LOCAL ENGINE - DEMO")
    print("=" * 80)
    
    engine = LocalEngine()
    
    try:
        # Verificar Ollama
        engine.check_ollama_available()
        
        # Listar modelos
        models = engine.list_models()
        
        if models:
            # Testar inferência com primeiro modelo
            model = models[0]
            print(f"\n[DEMO] Testando inferência com {model.name}...")
            
            request = LocalInferenceRequest(
                prompt="Write a Python function to calculate factorial",
                model=model.name,
                temperature=0.7,
                max_tokens=200
            )
            
            response = engine.generate(request)
            
            print(f"\n[DEMO] Resposta gerada:")
            print(response.text)
            print(f"\n[DEMO] Métricas:")
            print(f"  • Tokens: {response.tokens_generated}")
            print(f"  • Latência: {response.latency_ms:.0f}ms")
            print(f"  • Throughput: {response.tokens_per_second:.1f} tokens/s")
        else:
            print("\n[DEMO] Nenhum modelo instalado.")
            print("[DEMO] Instale um modelo com: ollama pull deepseek-coder:7b")
            
    except OllamaNotAvailableError as e:
        print(f"\n[DEMO] ❌ {e}")
        print("\n[DEMO] Para instalar Ollama:")
        print("  1. Visite: https://ollama.ai")
        print("  2. Baixe e instale para seu sistema operacional")
        print("  3. Execute: ollama pull deepseek-coder:7b")
        print("  4. Execute este script novamente")
