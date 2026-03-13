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
Aethel Standard Library v2.0.1 - Complete Demo

Demonstrates all proven financial functions:
- Interest calculations (v2.0.0)
- Loan amortization (v2.0.1)
- Risk metrics (v2.0.1)
"""

from diotec360.stdlib.financial import (
    # Interest
    simple_interest,
    compound_interest,
    
    # Amortization
    loan_payment,
    amortization_schedule,
    
    # Risk
    value_at_risk,
    sharpe_ratio,
    sortino_ratio
)


def demo_loan_amortization():
    """Demo: Loan Amortization"""
    print("=" * 80)
    print("DEMO 1: LOAN AMORTIZATION")
    print("Calculate monthly payments and amortization schedules")
    print("=" * 80)
    
    # Test case: $200,000 mortgage at 6% for 30 years
    principal = 20000000  # $200,000 in cents
    rate = 600  # 6% annual
    months = 360  # 30 years
    
    print(f"\nLoan Details:")
    print(f"  Principal: ${principal/100:,.2f}")
    print(f"  Annual Rate: {rate/100:.2f}%")
    print(f"  Term: {months} months ({months//12} years)")
    print("-" * 80)
    
    # Calculate monthly payment
    payment = loan_payment(principal, rate, months)
    
    print(f"\n✓ Monthly Payment: ${payment.monthly_payment/100:,.2f}")
    print(f"✓ Total Payment: ${payment.total_payment/100:,.2f}")
    print(f"✓ Total Interest: ${payment.total_interest/100:,.2f}")
    print(f"✓ Interest/Principal Ratio: {payment.total_interest/principal:.2f}x")
    print(f"✓ Proof: {payment.proof_certificate[:60]}...")
    
    # Generate full amortization schedule
    print(f"\n\nGenerating complete amortization schedule...")
    schedule = amortization_schedule(principal, rate, months)
    
    print(f"\n✓ Schedule generated: {len(schedule.schedule)} payments")
    print(f"✓ Total Principal: ${schedule.total_principal/100:,.2f}")
    print(f"✓ Total Interest: ${schedule.total_interest/100:,.2f}")
    print(f"✓ Final Balance: ${schedule.schedule[-1].balance/100:,.2f}")
    
    # Show first 3 and last 3 payments
    print(f"\n\nFirst 3 Payments:")
    print(f"{'Period':<8} {'Payment':<12} {'Principal':<12} {'Interest':<12} {'Balance':<15}")
    print("-" * 80)
    for entry in schedule.schedule[:3]:
        print(f"{entry.period:<8} ${entry.payment/100:<11,.2f} ${entry.principal/100:<11,.2f} "
              f"${entry.interest/100:<11,.2f} ${entry.balance/100:<14,.2f}")
    
    print(f"\n...")
    
    print(f"\nLast 3 Payments:")
    print(f"{'Period':<8} {'Payment':<12} {'Principal':<12} {'Interest':<12} {'Balance':<15}")
    print("-" * 80)
    for entry in schedule.schedule[-3:]:
        print(f"{entry.period:<8} ${entry.payment/100:<11,.2f} ${entry.principal/100:<11,.2f} "
              f"${entry.interest/100:<11,.2f} ${entry.balance/100:<14,.2f}")
    
    print("\n" + "=" * 80)
    print("OBSERVATION: Interest decreases, Principal increases over time")
    print("=" * 80)


def demo_value_at_risk():
    """Demo: Value at Risk (VaR)"""
    print("\n\n" + "=" * 80)
    print("DEMO 2: VALUE AT RISK (VaR)")
    print("Measure potential portfolio losses")
    print("=" * 80)
    
    # Simulate historical returns (in basis points)
    # Representing a volatile portfolio
    returns = [
        -1200, -800, -500, -300, -200, -100, 0, 50, 100, 150,
        200, 250, 300, 350, 400, 450, 500, 550, 600, 650,
        700, 750, 800, 850, 900, 950, 1000, 1050, 1100, 1150,
        -900, -600, -400, -250, -150, -50, 25, 75, 125, 175,
        225, 275, 325, 375, 425, 475, 525, 575, 625, 675
    ]  # 50 data points
    
    portfolio_value = 100000000  # $1,000,000
    
    print(f"\nPortfolio Value: ${portfolio_value/100:,.2f}")
    print(f"Historical Returns: {len(returns)} periods")
    print(f"Mean Return: {sum(returns)//len(returns)} bps ({sum(returns)//len(returns)/100:.2f}%)")
    print("-" * 80)
    
    # Calculate VaR at different confidence levels
    confidence_levels = [9000, 9500, 9900, 9950]
    
    print(f"\n{'Confidence':<15} {'VaR Amount':<20} {'Interpretation'}")
    print("-" * 80)
    
    for conf in confidence_levels:
        var = value_at_risk(portfolio_value, returns, conf)
        conf_pct = conf / 100
        print(f"{conf_pct:.2f}%{'':<10} ${var.var_amount/100:<19,.2f} "
              f"{100-conf_pct:.2f}% chance of losing more")
    
    # Detailed analysis for 95% confidence
    var_95 = value_at_risk(portfolio_value, returns, 9500)
    
    print(f"\n\nDetailed Analysis (95% Confidence):")
    print("-" * 80)
    print(f"✓ VaR Amount: ${var_95.var_amount/100:,.2f}")
    print(f"✓ Percentile Return: {var_95.percentile_return} bps ({var_95.percentile_return/100:.2f}%)")
    print(f"✓ Interpretation: 95% confident we won't lose more than ${var_95.var_amount/100:,.2f}")
    print(f"✓ Or: Only 5% chance of losing more than ${var_95.var_amount/100:,.2f}")
    print(f"✓ Proof: {var_95.proof_certificate[:60]}...")
    
    print("\n" + "=" * 80)
    print("✅ VaR PROVIDES QUANTITATIVE RISK MEASUREMENT")
    print("=" * 80)


def demo_sharpe_sortino():
    """Demo: Sharpe and Sortino Ratios"""
    print("\n\n" + "=" * 80)
    print("DEMO 3: SHARPE & SORTINO RATIOS")
    print("Measure risk-adjusted returns")
    print("=" * 80)
    
    # Three different investment strategies
    strategies = {
        "Conservative": [100, 150, 200, 150, 100, 150, 200, 150, 100, 150, 200, 150] * 2,
        "Balanced": [-200, 300, -100, 4