# Oracle Sanctuary - Requirements Specification

**Version**: v1.7.0  
**Status**: DRAFT  
**Author**: Kiro + Arquiteto  
**Date**: 4 de Fevereiro de 2026

---

## 🎯 Vision

**"Bring the world into the proof without breaking the trust."**

Aethel can prove mathematical truths, but it lives in isolation. The Oracle Sanctuary will allow Aethel to consume real-world data (prices, weather, events) while maintaining the same level of formal verification.

---

## 🔮 The Problem

### Current State
```aethel
intent check_insurance(patient: Person, treatment: Treatment) {
    guard {
        treatment_cost < 10000;  # Hardcoded!
    }
    verify {
        insurance_covers == true;
    }
}
```

**Problem**: The cost is hardcoded. In reality, it comes from an external database.

### Desired State
```aethel
intent check_insurance(patient: Person, treatment: Treatment) {
    guard {
        external treatment_cost from oracle("healthcare_db");
        treatment_cost < insurance_limit;
    }
    verify {
        insurance_covers == true;
    }
}
```

**Solution**: The `external` keyword fetches data from a trusted oracle, but only if it comes with a cryptographic proof.

---

## 🏗️ Requirements

### FR1: `external` Keyword
- **Description**: Declare that a variable comes from outside the system
- **Syntax**: `external <var_name> from oracle("<oracle_id>");`
- **Behavior**: Parser accepts it, Judge requires proof

### FR2: Oracle Registry
- **Description**: Whitelist of trusted oracles
- **Storage**: `.aethel_vault/oracles.json`
- **Fields**: `oracle_id`, `public_key`, `endpoint`, `reputation`

### FR3: Cryptographic Proof Verification
- **Description**: Every external value must come with a signature
- **Algorithm**: Ed25519 or ECDSA
- **Format**: `{value, timestamp, signature}`

### FR4: Chainlink Integration (Phase 1)
- **Description**: Support Chainlink Price Feeds
- **Oracles**: ETH/USD, BTC/USD, etc.
- **Proof**: Chainlink's aggregated signatures

### FR5: Band Protocol Integration (Phase 2)
- **Description**: Support Band Protocol data feeds
- **Oracles**: Weather, sports, custom APIs
- **Proof**: Band's validator signatures

### FR6: Timeout Protection
- **Description**: Oracle calls must complete within timeout
- **Default**: 5 seconds
- **Behavior**: If timeout, verification fails

### FR7: Fallback Values
- **Description**: Optional fallback if oracle is down
- **Syntax**: `external price from oracle("chainlink") fallback 1000;`
- **Behavior**: Use fallback only if oracle unreachable

### FR8: Oracle Reputation System
- **Description**: Track oracle reliability
- **Metrics**: Uptime, response time, signature validity
- **Action**: Warn if oracle reputation drops below threshold

---

## 🛡️ Security Requirements

### SR1: No Unsigned Data
- **Rule**: Judge MUST reject any external value without valid signature
- **Reason**: Prevent data injection attacks

### SR2: Timestamp Validation
- **Rule**: External data must be recent (< 5 minutes old)
- **Reason**: Prevent replay attacks

### SR3: Oracle Sandboxing
- **Rule**: Oracle calls run in isolated environment
- **Reason**: Prevent oracle from accessing system resources

### SR4: Rate Limiting
- **Rule**: Max 10 oracle calls per verification
- **Reason**: Prevent DoS via expensive oracle calls

### SR5: Audit Trail
- **Rule**: All oracle calls logged with signature
- **Reason**: Enable post-mortem analysis

---

## 📊 Use Cases

### UC1: DeFi Price Oracle
```aethel
intent liquidate_position(user: Account, collateral: Token) {
    guard {
        external eth_price from oracle("chainlink_eth_usd");
        collateral_value = collateral_amount * eth_price;
        collateral_value < debt_value * 1.5;  # Under-collateralized
    }
    verify {
        user_liquidated == true;
    }
}
```

### UC2: Weather-Based Insurance
```aethel
intent payout_crop_insurance(farmer: Account, location: GPS) {
    guard {
        external rainfall from oracle("weather_api");
        rainfall < 100;  # Drought condition
    }
    verify {
        farmer_balance == old_balance + payout_amount;
    }
}
```

### UC3: Sports Betting Settlement
```aethel
intent settle_bet(bettor: Account, game_id: GameID) {
    guard {
        external winner from oracle("sports_api");
        bettor_prediction == winner;
    }
    verify {
        bettor_balance == old_balance + winnings;
    }
}
```

### UC4: Supply Chain Verification
```aethel
intent verify_shipment(package: Package, destination: Location) {
    guard {
        external current_location from oracle("gps_tracker");
        current_location == destination;
        external temperature from oracle("iot_sensor");
        temperature < 25;  # Cold chain maintained
    }
    verify {
        shipment_verified == true;
    }
}
```

---

## 🎯 Success Criteria

### Phase 1 (v1.7.0)
- [ ] `external` keyword accepted by parser
- [ ] Oracle registry implemented
- [ ] Signature verification working
- [ ] Chainlink integration (1 price feed)
- [ ] 3 working examples

### Phase 2 (v1.7.1)
- [ ] Band Protocol integration
- [ ] Custom oracle support
- [ ] Reputation system
- [ ] 10+ oracle types

### Phase 3 (v1.8.0)
- [ ] Oracle marketplace
- [ ] Decentralized oracle network
- [ ] Stake-based reputation
- [ ] 100+ oracles

---

## 🚧 Non-Requirements (Out of Scope)

- ❌ Building our own oracle network (use existing)
- ❌ Oracle data storage (oracles are stateless)
- ❌ Oracle payment system (handled externally)
- ❌ Oracle discovery (manual registration)

---

## 📈 Metrics

### Performance
- Oracle call latency: < 1 second (p95)
- Signature verification: < 10ms
- Max concurrent oracle calls: 100

### Reliability
- Oracle uptime: > 99.9%
- Signature validity: 100%
- Timeout rate: < 1%

### Security
- Unsigned data rejections: 100%
- Replay attack prevention: 100%
- Rate limit violations: 0

---

## 🔗 Dependencies

### External
- Chainlink Price Feeds API
- Band Protocol API
- Ed25519 signature library
- HTTP client with timeout

### Internal
- Parser (grammar expansion)
- Judge (signature verification)
- Vault (oracle registry)
- State Manager (oracle call logging)

---

## 📚 References

- [Chainlink Documentation](https://docs.chain.link/)
- [Band Protocol Documentation](https://docs.bandchain.org/)
- [Oracle Problem in Blockchain](https://en.wikipedia.org/wiki/Oracle_problem)
- [Ed25519 Signatures](https://ed25519.cr.yp.to/)

---

## 🎭 Philosophical Note

**"The Oracle is not a source of truth. It is a witness to reality."**

Aethel doesn't trust oracles. It verifies their signatures. The oracle doesn't tell Aethel what is true - it provides evidence that Aethel can mathematically validate.

This is the difference between **trust** and **verification**.

---

**Status**: READY FOR DESIGN PHASE  
**Next**: Design specification  
**Estimated Effort**: 2-3 weeks  
**Risk**: MEDIUM (external dependencies)
