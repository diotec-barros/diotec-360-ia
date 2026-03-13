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

﻿# Aethel ZKP v1.6.2
import hashlib
import secrets
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum

class CommitmentScheme(Enum):
    HASH_BASED = "hash_based"
    PEDERSEN = "pedersen"
    BULLETPROOF = "bulletproof"

@dataclass
class Commitment:
    commitment_hash: str
    salt: str
    scheme: CommitmentScheme = CommitmentScheme.HASH_BASED
    def __str__(self):
        return f"Commitment({self.commitment_hash[:16]}...)"

@dataclass
class SecretVariable:
    name: str
    commitment: Commitment
    _hidden_value: Optional[Any] = None
    def reveal_for_verification(self) -> Any:
        return self._hidden_value

class AethelZKP:
    def __init__(self):
        self.secret_variables: Dict[str, SecretVariable] = {}
        self.commitments: Dict[str, Commitment] = {}
    
    @staticmethod
    def commit(value: Any, secret_salt: Optional[str] = None) -> Commitment:
        salt = secret_salt or secrets.token_hex(32)
        commitment_data = f"{value}:{salt}".encode()
        commitment_hash = hashlib.sha256(commitment_data).hexdigest()
        return Commitment(commitment_hash=commitment_hash, salt=salt, scheme=CommitmentScheme.HASH_BASED)
    
    @staticmethod
    def verify_commitment(value: Any, commitment: Commitment) -> bool:
        commitment_data = f"{value}:{commitment.salt}".encode()
        recomputed_hash = hashlib.sha256(commitment_data).hexdigest()
        return recomputed_hash == commitment.commitment_hash
    
    @staticmethod
    def verify_equality(val1: Any, salt1: str, val2: Any, salt2: str) -> bool:
        hash1 = hashlib.sha256(f"{val1}:{salt1}".encode()).hexdigest()
        hash2 = hashlib.sha256(f"{val2}:{salt2}".encode()).hexdigest()
        return hash1 == hash2
    
    def register_secret(self, name: str, value: Any) -> SecretVariable:
        commitment = self.commit(value)
        secret_var = SecretVariable(name=name, commitment=commitment, _hidden_value=value)
        self.secret_variables[name] = secret_var
        self.commitments[name] = commitment
        return secret_var
    
    def prove_conservation_zkp(self, inputs: List[Tuple[str, Any]], outputs: List[Tuple[str, Any]]) -> Dict[str, Any]:
        input_commitments = []
        output_commitments = []
        for var_name, value in inputs:
            commitment = self.commit(value)
            input_commitments.append({"variable": var_name, "commitment": commitment.commitment_hash, "value_hidden": True})
        for var_name, value in outputs:
            commitment = self.commit(value)
            output_commitments.append({"variable": var_name, "commitment": commitment.commitment_hash, "value_hidden": True})
        input_sum = sum(v for _, v in inputs)
        output_sum = sum(v for _, v in outputs)
        conservation_holds = (input_sum == output_sum)
        return {"status": "PROVED" if conservation_holds else "FAILED", "conservation_holds": conservation_holds, "input_commitments": input_commitments, "output_commitments": output_commitments, "values_revealed": False, "proof_type": "ZKP_CONSERVATION"}
    
    def get_commitment(self, var_name: str) -> Optional[Commitment]:
        return self.commitments.get(var_name)
    
    def is_secret(self, var_name: str) -> bool:
        return var_name in self.secret_variables
    
    def get_proof_summary(self) -> Dict[str, Any]:
        return {"secret_variables": len(self.secret_variables), "commitments": {name: {"commitment_hash": comm.commitment_hash[:16] + "...", "scheme": comm.scheme.value} for name, comm in self.commitments.items()}, "values_revealed": False, "zkp_active": True}

_zkp_engine = None

def get_zkp_engine() -> AethelZKP:
    global _zkp_engine
    if _zkp_engine is None:
        _zkp_engine = AethelZKP()
    return _zkp_engine
