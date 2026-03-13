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
DEMO: Virtual Card Gateway - Automated Sales Presentation
==========================================================

Non-interactive version for automated testing and presentations.

Author: Kiro AI - Chief Engineer
Version: v2.2.7 "Virtual Nexus"
Date: February 11, 2026
"""

import time
from demo_virtual_card import (
    print_scene_header,
    print_subsection,
    demo_scene_1_sovereign_creation,
    demo_scene_2_protected_spending,
    demo_scene_3_atomic_destruction,
    demo_statistics_report
)


def main():
    """Run complete sales demo without user interaction"""
    print("\n" + "╔" + "═" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "  AETHEL VIRTUAL CARD GATEWAY - SALES DEMONSTRATION".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("║" + "  Target: Angolan Banks (BAI, BFA, BIC)".center(78) + "║")
    print("║" + "  Value Proposition: The Unbreakable Card".center(78) + "║")
    print("║" + "  Business Model: $0.10 per transaction".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "═" * 78 + "╝")
    
    print("\n🎯 EXECUTIVE SUMMARY:")
    print("   • Mathematical validation prevents fraud")
    print("   • Ghost Identity protects customer privacy")
    print("   • Single-use cards self-destruct after use")
    print("   • Real-time forex integration")
    print("   • Complete audit trail with cryptographic seals")
    print("   • Revenue: $3M-$10M ARR potential")
    
    print("\n" + "─" * 80)
    print("Starting automated demonstration...")
    print("─" * 80)
    
    # Scene 1: Create card
    virtual_card, physical_card, account = demo_scene_1_sovereign_creation()
    
    if virtual_card:
        time.sleep(1)
        
        # Scene 2: Use card
        success = demo_scene_2_protected_spending(virtual_card, account)
        
        if success:
            time.sleep(1)
            
            # Scene 3: Destruction
            demo_scene_3_atomic_destruction(virtual_card, physical_card)
            
            time.sleep(1)
            
            # Scene 4: Statistics
            demo_statistics_report()
    
    # Final message
    print("\n" + "╔" + "═" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "  DEMONSTRATION COMPLETE".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("║" + "  Next Steps:".center(78) + "║")
    print("║" + "  1. Technical integration with BAI systems".center(78) + "║")
    print("║" + "  2. Pilot program with 1,000 customers".center(78) + "║")
    print("║" + "  3. Full deployment across Angola".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("║" + "  Contact: DIOTEC 360 - Dionísio Sebastião Barros".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "═" * 78 + "╝")
    
    print("\n✨ Thank you for your time!")
    print("🚀 Ready to revolutionize virtual card issuance in Angola!")


if __name__ == "__main__":
    main()
