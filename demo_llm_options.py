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
Demo: LLM Options for Aethel AI-Gate

Shows how to use:
1. Local LLM (Ollama) - Free, Private
2. Commercial API (OpenAI) - Paid, Managed
3. Hybrid (Best of both)

Run: python demo_llm_options.py
"""

from diotec360.ai.llm_config import LLMConfig, LLMPresets


def demo_local_llm():
    """Demo: Local LLM (Ollama)"""
    print("=" * 60)
    print("DEMO 1: LOCAL LLM (OLLAMA)")
    print("=" * 60)
    
    # Configure local LLM
    config = LLMConfig.local("ollama", model="llama3")
    
    print(f"\n✓ Provider: {config.provider.value}")
    print(f"✓ Model: {config.model}")
    print(f"✓ Endpoint: {config.endpoint}")
    print(f"✓ API Key: {config.api_key or 'Not required'}")
    print(f"✓ Cost per 1K tokens: ${config.cost_per_1k_input:.4f} (FREE!)")
    
    # Estimate cost for 10,000 translations
    input_tokens = 10000 * 100  # 100 tokens per translation
    output_tokens = 10000 * 200  # 200 tokens per response
    cost = config.estimate_cost(input_tokens, output_tokens)
    
    print(f"\n📊 Cost for 10,000 translations:")
    print(f"   Input tokens: {input_tokens:,}")
    print(f"   Output tokens: {output_tokens:,}")
    print(f"   Total cost: ${cost:.2f} (FREE!)")
    
    print(f"\n✅ Advantages:")
    print(f"   • Zero API costs")
    print(f"   • 100% privacy (data stays local)")
    print(f"   • No rate limits")
    print(f"   • No vendor lock-in")
    
    print(f"\n⚠️  Requirements:")
    print(f"   • Hardware: 16GB RAM, 8GB GPU (optional)")
    print(f"   • Install: curl -fsSL https://ollama.ai/install.sh | sh")
    print(f"   • Download model: ollama pull llama3")


def demo_commercial_api():
    """Demo: Commercial API (OpenAI)"""
    print("\n" + "=" * 60)
    print("DEMO 2: COMMERCIAL API (OPENAI GPT-4)")
    print("=" * 60)
    
    # Configure OpenAI (mock key for demo)
    config = LLMConfig.api(
        provider="openai",
        api_key="sk-demo-key-not-real",
        model="gpt-4-turbo"
    )
    
    print(f"\n✓ Provider: {config.provider.value}")
    print(f"✓ Model: {config.model}")
    print(f"✓ Endpoint: {config.endpoint}")
    print(f"✓ API Key: {config.api_key[:10]}... (hidden)")
    print(f"✓ Cost per 1K tokens:")
    print(f"   - Input: ${config.cost_per_1k_input:.4f}")
    print(f"   - Output: ${config.cost_per_1k_output:.4f}")
    
    # Estimate cost for 10,000 translations
    input_tokens = 10000 * 100
    output_tokens = 10000 * 200
    cost = config.estimate_cost(input_tokens, output_tokens)
    
    print(f"\n📊 Cost for 10,000 translations:")
    print(f"   Input tokens: {input_tokens:,}")
    print(f"   Output tokens: {output_tokens:,}")
    print(f"   Total cost: ${cost:.2f}")
    print(f"   Monthly: ${cost:.2f}")
    print(f"   Annual: ${cost * 12:.2f}")
    
    print(f"\n✅ Advantages:")
    print(f"   • Best quality (GPT-4)")
    print(f"   • No infrastructure management")
    print(f"   • Fast to start")
    print(f"   • Always up-to-date")
    
    print(f"\n⚠️  Considerations:")
    print(f"   • Pay per use")
    print(f"   • Data sent to OpenAI")
    print(f"   • Rate limits apply")
    print(f"   • Vendor dependency")


def demo_hybrid_approach():
    """Demo: Hybrid (Local + API Fallback)"""
    print("\n" + "=" * 60)
    print("DEMO 3: HYBRID (LOCAL + API FALLBACK)")
    print("=" * 60)
    
    # Primary: Local LLM
    primary = LLMConfig.local("ollama", "llama3")
    
    # Fallback: OpenAI API
    fallback = LLMConfig.api(
        "openai",
        "sk-demo-key",
        "gpt-4-turbo"
    )
    
    print(f"\n✓ Primary: {primary.provider.value} ({primary.model})")
    print(f"   Cost: ${primary.cost_per_1k_input:.4f} per 1K tokens (FREE)")
    
    print(f"\n✓ Fallback: {fallback.provider.value} ({fallback.model})")
    print(f"   Cost: ${fallback.cost_per_1k_input:.4f} per 1K tokens")
    
    # Estimate hybrid cost (90% local, 10% API)
    total_translations = 10000
    local_translations = int(total_translations * 0.9)
    api_translations = int(total_translations * 0.1)
    
    local_cost = 0.0  # Free
    api_cost = fallback.estimate_cost(
        api_translations * 100,
        api_translations * 200
    )
    total_cost = local_cost + api_cost
    
    print(f"\n📊 Cost for 10,000 translations (90% local, 10% API):")
    print(f"   Local: {local_translations:,} translations = ${local_cost:.2f}")
    print(f"   API: {api_translations:,} translations = ${api_cost:.2f}")
    print(f"   Total: ${total_cost:.2f}")
    print(f"   Savings vs 100% API: ${fallback.estimate_cost(1000000, 2000000) - total_cost:.2f}")
    
    print(f"\n✅ Best of Both Worlds:")
    print(f"   • 90% cost savings (local)")
    print(f"   • High availability (fallback)")
    print(f"   • Quality guaranteed (API for complex cases)")
    print(f"   • Privacy for most data (local)")


def demo_cost_comparison():
    """Demo: Cost Comparison"""
    print("\n" + "=" * 60)
    print("DEMO 4: COST COMPARISON (10,000 translations/month)")
    print("=" * 60)
    
    scenarios = [
        ("Ollama Local (Llama 3)", LLMConfig.local("ollama", "llama3")),
        ("OpenAI GPT-4", LLMConfig.api("openai", "sk-demo", "gpt-4-turbo")),
        ("OpenAI GPT-3.5", LLMConfig.api("openai", "sk-demo", "gpt-3.5-turbo")),
        ("Google Gemini", LLMConfig.api("google", "demo", "gemini-pro")),
        ("Cohere Command", LLMConfig.api("cohere", "demo", "command")),
    ]
    
    # Update costs for GPT-3.5
    scenarios[2][1].cost_per_1k_input = 0.0005
    scenarios[2][1].cost_per_1k_output = 0.0015
    
    print(f"\n{'Provider':<25} {'Monthly':<12} {'Annual':<12} {'Privacy'}")
    print("-" * 60)
    
    for name, config in scenarios:
        monthly_cost = config.estimate_cost(1000000, 2000000)
        annual_cost = monthly_cost * 12
        privacy = "100%" if config.is_local() else "Depends"
        
        print(f"{name:<25} ${monthly_cost:>10.2f}  ${annual_cost:>10.2f}  {privacy}")
    
    # Hybrid scenario
    hybrid_cost = scenarios[1][1].estimate_cost(100000, 200000)  # 10% of API
    print(f"{'Hybrid (90% local)':<25} ${hybrid_cost:>10.2f}  ${hybrid_cost * 12:>10.2f}  90%")


def demo_business_model():
    """Demo: Business Model for DIOTEC 360"""
    print("\n" + "=" * 60)
    print("DEMO 5: BUSINESS MODEL FOR DIOTEC 360")
    print("=" * 60)
    
    print("\n📦 TIER 1: BYOL (Bring Your Own LLM)")
    print("   Price: $500/month")
    print("   Client provides: Local LLM (Ollama)")
    print("   You provide: Aethel platform")
    print("   Your cost: $0 (no API)")
    print("   Your margin: $500/month (100%)")
    
    print("\n📦 TIER 2: MANAGED AI (BASIC)")
    print("   Price: $1,500/month")
    print("   Includes: 10K GPT-4 tokens/month")
    print("   Your cost: ~$300 (OpenAI)")
    print("   Your margin: $1,200/month (80%)")
    
    print("\n📦 TIER 3: MANAGED AI (PRO)")
    print("   Price: $5,000/month")
    print("   Includes: 100K GPT-4 tokens/month")
    print("   Your cost: ~$1,000 (OpenAI)")
    print("   Your margin: $4,000/month (80%)")
    
    print("\n📦 TIER 4: ENTERPRISE")
    print("   Price: $50,000/month")
    print("   Includes: Unlimited (hybrid)")
    print("   Your cost: ~$5,000 (infrastructure + API)")
    print("   Your margin: $45,000/month (90%)")
    
    print("\n📊 REVENUE PROJECTION (50 clients)")
    print("   20 BYOL clients: 20 × $500 = $10,000/month")
    print("   20 Basic clients: 20 × $1,500 = $30,000/month")
    print("   8 Pro clients: 8 × $5,000 = $40,000/month")
    print("   2 Enterprise: 2 × $50,000 = $100,000/month")
    print("   " + "-" * 50)
    print("   Total: $180,000/month")
    print("   Annual: $2,160,000/year")
    print("   Your costs: ~$30,000/year (API)")
    print("   Net profit: $2,130,000/year")


def demo_quick_start():
    """Demo: Quick Start Guide"""
    print("\n" + "=" * 60)
    print("DEMO 6: QUICK START (5 MINUTES)")
    print("=" * 60)
    
    print("\n🚀 STEP 1: Install Ollama (2 minutes)")
    print("   Windows: https://ollama.ai/download")
    print("   Linux/Mac: curl -fsSL https://ollama.ai/install.sh | sh")
    
    print("\n🚀 STEP 2: Download Model (2 minutes)")
    print("   ollama pull llama3")
    
    print("\n🚀 STEP 3: Test AI-Gate (1 minute)")
    print("   python")
    print("   >>> from diotec360.ai import AIGate, LLMConfig")
    print("   >>> config = LLMConfig.local('ollama', 'llama3')")
    print("   >>> gate = AIGate(config=config)")
    print("   >>> result = gate.voice_to_code('Transfer $100')")
    print("   >>> print(result.aethel_code)")
    
    print("\n✅ DONE! You now have:")
    print("   • Free LLM running locally")
    print("   • AI-Gate translating voice to verified code")
    print("   • Zero API costs")
    print("   • 100% privacy")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("AETHEL AI-GATE: LLM OPTIONS DEMO")
    print("=" * 60)
    print("\nThis demo shows how to use different LLM options:")
    print("1. Local LLM (Ollama) - Free, Private")
    print("2. Commercial API (OpenAI) - Paid, Managed")
    print("3. Hybrid - Best of Both Worlds")
    
    # Run all demos
    demo_local_llm()
    demo_commercial_api()
    demo_hybrid_approach()
    demo_cost_comparison()
    demo_business_model()
    demo_quick_start()
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("\n✅ Aethel supports:")
    print("   • Local LLMs (Ollama, LM Studio, llama.cpp)")
    print("   • Commercial APIs (OpenAI, Anthropic, Google, Cohere)")
    print("   • Hybrid (Local + API fallback)")
    print("   • Custom endpoints")
    
    print("\n💰 Business Model:")
    print("   • BYOL: $500/month (100% margin)")
    print("   • Managed: $1,500-50,000/month (80-90% margin)")
    print("   • Target: $2.16M/year with 50 clients")
    
    print("\n🚀 Next Steps:")
    print("   1. Install Ollama: https://ollama.ai")
    print("   2. Test AI-Gate locally")
    print("   3. Create PayPal Business account")
    print("   4. Launch diotec360.com")
    
    print("\n" + "=" * 60)
    print("[STATUS: READY FOR PRODUCTION]")
    print("=" * 60)
