# Tasks: Conservation-Checker + Oracle Integration

**Feature**: Conservation-Aware Oracle  
**Version**: v1.7.1  
**Status**: Ready for Implementation  
**Date**: 4 de Fevereiro de 2026

---

## 🎯 Objective

Integrate the Conservation Checker with the Oracle system to ensure that external data (oracle prices, rates, etc.) does not break conservation of value in financial transactions.

**Key Rule**: If an `external` variable affects financial state, the Guardian must validate that the exchange rate/price is within acceptable bounds (Slippage Check).

---

## 📋 Task List

### Phase 1: Oracle-Aware Conservation Detection

- [ ] 1.1 Extend `BalanceChange` to track oracle-influenced changes
- [ ] 1.2 Add `is_oracle_influenced` flag to `BalanceChange`
- [ ] 1.3 Detect when balance changes involve `external` variables
- [ ] 1.4 Extract oracle variable names from balance expressions

### Phase 2: Slippage Check Implementation

- [ ] 2.1 Create `SlippageValidator` class
- [ ] 2.2 Implement `validate_oracle_rate()` method
- [ ] 2.3 Add configurable slippage tolerance (default: 5%)
- [ ] 2.4 Validate oracle-influenced balance changes against bounds

### Phase 3: Conservation Checker Integration

- [ ] 3.1 Update `ConservationChecker.analyze_verify_block()` to detect oracle usage
- [ ] 3.2 Add `check_oracle_conservation()` method
- [ ] 3.3 Integrate slippage validation into conservation flow
- [ ] 3.4 Update error messages to include oracle-specific hints

### Phase 4: Example Implementation

- [ ] 4.1 Create `defi_liquidation_conservation.ae` example
- [ ] 4.2 Demonstrate oracle price with conservation
- [ ] 4.3 Show slippage violation detection
- [ ] 4.4 Document best practices

### Phase 5: Testing

- [ ] 5.1 Unit tests for oracle-aware balance detection
- [ ] 5.2 Unit tests for slippage validation
- [ ] 5.3 Integration test: DeFi liquidation with oracle
- [ ] 5.4 Integration test: Slippage violation detection
- [ ] 5.5 Property test: Conservation with oracle data

### Phase 6: Documentation

- [ ] 6.1 Update Conservation Checker docs with oracle integration
- [ ] 6.2 Create slippage check guide
- [ ] 6.3 Add oracle conservation examples to README
- [ ] 6.4 Update API documentation

---

## 🔍 Detailed Task Descriptions

### Task 1.1: Extend BalanceChange for Oracle Tracking

**Description**: Add fields to `BalanceChange` to track when a balance change is influenced by oracle data.

**Changes**:
```python
@dataclass
class BalanceChange:
    variable_name: str
    amount: Union[int, float, str]
    line_number: int
    is_increase: bool
    is_oracle_influenced: bool = False  # NEW
    oracle_variable: Optional[str] = None  # NEW
    oracle_value: Optional[float] = None  # NEW
```

**Acceptance Criteria**:
- BalanceChange can track oracle influence
- Oracle variable name is stored
- Oracle value is captured when available

---

### Task 2.1: Create SlippageValidator Class

**Description**: Implement a validator that checks if oracle-provided rates/prices are within acceptable bounds.

**Implementation**:
```python
class SlippageValidator:
    def __init__(self, tolerance: float = 0.05):
        self.tolerance = tolerance  # 5% default
    
    def validate_oracle_rate(
        self,
        oracle_value: float,
        expected_range: tuple[float, float]
    ) -> bool:
        """
        Validate that oracle value is within expected range.
        
        Args:
            oracle_value: Value from oracle
            expected_range: (min, max) acceptable values
            
        Returns:
            True if within bounds, False otherwise
        """
        min_val, max_val = expected_range
        return min_val <= oracle_value <= max_val
    
    def calculate_slippage(
        self,
        oracle_value: float,
        reference_value: float
    ) -> float:
        """Calculate slippage percentage."""
        return abs(oracle_value - reference_value) / reference_value
```

**Acceptance Criteria**:
- Slippage calculation is accurate
- Tolerance is configurable
- Validation returns correct boolean

---

### Task 3.2: Add check_oracle_conservation() Method

**Description**: Add method to ConservationChecker that validates conservation when oracles are involved.

**Implementation**:
```python
def check_oracle_conservation(
    self,
    changes: List[BalanceChange],
    oracle_proofs: Dict[str, OracleProof]
) -> ConservationResult:
    """
    Validate conservation with oracle-influenced changes.
    
    Args:
        changes: List of balance changes
        oracle_proofs: Oracle proofs for external variables
        
    Returns:
        ConservationResult with oracle validation
    """
    # 1. Identify oracle-influenced changes
    oracle_changes = [c for c in changes if c.is_oracle_influenced]
    
    # 2. Validate each oracle value
    slippage_validator = SlippageValidator()
    for change in oracle_changes:
        if change.oracle_variable in oracle_proofs:
            proof = oracle_proofs[change.oracle_variable]
            # Validate proof freshness and signature
            # Validate slippage
    
    # 3. Validate overall conservation
    return self.validate_conservation(changes)
```

**Acceptance Criteria**:
- Oracle-influenced changes are identified
- Oracle proofs are validated
- Slippage is checked
- Conservation is validated with oracle data

---

### Task 4.1: Create DeFi Liquidation Example

**Description**: Create a complete example showing oracle-aware conservation in a DeFi liquidation scenario.

**File**: `aethel/examples/defi_liquidation_conservation.ae`

**Content**:
```aethel
# DeFi Liquidation with Oracle-Aware Conservation
intent liquidate_position(
    borrower: Account,
    liquidator: Account,
    collateral_amount: Balance,
    external btc_price: Price
) {
    guard {
        # Oracle validation
        btc_price_verified == true;
        btc_price_fresh == true;
        
        # Liquidation condition
        collateral_value = collateral_amount * btc_price;
        debt_value > collateral_value * 1.5;  # Under-collateralized
        
        # Old values
        old_borrower_collateral == borrower_collateral;
        old_liquidator_balance == liquidator_balance;
    }
    
    verify {
        # Conservation with oracle-influenced values
        borrower_collateral == old_borrower_collateral - collateral_amount;
        liquidator_balance == old_liquidator_balance + collateral_amount;
        
        # Slippage check: btc_price within 5% of reference
        btc_price >= reference_price * 0.95;
        btc_price <= reference_price * 1.05;
    }
}
```

**Acceptance Criteria**:
- Example compiles without errors
- Conservation is validated
- Oracle price is checked
- Slippage bounds are enforced

---

### Task 5.3: Integration Test - DeFi with Oracle

**Description**: Create integration test that validates conservation with oracle data in a DeFi scenario.

**File**: `test_conservation_oracle_integration.py`

**Test Cases**:
1. Valid liquidation with oracle price
2. Conservation violation with oracle
3. Slippage violation detection
4. Multiple oracle values in one transaction

**Acceptance Criteria**:
- All test cases pass
- Conservation is validated correctly
- Oracle integration works end-to-end
- Error messages are clear

---

## 🎯 Success Criteria

### Phase 1 Complete When:
- ✅ BalanceChange tracks oracle influence
- ✅ Oracle variables are detected
- ✅ Tests pass

### Phase 2 Complete When:
- ✅ SlippageValidator implemented
- ✅ Slippage calculation accurate
- ✅ Tolerance configurable
- ✅ Tests pass

### Phase 3 Complete When:
- ✅ ConservationChecker detects oracle usage
- ✅ Oracle conservation validated
- ✅ Integration with existing code
- ✅ Tests pass

### Phase 4 Complete When:
- ✅ DeFi example created
- ✅ Example demonstrates all features
- ✅ Documentation complete

### Phase 5 Complete When:
- ✅ All unit tests pass
- ✅ All integration tests pass
- ✅ Property tests pass
- ✅ Coverage > 90%

### Phase 6 Complete When:
- ✅ Documentation updated
- ✅ Examples documented
- ✅ API docs complete
- ✅ README updated

---

## 📊 Estimated Effort

- **Phase 1**: 30 minutes
- **Phase 2**: 45 minutes
- **Phase 3**: 60 minutes
- **Phase 4**: 30 minutes
- **Phase 5**: 45 minutes
- **Phase 6**: 30 minutes

**Total**: ~4 hours

---

## 🔗 Dependencies

- ✅ Oracle system (v1.7.0) - COMPLETE
- ✅ Conservation Checker (v1.3.0) - EXISTS
- ✅ Parser with `external` keyword - COMPLETE
- ⏳ Integration code - TO BE IMPLEMENTED

---

## 📝 Notes

### Design Decisions

1. **Slippage Tolerance**: Default 5%, configurable per transaction
2. **Oracle Validation**: Happens before conservation check
3. **Error Messages**: Include both conservation and oracle errors
4. **Performance**: O(n) complexity maintained

### Future Enhancements (v1.8.0)

- Multi-oracle consensus for slippage
- Dynamic slippage based on market volatility
- Oracle reputation integration
- Historical price validation

---

**Status**: Ready for Implementation  
**Next**: Start with Phase 1 - Oracle-Aware Conservation Detection

🔮✨🛡️⚡🌌
