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
Aethel Sanitizer v1.5.1 - The Fortress Shield
==============================================

Protege contra ataques de injeção de código e prompt injection.

Detecta e bloqueia:
1. Tentativas de prompt injection
2. Comandos de sistema perigosos
3. Funções de execução dinâmica
4. Caracteres de escape maliciosos

Filosofia: "Sanitize first, verify later. Trust nothing from the outside."
"""

import re
from dataclasses import dataclass
from typing import List, Dict, Optional


@dataclass
class SanitizeResult:
    """Resultado da sanitização"""
    is_safe: bool
    violations: List[Dict[str, str]]
    message: str
    clean_code: Optional[str] = None
    
    def format_error(self) -> str:
        """Formata mensagem de erro para o usuário"""
        if self.is_safe:
            return "✅ Código aprovado pela sanitização"
        
        error_msg = "🚨 FORTRESS BLOCK - Tentativa de Injeção Detectada!\n\n"
        for v in self.violations:
            error_msg += f"  • Tipo: {v['type']}\n"
            error_msg += f"    Padrão: {v['pattern']}\n"
            error_msg += f"    Localização: {v['location']}\n"
            error_msg += f"    Risco: {v['risk']}\n\n"
        
        return error_msg


class AethelSanitizer:
    """
    Sanitizador de Código - Primeira linha de defesa contra ataques
    
    Estratégia:
    1. Detecta padrões maliciosos conhecidos
    2. Bloqueia comandos de sistema
    3. Remove comentários suspeitos
    4. Valida estrutura do código
    """
    
    # Padrões proibidos - Prompt Injection
    FORBIDDEN_PATTERNS = [
        (r'IGNORE\s+PREVIOUS', 'PROMPT_INJECTION', 'CRÍTICO'),
        (r'SYSTEM\s+PROMPT', 'PROMPT_INJECTION', 'CRÍTICO'),
        (r'DISREGARD\s+INSTRUCTIONS', 'PROMPT_INJECTION', 'CRÍTICO'),
        (r'OVERRIDE\s+SECURITY', 'PROMPT_INJECTION', 'CRÍTICO'),
        (r'BYPASS\s+', 'PROMPT_INJECTION', 'ALTO'),
        (r'LEAK\s+', 'DATA_EXFILTRATION', 'ALTO'),
        (r'OUTPUT\s+.*\s+IN\s+COMMENTS', 'DATA_EXFILTRATION', 'ALTO'),
    ]
    
    # Comandos de sistema perigosos
    DANGEROUS_COMMANDS = [
        (r'\bos\.', 'SYSTEM_COMMAND', 'CRÍTICO'),
        (r'\bsys\.', 'SYSTEM_COMMAND', 'CRÍTICO'),
        (r'\bsubprocess\.', 'SYSTEM_COMMAND', 'CRÍTICO'),
        (r'\beval\s*\(', 'CODE_EXECUTION', 'CRÍTICO'),
        (r'\bexec\s*\(', 'CODE_EXECUTION', 'CRÍTICO'),
        (r'\b__import__\s*\(', 'DYNAMIC_IMPORT', 'CRÍTICO'),
        (r'\bopen\s*\(', 'FILE_ACCESS', 'ALTO'),
        (r'\bfile\s*\(', 'FILE_ACCESS', 'ALTO'),
    ]
    
    # Caracteres suspeitos
    SUSPICIOUS_CHARS = [
        (r'[\x00-\x08\x0B\x0C\x0E-\x1F]', 'CONTROL_CHARS', 'MÉDIO'),
        (r'[^\x20-\x7E\n\r\t]', 'NON_ASCII', 'BAIXO'),  # Permite apenas ASCII imprimível
    ]
    
    # Limites de segurança
    MAX_CODE_LENGTH = 50000  # 50KB
    MAX_LINE_LENGTH = 1000
    MAX_COMMENT_LENGTH = 500
    
    def sanitize(self, code: str) -> SanitizeResult:
        """
        Sanitiza código Aethel
        
        Args:
            code: Código Aethel a ser sanitizado
        
        Returns:
            SanitizeResult com resultado da sanitização
        """
        violations = []
        
        # 1. Verificar tamanho do código
        if len(code) > self.MAX_CODE_LENGTH:
            violations.append({
                'type': 'SIZE_LIMIT',
                'pattern': f'Código muito grande: {len(code)} bytes',
                'location': 'global',
                'risk': 'MÉDIO'
            })
        
        # 2. Detectar padrões de prompt injection
        for pattern, attack_type, risk in self.FORBIDDEN_PATTERNS:
            matches = re.finditer(pattern, code, re.IGNORECASE)
            for match in matches:
                violations.append({
                    'type': attack_type,
                    'pattern': pattern,
                    'location': f'linha {self._get_line_number(code, match.start())}',
                    'risk': risk,
                    'matched': match.group(0)
                })
        
        # 3. Detectar comandos de sistema perigosos
        for pattern, attack_type, risk in self.DANGEROUS_COMMANDS:
            matches = re.finditer(pattern, code, re.IGNORECASE)
            for match in matches:
                violations.append({
                    'type': attack_type,
                    'pattern': pattern,
                    'location': f'linha {self._get_line_number(code, match.start())}',
                    'risk': risk,
                    'matched': match.group(0)
                })
        
        # 4. Detectar caracteres suspeitos
        for pattern, attack_type, risk in self.SUSPICIOUS_CHARS:
            matches = re.finditer(pattern, code)
            if matches:
                for match in list(matches)[:5]:  # Limitar a 5 exemplos
                    violations.append({
                        'type': attack_type,
                        'pattern': 'Caracteres não permitidos',
                        'location': f'posição {match.start()}',
                        'risk': risk,
                        'matched': repr(match.group(0))
                    })
        
        # 5. Verificar linhas muito longas
        lines = code.split('\n')
        for i, line in enumerate(lines, 1):
            if len(line) > self.MAX_LINE_LENGTH:
                violations.append({
                    'type': 'LINE_TOO_LONG',
                    'pattern': f'Linha com {len(line)} caracteres',
                    'location': f'linha {i}',
                    'risk': 'BAIXO'
                })
        
        # 6. Verificar comentários suspeitos
        comment_pattern = r'#.*$'
        for match in re.finditer(comment_pattern, code, re.MULTILINE):
            comment = match.group(0)
            if len(comment) > self.MAX_COMMENT_LENGTH:
                violations.append({
                    'type': 'SUSPICIOUS_COMMENT',
                    'pattern': 'Comentário muito longo',
                    'location': f'linha {self._get_line_number(code, match.start())}',
                    'risk': 'BAIXO'
                })
        
        # Resultado
        if violations:
            # Filtrar apenas violações críticas e altas
            critical_violations = [v for v in violations if v['risk'] in ['CRÍTICO', 'ALTO']]
            
            if critical_violations:
                return SanitizeResult(
                    is_safe=False,
                    violations=critical_violations,
                    message=f'Detectadas {len(critical_violations)} violação(ões) de segurança crítica(s)'
                )
            else:
                # Apenas avisos de baixo risco
                return SanitizeResult(
                    is_safe=True,
                    violations=violations,
                    message=f'Código aprovado com {len(violations)} aviso(s) de baixo risco',
                    clean_code=code
                )
        
        return SanitizeResult(
            is_safe=True,
            violations=[],
            message='Código aprovado pela sanitização',
            clean_code=code
        )
    
    def _get_line_number(self, code: str, position: int) -> int:
        """Retorna o número da linha para uma posição no código"""
        return code[:position].count('\n') + 1
    
    def check_complexity(self, code: str) -> Dict:
        """
        Verifica complexidade do código para prevenir DoS
        
        Returns:
            Dict com métricas de complexidade
        """
        lines = code.split('\n')
        
        # Contar variáveis únicas
        var_pattern = r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b'
        variables = set(re.findall(var_pattern, code))
        
        # Contar operadores
        operators = len(re.findall(r'[+\-*/%<>=!]', code))
        
        # Contar blocos
        blocks = code.count('{')
        
        return {
            'lines': len(lines),
            'variables': len(variables),
            'operators': operators,
            'blocks': blocks,
            'size_bytes': len(code.encode('utf-8'))
        }


# Singleton para uso global
_sanitizer_instance = None

def get_sanitizer() -> AethelSanitizer:
    """Retorna instância singleton do Sanitizer"""
    global _sanitizer_instance
    if _sanitizer_instance is None:
        _sanitizer_instance = AethelSanitizer()
    return _sanitizer_instance
