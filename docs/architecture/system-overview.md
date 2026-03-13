# Diotec360 system Architecture

## Overview

Aethel is a financial programming language with mathematical proof capabilities. This document describes the system architecture, component interactions, and design decisions.

## High-Level Architecture

```mermaid
graph TB
    User[User/Application]
    CLI[CLI Interface]
    API[API Server]
    
    Parser[Parser]
    Judge[Judge/Verifier]
    Runtime[Runtime Engine]
    Validator[Conservation Validator]
    
    Proof[Proof Generator]
    State[State Manager]
    Security[Security Layer]
    
    User --> CLI
    User --> API
    
    CLI --> Parser
    API --> Parser
    
    Parser --> Judge
    Judge --> Validator
    Judge --> Proof
    
    Judge --> Runtime
    Runtime --> State
    Runtime --> Security
    
    Validator --> Proof
    
    style Judge fill:#f9f,stroke:#333,stroke-width:4px
    style Runtime fill:#bbf,stroke:#333,stroke-width:4px
    style Validator fill:#bfb,stroke:#333,stroke-width:4px
```

## Core Components

### 1. Parser

**Purpose**: Converts Aethel source code into an Abstract Syntax Tree (AST).

**Responsibilities**:
- Lexical analysis (tokenization)
- Syntax analysis (parsing)
- AST generation
- Syntax error detection

**Input**: Aethel source code (`.ae` files)  
**Output**: Abstract Syntax Tree (AST)

```mermaid
graph LR
    Source[Source Code] --> Lexer[Lexer]
    Lexer --> Tokens[Token Stream]
    Tokens --> Parser[Parser]
    Parser --> AST[Abstract Syntax Tree]
    
    style AST fill:#bfb
```

### 2. Judge (Verifier)

**Purpose**: Verifies program correctness and generates mathematical proofs.

**Responsibilities**:
- Constraint verification
- Conservation law checking
- Proof generation
- Security analysis
- Overflow/underflow detection

**Input**: AST  
**Output**: Verification result + Proof

```mermaid
graph TB
    AST[AST] --> Judge[Judge]
    
    Judge --> ConstraintCheck[Constraint Checker]
    Judge --> ConservationCheck[Conservation Checker]
    Judge --> SecurityCheck[Security Analyzer]
    
    ConstraintCheck --> ProofGen[Proof Generator]
    ConservationCheck --> ProofGen
    SecurityCheck --> ProofGen
    
    ProofGen --> Result[Verification Result]
    
    style Judge fill:#f9f,stroke:#333,stroke-width:2px
```

### 3. Runtime Engine

**Purpose**: Executes verified Aethel programs in a safe environment.

**Responsibilities**:
- Program execution
- State management
- Sandboxing
- Resource limits
- Error handling

**Input**: Verified AST  
**Output**: Execution result + Final state

```mermaid
graph TB
    VerifiedAST[Verified AST] --> Runtime[Runtime Engine]
    
    Runtime --> Executor[Executor]
    Runtime --> StateManager[State Manager]
    Runtime --> Sandbox[Sandbox]
    
    Executor --> Operations[Operations]
    StateManager --> State[Program State]
    Sandbox --> Limits[Resource Limits]
    
    Operations --> Result[Execution Result]
    State --> Result
    
    style Runtime fill:#bbf,stroke:#333,stroke-width:2px
```

### 4. Conservation Validator

**Purpose**: Verifies that conservation laws hold throughout execution.

**Responsibilities**:
- Conservation checking
- Invariant verification
- Conservation proof generation
- Violation detection

**Input**: Program + Conservation laws  
**Output**: Conservation result + Proof

```mermaid
graph LR
    Program[Program] --> Validator[Conservation Validator]
    Laws[Conservation Laws] --> Validator
    
    Validator --> Check[Check Invariants]
    Check --> Proof[Generate Proof]
    Proof --> Result[Conservation Result]
    
    style Validator fill:#bfb,stroke:#333,stroke-width:2px
```

## Data Flow

### Complete Execution Pipeline

```mermaid
sequenceDiagram
    participant User
    participant Parser
    participant Judge
    participant Validator
    participant Runtime
    participant State
    
    User->>Parser: Submit program
    Parser->>Parser: Tokenize & Parse
    Parser->>Judge: AST
    
    Judge->>Judge: Verify constraints
    Judge->>Validator: Check conservation
    Validator->>Judge: Conservation result
    Judge->>Judge: Generate proof
    Judge->>User: Verification result
    
    alt Verification passed
        User->>Runtime: Execute program
        Runtime->>State: Initialize state
        Runtime->>Runtime: Execute operations
        Runtime->>State: Update state
        Runtime->>Validator: Verify final conservation
        Validator->>Runtime: Conservation OK
        Runtime->>User: Execution result
    else Verification failed
        Judge->>User: Errors
    end
```

## Component Interactions

### Verification Phase

```mermaid
graph TB
    subgraph "Verification Phase"
        AST[AST] --> Judge[Judge]
        Judge --> C1[Constraint Checker]
        Judge --> C2[Type Checker]
        Judge --> C3[Security Analyzer]
        
        C1 --> Validator[Conservation Validator]
        C2 --> Validator
        C3 --> Validator
        
        Validator --> ProofGen[Proof Generator]
        ProofGen --> Result[Verification Result]
    end
    
    style Judge fill:#f9f
    style Validator fill:#bfb
```

### Execution Phase

```mermaid
graph TB
    subgraph "Execution Phase"
        VerifiedAST[Verified AST] --> Runtime[Runtime]
        Runtime --> Sandbox[Sandbox]
        
        Sandbox --> Executor[Executor]
        Executor --> Ops[Operations]
        
        Ops --> State[State Manager]
        State --> Memory[Memory]
        
        Ops --> Monitor[Resource Monitor]
        Monitor --> Limits[Check Limits]
        
        State --> FinalState[Final State]
    end
    
    style Runtime fill:#bbf
```

## Security Architecture

### Multi-Layer Security

```mermaid
graph TB
    subgraph "Security Layers"
        Input[User Input] --> L1[Layer 1: Parser]
        L1 --> L2[Layer 2: Judge]
        L2 --> L3[Layer 3: Validator]
        L3 --> L4[Layer 4: Sandbox]
        L4 --> L5[Layer 5: Runtime]
        L5 --> Output[Safe Execution]
    end
    
    L1 -.->|Syntax Errors| Reject1[Reject]
    L2 -.->|Constraint Violations| Reject2[Reject]
    L3 -.->|Conservation Violations| Reject3[Reject]
    L4 -.->|Resource Violations| Reject4[Reject]
    L5 -.->|Runtime Errors| Reject5[Reject]
    
    style L1 fill:#fbb
    style L2 fill:#fdb
    style L3 fill:#ffb
    style L4 fill:#bfb
    style L5 fill:#bbf
```

### Sandboxing

```mermaid
graph LR
    subgraph "Sandbox Environment"
        Program[Program] --> Limits[Resource Limits]
        
        Limits --> Memory[Memory Limit]
        Limits --> Time[Time Limit]
        Limits --> CPU[CPU Limit]
        
        Memory --> Monitor[Monitor]
        Time --> Monitor
        CPU --> Monitor
        
        Monitor --> Enforce[Enforce Limits]
        Enforce --> Safe[Safe Execution]
    end
    
    style Limits fill:#fbb
    style Monitor fill:#ffb
    style Safe fill:#bfb
```

## State Management

### State Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Initial: Create Runtime
    Initial --> Parsing: Submit Program
    Parsing --> Verification: AST Generated
    Verification --> Ready: Verified
    Verification --> Error: Failed
    Ready --> Executing: Execute
    Executing --> Updating: Operations
    Updating --> Executing: More Operations
    Executing --> Final: Complete
    Final --> [*]: Return Result
    Error --> [*]: Return Errors
```

### State Structure

```mermaid
graph TB
    subgraph "Program State"
        State[State Manager]
        
        State --> Variables[Variables]
        State --> Stack[Call Stack]
        State --> Heap[Heap Memory]
        
        Variables --> Scope[Scope Chain]
        Stack --> Frames[Stack Frames]
        Heap --> Objects[Objects]
        
        Scope --> Global[Global Scope]
        Scope --> Local[Local Scopes]
    end
    
    style State fill:#bbf
```

## Proof Generation

### Proof Architecture

```mermaid
graph TB
    subgraph "Proof Generation"
        Input[Program + Constraints] --> Analyzer[Symbolic Analyzer]
        
        Analyzer --> Constraints[Constraint Proofs]
        Analyzer --> Conservation[Conservation Proofs]
        Analyzer --> Security[Security Proofs]
        
        Constraints --> Combiner[Proof Combiner]
        Conservation --> Combiner
        Security --> Combiner
        
        Combiner --> Verifier[Proof Verifier]
        Verifier --> Certificate[Proof Certificate]
    end
    
    style Analyzer fill:#f9f
    style Certificate fill:#bfb
```

## Design Decisions

### 1. Verification Before Execution

**Decision**: Always verify programs before execution.

**Rationale**:
- Prevents invalid programs from executing
- Catches errors at compile-time
- Generates proofs of correctness
- Provides security guarantees

**Trade-offs**:
- Adds verification overhead (~10-100ms)
- Requires more complex tooling
- Worth it for financial applications

### 2. Immutable State Transitions

**Decision**: State transitions are atomic and immutable.

**Rationale**:
- Easier to reason about program behavior
- Simplifies proof generation
- Enables rollback on errors
- Supports parallel execution

**Trade-offs**:
- Higher memory usage
- Slower for large state
- Acceptable for financial transactions

### 3. Conservation by Default

**Decision**: Conservation laws are checked automatically.

**Rationale**:
- Financial correctness is critical
- Prevents money creation/destruction bugs
- Provides mathematical guarantees
- Builds trust in the system

**Trade-offs**:
- Adds checking overhead (~1-10μs)
- Requires explicit conservation laws
- Essential for financial applications

### 4. Sandboxed Execution

**Decision**: All programs execute in a sandbox.

**Rationale**:
- Prevents resource exhaustion
- Limits attack surface
- Enables safe multi-tenancy
- Provides isolation guarantees

**Trade-offs**:
- Adds execution overhead (~5-10%)
- Limits system access
- Necessary for security

### 5. Proof Certificates

**Decision**: Generate verifiable proof certificates.

**Rationale**:
- Enables independent verification
- Provides audit trail
- Supports compliance requirements
- Builds trust through transparency

**Trade-offs**:
- Increases output size
- Adds generation time
- Critical for trust

## Performance Characteristics

### Typical Latencies

| Operation | Latency | Notes |
|-----------|---------|-------|
| Parse | 1-10ms | Depends on program size |
| Verify | 10-100ms | Depends on complexity |
| Execute | 0.1-10ms | Depends on operations |
| Conservation Check | 1-10μs | Per conserve statement |
| Proof Generation | 10-100ms | Depends on proof complexity |

### Scalability

```mermaid
graph LR
    subgraph "Horizontal Scaling"
        LB[Load Balancer] --> R1[Runtime 1]
        LB --> R2[Runtime 2]
        LB --> R3[Runtime 3]
        
        R1 --> State1[State Store 1]
        R2 --> State2[State Store 2]
        R3 --> State3[State Store 3]
    end
    
    style LB fill:#bbf
```

## Extension Points

### Plugin Architecture

```mermaid
graph TB
    subgraph "Plugin System"
        Core[Diotec360 core] --> API[Plugin API]
        
        API --> P1[Custom Validators]
        API --> P2[Custom Provers]
        API --> P3[Custom Analyzers]
        
        P1 --> Registry[Plugin Registry]
        P2 --> Registry
        P3 --> Registry
    end
    
    style Core fill:#f9f
    style API fill:#bbf
```

## Deployment Architecture

### Single Node

```mermaid
graph TB
    subgraph "Single Node Deployment"
        Client[Client] --> API[API Server]
        API --> Aethel[Aethel Runtime]
        Aethel --> DB[(State DB)]
    end
```

### Distributed

```mermaid
graph TB
    subgraph "Distributed Deployment"
        Clients[Clients] --> LB[Load Balancer]
        
        LB --> API1[API Server 1]
        LB --> API2[API Server 2]
        LB --> API3[API Server 3]
        
        API1 --> Cache[Redis Cache]
        API2 --> Cache
        API3 --> Cache
        
        API1 --> DB[(PostgreSQL)]
        API2 --> DB
        API3 --> DB
    end
    
    style LB fill:#bbf
    style Cache fill:#ffb
    style DB fill:#bfb
```

## See Also

- [Getting Started](../getting-started/quickstart.md)
- [API Reference](../api-reference/judge.md)
- [Advanced Topics](../advanced/formal-verification.md)
- [Examples](../examples/banking.md)
