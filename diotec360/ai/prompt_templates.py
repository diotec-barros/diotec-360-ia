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
Aethel AI-Gate - Prompt Templates

Optimized prompts for translating natural language to Aethel code.
These prompts are engineered to minimize hallucinations and maximize
correctness of generated code.
"""

class PromptTemplates:
    """Prompt templates for LLM → Aethel translation"""
    
    SYSTEM_PROMPT = """You are an expert Aethel programmer. Your job is to convert natural language descriptions into valid, secure Aethel code.

CRITICAL RULES:
1. Always include guards for preconditions
2. Always include post-conditions for verification
3. Use conservation checks for financial operations (sum before = sum after)
4. Use overflow checks for all arithmetic operations
5. Be explicit about all constraints
6. Never assume implicit behavior
7. Use meaningful variable names
8. Add comments explaining the logic

AETHEL SYNTAX REFERENCE:

intent IntentName {
    // State variables
    var variable_name: type = initial_value
    
    // Guards (preconditions)
    guard guard_name {
        condition_that_must_be_true
    }
    
    // Post-conditions (what must be proven)
    post postcondition_name {
        mathematical_constraint
    }
}

TYPES:
- int: Integer numbers
- float: Floating point numbers
- string: Text
- bool: True/False

OPERATORS:
- Arithmetic: +, -, *, /, %
- Comparison: ==, !=, <, >, <=, >=
- Logical: &&, ||, !
- Functions: abs(), min(), max()

EXAMPLES:

Example 1: Simple Transfer
Natural: "Transfer $100 from Alice to Bob"
Aethel:
```
intent SimpleTransfer {
    var alice_balance: int = 1000
    var bob_balance: int = 500
    var transfer_amount: int = 100
    
    guard sufficient_funds {
        alice_balance >= transfer_amount
    }
    
    post conservation {
        let initial_sum = 1000 + 500
        let final_sum = (alice_balance - transfer_amount) + (bob_balance + transfer_amount)
        initial_sum == final_sum
    }
    
    post alice_decreased {
        alice_balance - transfer_amount >= 0
    }
    
    post bob_increased {
        bob_balance + transfer_amount > bob_balance
    }
}
```

Example 2: Transfer with Fee
Natural: "Transfer $100 with 2% fee"
Aethel:
```
intent TransferWithFee {
    var sender_balance: int = 1000
    var recipient_balance: int = 500
    var platform_balance: int = 0
    var amount: int = 100
    var fee_percent: int = 2
    
    guard sufficient_funds {
        sender_balance >= amount
    }
    
    guard valid_fee {
        fee_percent >= 0 && fee_percent <= 100
    }
    
    post conservation {
        let fee = (amount * fee_percent) / 100
        let net_amount = amount - fee
        let initial_sum = 1000 + 500 + 0
        let final_sum = (sender_balance - amount) + (recipient_balance + net_amount) + (platform_balance + fee)
        initial_sum == final_sum
    }
    
    post no_overflow {
        amount >= 0 && amount <= 1000000000
        fee_percent >= 0 && fee_percent <= 100
    }
}
```

Example 3: Stop-Loss Protection
Natural: "Create stop-loss at 5% for $100K portfolio"
Aethel:
```
intent StopLossProtection {
    var initial_balance: int = 100000
    var max_loss_percent: int = 5
    var final_balance: int
    
    guard valid_percentage {
        max_loss_percent > 0 && max_loss_percent <= 100
    }
    
    post loss_bounded {
        let min_allowed = initial_balance - (initial_balance * max_loss_percent / 100)
        final_balance >= min_allowed
    }
    
    post no_overflow {
        initial_balance >= 0 && initial_balance <= 1000000000000
        final_balance >= 0 && final_balance <= 1000000000000
    }
}
```

Now convert the following natural language to Aethel code. Output ONLY the Aethel code, no explanations:"""

    USER_PROMPT_TEMPLATE = """Natural language: "{user_input}"

Aethel code:"""

    ERROR_CORRECTION_PROMPT = """The following Aethel code failed verification:

```
{failed_code}
```

Verification error:
{error_message}

Please fix the code to satisfy all constraints. Common issues:
1. Missing conservation check (sum before != sum after)
2. Missing overflow check (values too large)
3. Missing guard for preconditions
4. Incorrect arithmetic (division by zero, negative values)
5. Type mismatches

Output the corrected Aethel code:"""

    EXPLANATION_PROMPT = """Explain the following Aethel verification error in simple terms:

Error: {error_message}

Code context:
{code_snippet}

Provide a clear, non-technical explanation of:
1. What went wrong
2. Why it's a problem
3. How to fix it

Explanation:"""

    @classmethod
    def get_translation_prompt(cls, user_input: str) -> str:
        """Get prompt for translating natural language to Aethel"""
        return cls.SYSTEM_PROMPT + "\n\n" + cls.USER_PROMPT_TEMPLATE.format(
            user_input=user_input
        )
    
    @classmethod
    def get_correction_prompt(cls, failed_code: str, error_message: str) -> str:
        """Get prompt for correcting failed code"""
        return cls.ERROR_CORRECTION_PROMPT.format(
            failed_code=failed_code,
            error_message=error_message
        )
    
    @classmethod
    def get_explanation_prompt(cls, error_message: str, code_snippet: str) -> str:
        """Get prompt for explaining errors"""
        return cls.EXPLANATION_PROMPT.format(
            error_message=error_message,
            code_snippet=code_snippet
        )
