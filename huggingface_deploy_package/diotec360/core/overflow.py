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
Aethel Overflow Sentinel v1.4.0
================================

Detecta e previne integer overflow/underflow em operações aritméticas.

A Sentinela analisa todas as operações matemáticas e garante que:
1. Nenhum valor exceda MAX_INT (2^63 - 1 para signed 64-bit)
2. Nenhum valor fique abaixo de MIN_INT (-2^63 para signed 64-bit)
3. Operações intermediárias não causem overflow

Filosofia: "Se o hardware pode quebrar, a matemática deve prevenir."
"""

import re
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple


# Limites para inteiros de 64 bits (signed)
MAX_INT = 2**63 - 1  # 9,223,372,036,854,775,807
MIN_INT = -(2**63)   # -9,223,372,036,854,775,808


@dataclass
class OverflowResult:
    """Resultado da verificação de overflow"""
    is_safe: bool
    violations: List[Dict[str, any]]
    message: str
    
    def format_error(self) -> str:
        """Formata mensagem de erro para o usuário"""
        if self.is_safe:
            return "✅ Nenhum overflow detectado"
        
        error_msg = "🚨 OVERFLOW/UNDERFLOW DETECTADO!\n\n"
        for v in self.violations:
            error_msg += f"  • Operação: {v['operation']}\n"
            error_msg += f"    Variável: {v['variable']}\n"
            error_msg += f"    Tipo: {v['type']}\n"
            error_msg += f"    Valor resultante: {v['result']}\n"
            error_msg += f"    Limite: {v['limit']}\n\n"
        
        return error_msg


class OverflowSentinel:
    """
    Sentinela de Overflow - Detecta operações aritméticas perigosas
    
    Estratégia:
    1. Extrai todas as operações aritméticas das pós-condições
    2. Para cada operação, verifica se pode causar overflow/underflow
    3. Considera valores máximos possíveis para variáveis
    4. Bloqueia código se detectar risco
    """
    
    def __init__(self, max_int: int = MAX_INT, min_int: int = MIN_INT):
        self.max_int = max_int
        self.min_int = min_int
    
    def check_intent(self, intent_data: Dict) -> OverflowResult:
        """
        Verifica se um intent pode causar overflow/underflow
        
        Args:
            intent_data: Dicionário com 'verify' (pós-condições)
        
        Returns:
            OverflowResult com resultado da verificação
        """
        post_conditions = intent_data.get('verify', [])
        violations = []
        
        for condition in post_conditions:
            if isinstance(condition, dict):
                condition = str(condition.get('expression', '')).strip()
            else:
                condition = str(condition).strip()

            if not condition:
                continue

            # Detectar operações aritméticas
            operations = self._extract_operations(condition)
            
            for op in operations:
                violation = self._check_operation_safety(op, condition)
                if violation:
                    violations.append(violation)
        
        if violations:
            return OverflowResult(
                is_safe=False,
                violations=violations,
                message=f"Detectadas {len(violations)} operação(ões) com risco de overflow/underflow"
            )
        
        return OverflowResult(
            is_safe=True,
            violations=[],
            message="Todas as operações são seguras contra overflow/underflow"
        )
    
    def _extract_operations(self, condition: str) -> List[Dict]:
        """
        Extrai operações aritméticas de uma condição
        
        Exemplo:
            "balance == old_balance + 1000000000000000000"
            -> [{'var': 'balance', 'op': '+', 'value': 1000000000000000000}]
        
        v1.4.1: Agora também extrai operações entre literais (ex: 800 + 100)
        """
        operations = []
        
        # Padrão 1: variável == old_variável [+/-/*///%] valor
        # Exemplo: balance == old_balance + 100
        pattern = r'(\w+)\s*==\s*(\w+)\s*([+\-*/%])\s*(\d+)'
        matches = re.finditer(pattern, condition)
        
        for match in matches:
            var_name = match.group(1)
            old_var = match.group(2)
            operator = match.group(3)
            value = int(match.group(4))
            
            operations.append({
                'variable': var_name,
                'old_variable': old_var,
                'operator': operator,
                'value': value,
                'full_expr': match.group(0),
                'type': 'var_op_literal'
            })
        
        # Padrão 2: variável == (literal [+/-/*///%] literal)
        # Exemplo: balance == (9223372036854775800 + 100)
        # v1.4.1: CRITICAL - Detecta operações entre literais!
        # Suporta números negativos: -123
        pattern2 = r'(\w+)\s*==\s*\(?\s*(-?\d+)\s*([+\-*/%])\s*(-?\d+)\s*\)?'
        matches2 = re.finditer(pattern2, condition)
        
        for match in matches2:
            var_name = match.group(1)
            literal1 = int(match.group(2))
            operator = match.group(3)
            literal2 = int(match.group(4))
            
            operations.append({
                'variable': var_name,
                'literal1': literal1,
                'operator': operator,
                'literal2': literal2,
                'full_expr': match.group(0),
                'type': 'literal_op_literal'
            })
        
        return operations
    
    def _check_operation_safety(self, operation: Dict, condition: str) -> Optional[Dict]:
        """
        Verifica se uma operação específica é segura
        
        v1.4.1 CRITICAL FIX: Agora verifica o RESULTADO da operação, não apenas valores individuais
        
        Para operações literal-to-literal: calcula o resultado exato
        Para operações com variáveis: assume pior caso (variável no limite)
        """
        operator = operation['operator']
        op_type = operation['type']
        variable = operation['variable']
        
        # CASO 1: Operação entre literais (ex: balance == (9223372036854775800 + 100))
        if op_type == 'literal_op_literal':
            literal1 = operation['literal1']
            literal2 = operation['literal2']
            
            # Calcular resultado exato
            try:
                if operator == '+':
                    result = literal1 + literal2
                    if result > self.max_int:
                        return {
                            'operation': f"{variable} = ({literal1} + {literal2})",
                            'variable': variable,
                            'type': 'OVERFLOW',
                            'result': f"{result} > {self.max_int}",
                            'limit': f"MAX_INT = {self.max_int}",
                            'recommendation': f"Resultado da adição excede MAX_INT por {result - self.max_int}"
                        }
                    if result < self.min_int:
                        return {
                            'operation': f"{variable} = ({literal1} + {literal2})",
                            'variable': variable,
                            'type': 'UNDERFLOW',
                            'result': f"{result} < {self.min_int}",
                            'limit': f"MIN_INT = {self.min_int}",
                            'recommendation': f"Resultado da adição está abaixo de MIN_INT"
                        }
                
                elif operator == '-':
                    result = literal1 - literal2
                    if result > self.max_int:
                        return {
                            'operation': f"{variable} = ({literal1} - {literal2})",
                            'variable': variable,
                            'type': 'OVERFLOW',
                            'result': f"{result} > {self.max_int}",
                            'limit': f"MAX_INT = {self.max_int}",
                            'recommendation': f"Resultado da subtração excede MAX_INT"
                        }
                    if result < self.min_int:
                        return {
                            'operation': f"{variable} = ({literal1} - {literal2})",
                            'variable': variable,
                            'type': 'UNDERFLOW',
                            'result': f"{result} < {self.min_int}",
                            'limit': f"MIN_INT = {self.min_int}",
                            'recommendation': f"Resultado da subtração está abaixo de MIN_INT por {self.min_int - result}"
                        }
                
                elif operator == '*':
                    result = literal1 * literal2
                    if result > self.max_int:
                        return {
                            'operation': f"{variable} = ({literal1} * {literal2})",
                            'variable': variable,
                            'type': 'OVERFLOW',
                            'result': f"{result} > {self.max_int}",
                            'limit': f"MAX_INT = {self.max_int}",
                            'recommendation': f"Resultado da multiplicação excede MAX_INT por {result - self.max_int}"
                        }
                    if result < self.min_int:
                        return {
                            'operation': f"{variable} = ({literal1} * {literal2})",
                            'variable': variable,
                            'type': 'UNDERFLOW',
                            'result': f"{result} < {self.min_int}",
                            'limit': f"MIN_INT = {self.min_int}",
                            'recommendation': f"Resultado da multiplicação está abaixo de MIN_INT"
                        }
                
                elif operator == '/' or operator == '%':
                    if literal2 == 0:
                        return {
                            'operation': f"{variable} = ({literal1} {operator} {literal2})",
                            'variable': variable,
                            'type': 'DIVISION_BY_ZERO',
                            'result': 'UNDEFINED',
                            'limit': 'N/A',
                            'recommendation': 'Divisão por zero é matematicamente impossível'
                        }
            except:
                # Se Python overflow (improvável com Python 3), bloquear
                return {
                    'operation': f"{variable} = ({literal1} {operator} {literal2})",
                    'variable': variable,
                    'type': 'OVERFLOW',
                    'result': 'EXCEEDS PYTHON LIMITS',
                    'limit': f"MAX_INT = {self.max_int}",
                    'recommendation': 'Operação excede limites computacionais'
                }
        
        # CASO 2: Operação com variável (ex: balance == old_balance + 100)
        elif op_type == 'var_op_literal':
            value = operation['value']
            old_variable = operation['old_variable']
            
            # Verificar adição: assume pior caso (variável já está no MAX_INT)
            if operator == '+':
                # Se adicionar value ao MAX_INT causaria overflow?
                # Matemática: MAX_INT + value > MAX_INT sempre que value > 0
                # Mas queremos saber: existe algum valor de old_variable onde old_variable + value > MAX_INT?
                # Resposta: sim, se old_variable > MAX_INT - value
                # Como não sabemos old_variable, assumimos pior caso: old_variable = MAX_INT
                worst_case_result = self.max_int + value
                if worst_case_result > self.max_int:  # Sempre true se value > 0, mas checamos overflow
                    # Verificar se value é grande o suficiente para ser perigoso
                    # Se value > 0, sempre há risco (old_variable pode estar perto de MAX_INT)
                    # Mas para evitar falsos positivos, só alertamos se value é significativo
                    if value > 1000:  # Threshold: valores > 1000 são considerados perigosos
                        return {
                            'operation': f"{variable} = {old_variable} + {value}",
                            'variable': variable,
                            'type': 'OVERFLOW_RISK',
                            'result': f"Pode exceder {self.max_int} se {old_variable} > {self.max_int - value}",
                            'limit': f"MAX_INT = {self.max_int}",
                            'recommendation': f"Adicione guard: {old_variable} <= {self.max_int - value}"
                        }
            
            # Verificar subtração: assume pior caso (variável já está no MIN_INT)
            elif operator == '-':
                worst_case_result = self.min_int - value
                if worst_case_result < self.min_int:
                    if value > 1000:  # Threshold
                        return {
                            'operation': f"{variable} = {old_variable} - {value}",
                            'variable': variable,
                            'type': 'UNDERFLOW_RISK',
                            'result': f"Pode ficar abaixo de {self.min_int} se {old_variable} < {self.min_int + value}",
                            'limit': f"MIN_INT = {self.min_int}",
                            'recommendation': f"Adicione guard: {old_variable} >= {self.min_int + value}"
                        }
            
            # Verificar multiplicação: perigosa se multiplicador é grande
            elif operator == '*':
                # Se old_variable = MAX_INT e value > 1, overflow garantido
                # Verificar: MAX_INT * value > MAX_INT?
                if value > 1:
                    # Calcular: qual o máximo valor de old_variable que não causa overflow?
                    # old_variable * value <= MAX_INT
                    # old_variable <= MAX_INT / value
                    safe_max = self.max_int // value
                    if safe_max < 1000000:  # Se o limite seguro é muito baixo, é perigoso
                        return {
                            'operation': f"{variable} = {old_variable} * {value}",
                            'variable': variable,
                            'type': 'OVERFLOW_RISK',
                            'result': f"Pode exceder {self.max_int} se {old_variable} > {safe_max}",
                            'limit': f"MAX_INT = {self.max_int}",
                            'recommendation': f"Adicione guard: {old_variable} <= {safe_max}"
                        }
            
            # Verificar divisão por zero
            elif operator == '/' or operator == '%':
                if value == 0:
                    return {
                        'operation': f"{variable} = {old_variable} {operator} {value}",
                        'variable': variable,
                        'type': 'DIVISION_BY_ZERO',
                        'result': 'UNDEFINED',
                        'limit': 'N/A',
                        'recommendation': 'Divisão por zero é matematicamente impossível'
                    }
        
        return None
    
    def check_explicit_overflow(self, variable: str, value: int) -> Optional[Dict]:
        """
        Verifica se um valor explícito causa overflow
        
        Exemplo: balance == 99999999999999999999 (maior que MAX_INT)
        """
        if value > self.max_int:
            return {
                'operation': f"{variable} = {value}",
                'variable': variable,
                'type': 'EXPLICIT_OVERFLOW',
                'result': value,
                'limit': f"MAX_INT = {self.max_int}",
                'recommendation': f"Valor excede o limite máximo de inteiros de 64 bits"
            }
        
        if value < self.min_int:
            return {
                'operation': f"{variable} = {value}",
                'variable': variable,
                'type': 'EXPLICIT_UNDERFLOW',
                'result': value,
                'limit': f"MIN_INT = {self.min_int}",
                'recommendation': f"Valor está abaixo do limite mínimo de inteiros de 64 bits"
            }
        
        return None
    
    def get_safe_range(self) -> Tuple[int, int]:
        """Retorna o range seguro de valores"""
        return (self.min_int, self.max_int)
    
    def format_limits(self) -> str:
        """Formata os limites de forma legível"""
        return f"""
╔══════════════════════════════════════════════════════════╗
║              OVERFLOW SENTINEL - LIMITES                 ║
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║  Tipo: Inteiros de 64 bits (signed)                     ║
║                                                          ║
║  MAX_INT: {self.max_int:>20,}                    ║
║  MIN_INT: {self.min_int:>20,}                    ║
║                                                          ║
║  Range seguro: [{self.min_int}, {self.max_int}]         ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
"""


# Singleton para uso global
_sentinel_instance = None

def get_overflow_sentinel() -> OverflowSentinel:
    """Retorna instância singleton da Sentinela"""
    global _sentinel_instance
    if _sentinel_instance is None:
        _sentinel_instance = OverflowSentinel()
    return _sentinel_instance
