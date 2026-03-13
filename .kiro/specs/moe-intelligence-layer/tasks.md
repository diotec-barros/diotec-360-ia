# Implementation Plan: MOE Intelligence Layer v2.1

## Overview

This implementation plan transforms Aethel from a single-agent verification system into a **Multi-Expert Consensus Architecture**. The MOE (Mixture of Experts) layer deploys specialized expert agents that work in parallel, each optimized for their domain.

Implementation follows a bottom-up approach: base infrastructure first, then individual experts, then orchestration and consensus, and finally visual integration.

## Tasks

- [-] 1. MOE Infrastructure - Base Classes and Interfaces
  - [x] 1.1 Implement BaseExpert abstract class
    - Create abstract interface that all experts must implement
    - Implement accuracy tracking and telemetry
    - _Requirements: All_

  - [x] 1.2 Implement ExpertVerdict and MOEResult data structures
    - Create dataclasses for expert responses
    - Implement JSON serialization
    - _Requirements: 1.1, 1.2, 1.3, 1.4_

  - [x] 1.3 Implement ExpertTelemetry system
    - Create SQLite database for expert metrics
    - Implement performance tracking per expert
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7_

  - [x] 1.4 Write unit tests for base infrastructure
    - Test BaseExpert interface
    - Test telemetry recording and retrieval
    - _Requirements: All infrastructure_

- [-] 2. Z3 Expert - Mathematical Logic Specialist
  - [x] 2.1 Implement Z3Expert class
    - Integrate with existing Z3Prover (Layer 3)
    - Implement confidence calculation based on proof complexity
    - Implement timeout handling (30s normal, 5s crisis)
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7_

  - [x] 2.2 Write unit tests for Z3Expert
    - Test arithmetic verification
    - Test logical contradiction detection
    - Test confidence scoring
    - Test timeout behavior
    - _Requirements: 2.1-2.7_

  - [x] 2.3 Write property tests for Z3Expert
    - **Property 1: Z3 Expert accuracy**
    - **Property 2: Z3 Expert latency**
    - **Validates: Requirements 2.6, 2.7**

- [x] 3. Sentinel Expert - Security Specialist
  - [x] 3.1 Implement SentinelExpert class
    - Integrate with SemanticSanitizer (Layer -1)
    - Integrate with OverflowDetector (Layer 2)
    - Implement entropy-based confidence scoring
    - Implement 100ms timeout
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7_

  - [x] 3.2 Write unit tests for SentinelExpert
    - Test overflow detection
    - Test DoS pattern detection
    - Test injection attack detection
    - Test entropy scoring
    - _Requirements: 3.1-3.7_

  - [x] 3.3 Write property tests for SentinelExpert
    - **Property 3: Sentinel Expert accuracy**
    - **Property 4: Sentinel Expert latency**
    - **Validates: Requirements 3.6, 3.7**

- [x] 4. Guardian Expert - Financial Specialist
  - [x] 4.1 Implement GuardianExpert class
    - Integrate with ConservationChecker (Layer 1)
    - Implement Merkle tree integrity verification
    - Implement double-spending detection
    - Implement 50ms timeout
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7_

  - [x] 4.2 Write unit tests for GuardianExpert
    - Test conservation verification
    - Test Merkle tree validation
    - Test double-spending detection
    - Test confidence scoring
    - _Requirements: 4.1-4.7_

  - [x] 4.3 Write property tests for GuardianExpert
    - **Property 5: Guardian Expert accuracy**
    - **Property 6: Guardian Expert latency**
    - **Validates: Requirements 4.6, 4.7**

- [x] 5. Checkpoint - All Experts Implemented
  - Ensure all three experts pass unit tests
  - Verify expert latency meets requirements
  - Verify expert accuracy on test dataset
  - Ask the user if questions arise

- [x] 6. Gating Network - Intelligent Routing
  - [x] 6.1 Implement GatingNetwork class
    - Implement feature extraction from transaction intent
    - Implement routing rules (financial, arithmetic, security)
    - Implement routing history tracking
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7_

  - [x] 6.2 Write unit tests for GatingNetwork
    - Test feature extraction
    - Test routing rules
    - Test routing for different transaction types
    - _Requirements: 5.1-5.7_

  - [x] 6.3 Write property tests for GatingNetwork
    - **Property 7: Routing correctness**
    - **Property 8: Routing latency**
    - **Validates: Requirements 5.7**

- [x] 7. Consensus Engine - Verdict Aggregation
  - [x] 7.1 Implement ConsensusEngine class
    - Implement unanimous approval logic
    - Implement high-confidence rejection logic
    - Implement uncertainty detection
    - Implement confidence aggregation
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7_

  - [x] 7.2 Write unit tests for ConsensusEngine
    - Test unanimous approval
    - Test single expert rejection
    - Test mixed confidence scenarios
    - Test uncertainty detection
    - _Requirements: 6.1-6.7_

  - [x] 7.3 Write property tests for ConsensusEngine
    - **Property 9: Consensus correctness**
    - **Property 10: Consensus latency**
    - **Validates: Requirements 6.7**

- [x] 8. MOE Orchestrator - Central Coordination
  - [x] 8.1 Implement MOEOrchestrator class
    - Implement expert registration
    - Implement parallel expert execution
    - Implement feature extraction
    - Implement result aggregation
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7_

  - [x] 8.2 Implement verdict caching
    - Implement cache key generation (SHA256 of intent)
    - Implement TTL-based cache expiration (5 minutes)
    - Implement cache hit/miss tracking
    - _Requirements: 10.1, 10.2, 10.3_

  - [x] 8.3 Write unit tests for MOEOrchestrator
    - Test expert registration
    - Test parallel execution
    - Test result aggregation
    - Test caching behavior
    - _Requirements: 1.1-1.7, 10.1-10.3_

  - [x] 8.4 Write integration tests for MOEOrchestrator
    - Test end-to-end verification flow
    - Test expert failure handling
    - Test fallback mechanisms
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7_

- [x] 9. Checkpoint - Core MOE System Complete
  - Ensure all components pass unit tests
  - Verify end-to-end integration tests pass
  - Verify performance meets requirements (<10ms overhead)
  - Ask the user if questions arise

- [x] 10. Visual Dashboard Integration
  - [x] 10.1 Implement LED indicator system in console
    - Create three LED components (Z3, Sentinel, Guardian)
    - Implement real-time status updates
    - Implement color coding (yellow=processing, green=approve, red=reject)
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7_

  - [x] 10.2 Implement confidence display
    - Show per-expert confidence scores
    - Show overall confidence
    - Show latency per expert
    - _Requirements: 8.5, 8.6_

  - [x] 10.3 Implement animation for parallel processing
    - Animate LEDs to show simultaneous execution
    - Show progress indicators
    - _Requirements: 8.7_

  - [x] 10.4 Write UI tests for visual dashboard
    - Test LED state transitions
    - Test confidence display updates
    - Test animation behavior
    - _Requirements: 8.1-8.7_

- [x] 11. Integration with Existing Judge
  - [x] 11.1 Modify judge.py to integrate MOE
    - Add MOE verification before existing layers
    - Implement MOE enable/disable flag
    - Implement fallback to existing layers on MOE failure
    - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5, 12.6, 12.7_

  - [x] 11.2 Write integration tests for Judge + MOE
    - Test MOE approval → existing layers
    - Test MOE rejection → skip existing layers
    - Test MOE failure → fallback to existing layers
    - _Requirements: 12.1-12.7_

  - [x] 11.3 Write backward compatibility tests
    - Run all v1.9.0 tests with MOE enabled
    - Verify all tests pass
    - _Requirements: 12.6_

- [x] 12. Expert Training and Adaptation
  - [x] 12.1 Implement ground truth collection
    - Record expert verdicts and actual outcomes
    - Store in training database
    - _Requirements: 11.1, 11.2_

  - [x] 12.2 Implement accuracy calculation
    - Calculate per-expert accuracy over rolling window
    - Update expert confidence thresholds
    - _Requirements: 11.2, 11.3_

  - [x] 12.3 Implement A/B testing framework
    - Support multiple expert model versions
    - Compare accuracy across versions
    - Automatic promotion of better models
    - _Requirements: 11.4, 11.5, 11.6_

  - [x] 12.4 Write tests for training system
    - Test accuracy calculation
    - Test threshold adjustment
    - Test A/B testing
    - _Requirements: 11.1-11.7_

- [x] 13. Performance Testing and Optimization
  - [x] 13.1 Benchmark MOE overhead
    - Measure orchestration overhead (<10ms target)
    - Measure gating network latency (<10ms target)
    - Measure consensus engine latency (<1s target)
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7_

  - [x] 13.2 Benchmark expert latency
    - Measure Z3 Expert latency (<30s target)
    - Measure Sentinel Expert latency (<100ms target)
    - Measure Guardian Expert latency (<50ms target)
    - _Requirements: 2.6, 3.7, 4.7_

  - [x] 13.3 Benchmark throughput
    - Measure transactions per second (>1000 target)
    - Compare with v1.9.0 baseline
    - Verify <5% overhead
    - _Requirements: 10.3, 10.6_

  - [x] 13.4 Write property tests for performance
    - **Property 11: MOE overhead**
    - **Property 12: Expert latency**
    - **Property 13: System throughput**
    - **Validates: Requirements 10.1-10.7**

- [x] 14. Checkpoint - Performance Validated
  - Ensure all performance benchmarks pass
  - Verify overhead meets <10ms requirement
  - Verify throughput meets >1000 tx/s requirement
  - Ask the user if questions arise

- [x] 15. Documentation and Examples
  - [x] 15.1 Create MOE_GUIDE.md
    - Explain MOE architecture
    - Document expert responsibilities
    - Provide configuration examples
    - _Requirements: All_

  - [x] 15.2 Create demo_moe.py example
    - Demonstrate MOE verification flow
    - Show expert consensus
    - Show visual dashboard
    - _Requirements: All_

  - [x] 15.3 Update README.md with MOE features
    - Document MOE capabilities
    - Provide quick start guide
    - Explain expert system
    - _Requirements: All_

  - [x] 15.4 Create MIGRATION_GUIDE_V2_1.md
    - Document migration from v1.9.0 to v2.1.0
    - Explain breaking changes (if any)
    - Provide upgrade path
    - _Requirements: All_

- [x] 16. Deployment Preparation
  - [x] 16.1 Create deployment scripts
    - Create shadow mode deployment script
    - Create soft launch script (10% traffic)
    - Create full activation script (100% traffic)
    - _Requirements: All_

  - [x] 16.2 Create monitoring configuration
    - Configure expert telemetry collection
    - Set up alerts (expert failures, latency spikes)
    - Create monitoring dashboard
    - _Requirements: 7.1-7.7_

  - [x] 16.3 Create rollback plan
    - Document MOE disable procedure
    - Document fallback to v1.9.0 behavior
    - Create rollback testing checklist
    - _Requirements: 9.1-9.7, 12.7_

- [x] 17. Final Release Preparation
  - [x] 17.1 Run full test suite
    - Execute all unit tests
    - Execute all integration tests
    - Execute all property tests
    - Execute all performance tests
    - _Requirements: All_

  - [x] 17.2 Generate release artifacts
    - Create v2.1.0 release notes
    - Generate API documentation
    - Create deployment guide
    - Package release for distribution
    - _Requirements: All_

  - [x] 17.3 Final review and sign-off
    - Review all code changes
    - Review all documentation
    - Verify all requirements met
    - Get stakeholder approval
    - _Requirements: All_

## Notes

- MOE layer executes BEFORE existing Layers 0-4
- All experts execute in parallel for maximum throughput
- Consensus requires unanimous approval from activated experts
- Expert failures trigger automatic fallback to existing layers
- Visual dashboard provides real-time expert status
- System maintains backward compatibility with v1.9.0
- Performance target: <10ms orchestration overhead, >1000 tx/s throughput

## Success Criteria

- All 13 property tests pass with 100 examples each
- All unit tests pass (target: >150 unit tests)
- All integration tests pass
- Performance benchmarks meet requirements
- Backward compatibility tests pass 100% of v1.9.0 test suite
- Visual dashboard displays expert status correctly
- Expert accuracy >99.9%, false positive rate <0.1%

---

**Author**: Kiro AI - Engenheiro-Chefe  
**Date**: February 5, 2026  
**Version**: v2.1.0 "The MOE Intelligence Layer"  
**Status**: 🏛️ READY TO BUILD THE COUNCIL OF EXPERTS
