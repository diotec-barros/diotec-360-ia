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

class AethelBridge:
    def __init__(self, intent_map):
        self.intent_map = intent_map
        self.error_feedback = []  # Histórico de erros para feedback loop

    def _condition_to_expression(self, condition):
        if isinstance(condition, dict):
            return str(condition.get('expression', '')).strip()
        return str(condition).strip()

    def _format_params(self, params):
        if not params:
            return ""
        if isinstance(params, list) and params and isinstance(params[0], dict):
            return ", ".join(
                f"{p.get('name')}:{p.get('type')}" for p in params if p.get('name') and p.get('type')
            )
        return ", ".join(str(p) for p in params)
    
    def generate_generation_prompt(self, intent_name):
        """
        Esta função transforma a intenção em uma especificação técnica 
        que nenhum modelo de IA comum ignoraria.
        """
        data = self.intent_map[intent_name]
        
        # O "Contrato Inquebrável"
        prompt = f"""[ROLE: AETHEL_KERNEL_GENERATOR]
[TARGET_LANGUAGE: RUST]
[INTENT: {intent_name}]
[PARAMETERS: {self._format_params(data.get('params', []))}]

[STRICT_CONSTRAINTS]:
As condições abaixo DEVEM ser validadas antes da execução:
{self._format_constraints(data['constraints'])}

[OPTIMIZATION_GOAL]:
{self._format_instructions(data['ai_instructions'])}

[POST_CONDITION_VERIFICATION]:
{self._format_constraints(data['post_conditions'])}
"""
        
        # Adicionar feedback de erros anteriores (se houver)
        if self.error_feedback:
            prompt += "\n[PREVIOUS_ERRORS]:\n"
            prompt += "O código anterior falhou nas seguintes verificações:\n"
            for i, error in enumerate(self.error_feedback, 1):
                prompt += f"\nErro {i}:\n"
                prompt += f"  Status: {error['status']}\n"
                prompt += f"  Mensagem: {error['message']}\n"
                if error.get('counter_examples'):
                    prompt += "  Contra-exemplos encontrados:\n"
                    for ce in error['counter_examples']:
                        prompt += f"    - {ce['condition']}: falha quando {ce['counter_example']}\n"
            prompt += "\nCORRIJA o algoritmo para suportar essas restrições.\n"
        
        prompt += "\nGere apenas o corpo da função em Rust, focado em performance e segurança de memória.\n"
        
        return prompt
    
    def _format_constraints(self, constraints):
        return '\n'.join([f"  - {self._condition_to_expression(c)}" for c in (constraints or []) if self._condition_to_expression(c)])
    
    def _format_instructions(self, instructions):
        return '\n'.join([f"  - {k}: {v}" for k, v in instructions.items()])
    
    def build_final_artifact(self, generated_code, intent_name):
        """
        Aqui você implementaria a lógica para salvar o código em um arquivo .rs 
        ou enviá-lo para um compilador JIT.
        """
        # Por enquanto, vamos apenas simular o empacotamento
        artifact = f"""// Aethel Artifact v0.2
// Generated from intent: {intent_name}
// Timestamp: {{timestamp}}

{generated_code}
"""
        return artifact

    def feed_error(self, verification_result):
        """
        Injeta feedback de erro no próximo prompt.
        Permite que a IA aprenda com falhas anteriores.
        """
        self.error_feedback.append(verification_result)
        print(f"  📝 Feedback registrado: {verification_result['status']}")
    
    def clear_errors(self):
        """Limpa o histórico de erros"""
        self.error_feedback = []
