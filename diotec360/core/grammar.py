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

# Gramática Aethel v1.8.1 - "Synchrony Protocol"
# Suporte a: operadores aritméticos, números literais (inteiros e decimais), comentários, SECRET keyword, EXTERNAL keyword, ATOMIC_BATCH
aethel_grammar = """
    start: (intent_def | atomic_batch)+
    
    intent_def: "intent" NAME "(" params ")" "{" guard_block solve_block verify_block "}"
    atomic_batch: "atomic_batch" NAME "{" intent_def* "}"
    
    params: (param ("," param)*)?
    param: ["secret"] ["external"] NAME ":" NAME
    
    guard_block: "guard" "{" (condition ";")+ "}"
    solve_block: "solve" "{" (setting ";")+ "}"
    verify_block: "verify" "{" (condition ";")+ "}"
    
    condition: ["secret"] ["external"] expr OPERATOR expr
    setting: NAME ":" NAME
    
    ?expr: term
         | expr "+" term    -> add
         | expr "-" term    -> subtract
    
    ?term: factor
         | term "*" factor  -> multiply
         | term "/" factor  -> divide
         | term "%" factor  -> modulo
    
    ?factor: atom
           | "(" expr ")"
    
    ?atom: NAME
         | NUMBER
    
    OPERATOR: ">=" | "<=" | "==" | "!=" | ">" | "<"
    NUMBER: /-?[0-9]+(\\.[0-9]+)?/  # ✅ ATUALIZADO: Suporte a números decimais
    NAME: /[a-zA-Z_][a-zA-Z0-9_]*/
    COMMENT: /#[^\\n]*/
    
    %import common.WS
    %ignore WS
    %ignore COMMENT
"""
