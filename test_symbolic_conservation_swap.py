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

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from diotec360.core.parser import DIOTEC360Parser
from diotec360.core.judge import DIOTEC360Judge


def _run(code: str, intent_name: str) -> dict:
    parser = DIOTEC360Parser()
    intent_map = parser.parse(code)
    judge = DIOTEC360Judge(intent_map)
    return judge.verify_logic(intent_name)


def test_multi_party_swap_symbolic_conservation() -> bool:
    """Stress test: conservation with symbolic amounts must be proved via Z3 (no fail-open)."""

    good_code = """
intent multiparty_swap(
    maker_a: Account,
    maker_b: Account,
    taker_a: Account,
    taker_b: Account,
    amount_a: Balance,
    amount_b: Balance
) {
    guard {
        amount_a > 0;
        amount_b > 0;
        old_maker_a_balance == 1000;
        old_maker_b_balance == 2000;
        old_taker_a_balance == 3000;
        old_taker_b_balance == 4000;
    }

    solve {
        priority: security;
        target: dex;
    }

    verify {
        maker_a_balance == old_maker_a_balance - amount_a;
        taker_a_balance == old_taker_a_balance + amount_a;
        maker_b_balance == old_maker_b_balance + amount_b;
        taker_b_balance == old_taker_b_balance - amount_b;
    }
}
"""

    bad_code = """
intent multiparty_swap_broken(
    maker_a: Account,
    taker_a: Account,
    amount_a: Balance
) {
    guard {
        amount_a > 0;
        old_maker_a_balance == 1000;
        old_taker_a_balance == 3000;
    }

    solve {
        priority: security;
        target: dex;
    }

    verify {
        maker_a_balance == old_maker_a_balance + amount_a;
        taker_a_balance == old_taker_a_balance + amount_a;
    }
}
"""

    good_result = _run(good_code, "multiparty_swap")
    if good_result.get("status") != "PROVED":
        print("[FAIL] Expected PROVED for good swap")
        print(good_result)
        return False

    bad_result = _run(bad_code, "multiparty_swap_broken")
    if bad_result.get("status") != "FAILED":
        print("[FAIL] Expected FAILED for broken swap (should violate conservation under amount_a > 0)")
        print(bad_result)
        return False

    print("[OK] Symbolic conservation enforced via Z3")
    return True


if __name__ == "__main__":
    ok = test_multi_party_swap_symbolic_conservation()
    raise SystemExit(0 if ok else 1)
