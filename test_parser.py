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

import json
from diotec360.core.parser import DIOTEC360Parser


# --- TESTE DO PARSER ---
code = """
intent transfer_funds(sender: Account, receiver: Account, amount: Gold) {
    guard {
        sender_balance >= amount;
        amount > 0;
    }
    solve {
        priority: speed;
        target: blockchain;
    }
    verify {
        sender_balance < old_balance;
    }
}
"""

parser = DIOTEC360Parser()
ast = parser.parse(code)

print(json.dumps(ast, indent=4))
