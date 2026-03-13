# Requirements Document: Aethel-Pilot v3.7

## Introduction

The Aethel-Pilot v3.7 is a real-time predictive autocomplete engine that integrates into the Aethel Explorer's code editor (Monaco Editor). Unlike traditional autocomplete systems that suggest syntactically correct code, Aethel-Pilot suggests code that is provably correct according to Aethel's conservation laws and formal verification principles. The system provides real-time visual feedback through a "traffic light" indicator and offers automatic correction suggestions as developers type.

This feature transforms the Aethel Explorer from a passive analysis tool into an active development environment that prevents bugs before they are written, creating a viral marketing opportunity where developers experience "a language that won't let me write bugs."

## Glossary

- **Autopilot_Engine**: The backend Python service that analyzes code context and generates suggestions (`aethel/ai/autopilot_engine.py`)
- **Monaco_Editor**: Industry-standard web-based code editor component used in VS Code
- **Traffic_Light**: Visual indicator showing code safety status (green = safe, red = vulnerable)
- **Suggestion**: An autocomplete recommendation with code snippet, description, and priority
- **Editor_State**: Current state of the editor including code, cursor position, and selection
- **Context**: The type of code block being edited (guard, verify, solve, intent)
- **Conservation_Violation**: Code that creates or destroys value illegally
- **API_Endpoint**: FastAPI REST endpoint that connects frontend to backend
- **IntelliSense**: Microsoft's term for intelligent code completion
- **WebSocket**: Bidirectional communication protocol for real-time updates
- **Cursor_Position**: Current location of the text cursor in the editor
- **Guard_Block**: Aethel code block that defines preconditions
- **Verify_Block**: Aethel code block that defines postconditions
- **Solve_Block**: Aethel code block that invokes formal verification

## Requirements

### Requirement 1: Monaco Editor Integration

**User Story:** As a developer, I want to write Aethel code in a professional code editor, so that I have a familiar and powerful development experience.

#### Acceptance Criteria

1. WHEN a user visits the Explorer page, THE Monaco_Editor SHALL be rendered and ready for input
2. WHEN a user types Aethel code, THE Monaco_Editor SHALL provide syntax highlighting for Aethel language constructs
3. WHEN a user interacts with the editor, THE Monaco_Editor SHALL maintain cursor position and selection state
4. WHEN the editor loads, THE Monaco_Editor SHALL be configured with Aethel language support
5. THE Monaco_Editor SHALL support standard keyboard shortcuts (Ctrl+Z, Ctrl+C, Ctrl+V, etc.)

### Requirement 2: Real-Time Autocomplete Suggestions

**User Story:** As a developer, I want to receive intelligent code suggestions as I type, so that I can write correct code faster.

#### Acceptance Criteria

1. WHEN a user types in the editor, THE Autopilot_Engine SHALL analyze the current Editor_State
2. WHEN the cursor is inside a Guard_Block, THE Autopilot_Engine SHALL suggest valid guard conditions
3. WHEN the cursor is inside a Verify_Block, THE Autopilot_Engine SHALL suggest conservation-preserving postconditions
4. WHEN the cursor is inside a Solve_Block, THE Autopilot_Engine SHALL suggest formal verification options
5. WHEN typing an intent declaration, THE Autopilot_Engine SHALL suggest required parameters
6. WHEN suggestions are available, THE Monaco_Editor SHALL display them in an IntelliSense-style dropdown
7. WHEN a user selects a suggestion, THE Monaco_Editor SHALL insert the suggested code at the cursor position
8. THE Autopilot_Engine SHALL return suggestions within 200ms of receiving a request

### Requirement 3: Traffic Light Visual Feedback

**User Story:** As a developer, I want immediate visual feedback on code safety, so that I know when my code has vulnerabilities before running it.

#### Acceptance Criteria

1. WHEN the code is analyzed and no vulnerabilities are detected, THE Monaco_Editor SHALL display a green background glow
2. WHEN the code is analyzed and vulnerabilities are detected, THE Monaco_Editor SHALL display a red background glow
3. WHEN the code is being analyzed, THE Monaco_Editor SHALL display a neutral state (no glow)
4. WHEN the safety status changes, THE visual feedback SHALL transition smoothly within 100ms
5. THE traffic light indicator SHALL update in real-time as the user types

### Requirement 4: Automatic Correction Suggestions

**User Story:** As a developer, I want to receive correction suggestions when I write unsafe code, so that I can fix vulnerabilities immediately.

#### Acceptance Criteria

1. WHEN unsafe code is detected, THE Autopilot_Engine SHALL generate a correction suggestion
2. WHEN a correction is available, THE Monaco_Editor SHALL display an inline tooltip with the suggestion
3. WHEN a correction tooltip is displayed, THE tooltip SHALL include the vulnerability type and recommended fix
4. WHEN a user clicks on a correction suggestion, THE Monaco_Editor SHALL apply the correction automatically
5. THE correction tooltip SHALL appear within 200ms of detecting the vulnerability

### Requirement 5: Vulnerability Pattern Detection

**User Story:** As a developer, I want the system to detect common vulnerability patterns, so that I can avoid security issues.

#### Acceptance Criteria

1. WHEN code contains a Conservation_Violation, THE Autopilot_Engine SHALL detect it and report the violation type
2. WHEN code contains potential overflow conditions, THE Autopilot_Engine SHALL detect missing bounds checks
3. WHEN code contains potential underflow conditions, THE Autopilot_Engine SHALL detect missing non-negativity checks
4. WHEN code contains reentrancy patterns, THE Autopilot_Engine SHALL detect missing reentrancy guards
5. WHEN code is missing required guard conditions, THE Autopilot_Engine SHALL identify the missing guards

### Requirement 6: API Endpoint for Suggestions

**User Story:** As a frontend developer, I want a reliable API endpoint for autocomplete, so that I can integrate the Autopilot_Engine with the Monaco_Editor.

#### Acceptance Criteria

1. THE API_Endpoint SHALL accept POST requests at `/api/autopilot/suggestions`
2. WHEN a request is received, THE API_Endpoint SHALL validate the request contains code and cursor position
3. WHEN a valid request is received, THE API_Endpoint SHALL call the Autopilot_Engine with the Editor_State
4. WHEN the Autopilot_Engine returns results, THE API_Endpoint SHALL format them as JSON
5. WHEN an error occurs, THE API_Endpoint SHALL return an appropriate HTTP error code and message
6. THE API_Endpoint SHALL respond within 250ms for 95% of requests

### Requirement 7: Real-Time Communication

**User Story:** As a developer, I want instant feedback as I type, so that I don't have to wait for analysis results.

#### Acceptance Criteria

1. WHEN a user types in the editor, THE frontend SHALL debounce requests to avoid overwhelming the backend
2. WHEN the debounce period expires, THE frontend SHALL send the current Editor_State to the API_Endpoint
3. WHEN a response is received, THE frontend SHALL update the UI with new suggestions and safety status
4. WHEN multiple requests are in flight, THE frontend SHALL cancel outdated requests
5. THE debounce period SHALL be configurable with a default of 300ms

### Requirement 8: Context-Aware Suggestions

**User Story:** As a developer, I want suggestions that are relevant to what I'm currently writing, so that I don't see irrelevant options.

#### Acceptance Criteria

1. WHEN the cursor is at the start of a line, THE Autopilot_Engine SHALL suggest Aethel keywords (intent, guard, verify, solve)
2. WHEN the cursor is after "intent", THE Autopilot_Engine SHALL suggest intent types (payment, transfer, swap)
3. WHEN the cursor is inside a guard block, THE Autopilot_Engine SHALL only suggest guard-appropriate conditions
4. WHEN the cursor is inside a verify block, THE Autopilot_Engine SHALL only suggest verify-appropriate assertions
5. WHEN variables are available in scope, THE Autopilot_Engine SHALL include them in suggestions

### Requirement 9: Integration with Existing Judge System

**User Story:** As a system architect, I want the Autopilot to use the existing Judge and Ghost-Runner, so that suggestions are consistent with verification results.

#### Acceptance Criteria

1. WHEN generating safety status, THE Autopilot_Engine SHALL use the existing Judge for verification
2. WHEN detecting conservation violations, THE Autopilot_Engine SHALL use the existing conservation validator
3. WHEN suggesting corrections, THE Autopilot_Engine SHALL verify corrections would pass Judge validation
4. THE Autopilot_Engine SHALL reuse existing vulnerability detection logic from the Judge
5. THE Autopilot_Engine SHALL maintain consistency with the `/api/verify` endpoint results

### Requirement 10: Performance and Responsiveness

**User Story:** As a developer, I want the autocomplete to feel instant, so that it doesn't interrupt my flow.

#### Acceptance Criteria

1. THE Autopilot_Engine SHALL process suggestion requests in under 200ms for 95% of requests
2. THE API_Endpoint SHALL have a maximum response time of 250ms for 95% of requests
3. WHEN the backend is slow, THE frontend SHALL show a loading indicator after 500ms
4. THE frontend SHALL cache recent suggestions to improve perceived performance
5. THE system SHALL handle at least 10 concurrent users without degradation

### Requirement 11: User Experience Polish

**User Story:** As a developer, I want a polished and intuitive interface, so that the tool feels professional and trustworthy.

#### Acceptance Criteria

1. WHEN suggestions appear, THE Monaco_Editor SHALL display them with clear descriptions and icons
2. WHEN the traffic light changes color, THE transition SHALL be smooth and not jarring
3. WHEN correction tooltips appear, THE tooltips SHALL be positioned to not obscure code
4. WHEN the user is typing quickly, THE system SHALL not interrupt with unwanted popups
5. THE visual design SHALL be consistent with the existing Aethel Explorer aesthetic

### Requirement 12: Error Handling and Resilience

**User Story:** As a developer, I want the system to handle errors gracefully, so that I can continue working even when issues occur.

#### Acceptance Criteria

1. WHEN the API_Endpoint is unavailable, THE frontend SHALL display an error message and disable autocomplete
2. WHEN a request times out, THE frontend SHALL retry once before showing an error
3. WHEN the Autopilot_Engine encounters invalid code, THE system SHALL return empty suggestions rather than crashing
4. WHEN an unexpected error occurs, THE system SHALL log the error and continue functioning
5. THE system SHALL recover automatically when the backend becomes available again
