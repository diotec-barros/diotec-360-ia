# Diotec360 v5.0 - STATISTICS

*Generated automatically by Genesis Statistics Generator*

## Lines of Code

**Total Files**: 395
**Total Lines**: 129,598
**Code Lines**: 93,563

### By Category

| Category | Files | Total Lines | Code Lines |
|----------|-------|-------------|------------|
| Ai | 25 | 9,835 | 7,520 |
| Benchmarks | 13 | 4,112 | 3,030 |
| Commercial | 5 | 1,570 | 1,208 |
| Consensus | 16 | 6,996 | 5,142 |
| Core Engine | 84 | 31,036 | 23,282 |
| Demos | 59 | 19,216 | 14,280 |
| Examples | 29 | 3,740 | 1,825 |
| Lattice | 8 | 4,147 | 3,077 |
| Other | 13 | 587 | 339 |
| Plugins | 5 | 840 | 648 |
| Stdlib | 9 | 1,188 | 800 |
| Tests | 121 | 44,960 | 31,584 |
| Trading | 8 | 1,371 | 828 |

## Test Coverage

**Total Test Files**: 121
- Unit Tests: 73
- Property Tests: 39
- Integration Tests: 9

**Total Assertions**: 3,295
**Property Tests**: 192

## Invariants & Properties

**Total Invariants**: 270

### Conservation Laws
**Count**: 258

1. battery_level >= battery_min;
2. altitude > altitude_min;
3. angular_velocity < velocity_max;
4. current_angle >= angle_min;
5. angle >= reentry_min;
6. angle <= reentry_max;
7. altitude > altitude_zero;
8. if payout_amount > 0 {
9. oracle_confidence >= 95;
10. new_portfolio_value == portfolio_value;
... and 248 more

### Trading Invariants
**Count**: 12

1. new_total_capital == total_capital + realized_pnl;
2. let actual_takashi = takashi_current_value * 10000 / new_total_capital;
3. let actual_simons = simons_current_value * 10000 / new_total_capital;
4. let actual_dalio = dalio_current_value * 10000 / new_total_capital;
5. abs(actual_takashi - takashi_allocation) <= rebalance_threshold;
6. abs(actual_simons - simons_allocation) <= rebalance_threshold;
7. abs(actual_dalio - dalio_allocation) <= rebalance_threshold;
8. let current_drawdown = (peak_capital - new_total_capital) * 10000 / peak_capital;
9. current_drawdown <= max_drawdown;
10. for position in all_positions {
... and 2 more

## Performance Metrics

**Consensus Finality**: 30.00 s

## Summary

Diotec360 v5.0 consists of **93,563 lines of code** across **395 files**, 
protected by **121 test files** with **3,295 assertions** 
and **270 mathematical invariants**.
