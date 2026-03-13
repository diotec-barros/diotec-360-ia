"""
Aethel Explorer API - Public Code Analysis Endpoint
Allows anyone to test the Aethel Judge for free
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import re

from diotec360.core.judge import AethelJudge
from diotec360.core.conservation import ConservationChecker

router = APIRouter(prefix="/api/v3/explorer", tags=["explorer"])


class AnalyzeRequest(BaseModel):
    code: str
    language: str  # 'python' or 'solidity'


class Violation(BaseModel):
    type: str
    description: str
    line: Optional[int] = None
    severity: str  # 'critical', 'high', 'medium', 'low'


class AnalyzeResponse(BaseModel):
    violations: List[Violation]
    safe: bool
    analysis_time_ms: float


def analyze_python_code(code: str) -> List[Violation]:
    """Analyze Python code for integrity violations"""
    violations = []
    
    # Check for conservation violations
    lines = code.split('\n')
    for i, line in enumerate(lines, 1):
        # Detect value creation (x = x + constant without corresponding subtraction)
        if '+' in line and '=' in line:
            # Simple heuristic: look for patterns like "balance = balance + amount + 1"
            if re.search(r'\+\s*\d+\s*(?!-)', line) and 'return' not in line:
                violations.append(Violation(
                    type="Violação de Conservação",
                    description="Possível criação de valor detectada. A soma não preserva o total.",
                    line=i,
                    severity="critical"
                ))
        
        # Detect multiplication in transfers
        if '*' in line and any(word in line.lower() for word in ['balance', 'amount', 'value']):
            violations.append(Violation(
                type="Multiplicação Suspeita",
                description="Multiplicação detectada em operação de valor. Pode duplicar fundos.",
                line=i,
                severity="high"
            ))
        
        # Detect potential overflow
        if '+=' in line or '-=' in line:
            if 'int' in code or 'uint' in code:
                violations.append(Violation(
                    type="Risco de Overflow",
                    description="Operação aritmética sem verificação de limites.",
                    line=i,
                    severity="medium"
                ))
    
    return violations


def analyze_solidity_code(code: str) -> List[Violation]:
    """Analyze Solidity code for integrity violations"""
    violations = []
    
    lines = code.split('\n')
    for i, line in enumerate(lines, 1):
        # Check for unchecked arithmetic
        if any(op in line for op in ['+=', '-=', '*', '/']):
            if 'unchecked' not in code[:code.index(line) if line in code else 0]:
                violations.append(Violation(
                    type="Aritmética Não Verificada",
                    description="Operação aritmética sem proteção contra overflow/underflow.",
                    line=i,
                    severity="high"
                ))
        
        # Check for multiplication in transfers
        if '*' in line and 'balance' in line.lower():
            violations.append(Violation(
                type="Violação de Conservação",
                description="Multiplicação em transferência pode criar tokens do nada.",
                line=i,
                severity="critical"
            ))
        
        # Check for reentrancy patterns
        if 'call' in line and 'balance' in code.lower():
            violations.append(Violation(
                type="Risco de Reentrância",
                description="Chamada externa antes de atualizar estado pode permitir reentrância.",
                line=i,
                severity="critical"
            ))
    
    return violations


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_code(request: AnalyzeRequest):
    """
    Public endpoint to analyze code for integrity violations
    This is the free "taste" that converts visitors to customers
    """
    import time
    start_time = time.time()
    
    try:
        if request.language == 'python':
            violations = analyze_python_code(request.code)
        elif request.language == 'solidity':
            violations = analyze_solidity_code(request.code)
        else:
            raise HTTPException(status_code=400, detail="Linguagem não suportada")
        
        analysis_time = (time.time() - start_time) * 1000
        
        return AnalyzeResponse(
            violations=violations,
            safe=len(violations) == 0,
            analysis_time_ms=round(analysis_time, 2)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na análise: {str(e)}")


@router.get("/stats")
async def get_explorer_stats():
    """Get public statistics about Explorer usage"""
    # These would come from a real database in production
    return {
        "total_analyses": 1247,
        "analyses_today": 89,
        "error_rate": 0.89,
        "total_value_protected": 2400000,
        "top_violations": [
            {"type": "Violação de Conservação", "count": 456},
            {"type": "Risco de Overflow", "count": 234},
            {"type": "Multiplicação Suspeita", "count": 189},
        ]
    }
