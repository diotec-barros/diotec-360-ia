(module
  ;; Aethel WASM Module: vote
  ;; Generated: 2026-02-02T00:22:54.418726
  ;; Bundle Hash: vote_test_hash...

  ;; Memory: 1 page (64KB) - isolated linear memory
  (memory 1)

  (func $vote
    (param $votes i32)
    (result i32)

    ;; Local variables for snapshots
    (local $old_votes i32)
    local.get $0
    local.set $1  ;; old_votes = votes

    ;; === GUARDS (Pre-conditions) ===
    ;; Guard 1: votes >= votes_zero
    local.get $0  ;; votes
    local.get $0  ;; votes_zero
    i32.ge_s  ;; votes >= votes_zero
    i32.eqz
    if
      unreachable  ;; PANIC: Guard violation
    end
    ;; Guard 2: old_votes == votes
    local.get $1  ;; old_votes
    local.get $0  ;; votes
    i32.eq  ;; old_votes == votes
    i32.eqz
    if
      unreachable  ;; PANIC: Guard violation
    end

    ;; === BUSINESS LOGIC ===
    ;; votes += 1
    local.get $0  ;; votes
    i32.const 1
    i32.add
    local.set $0  ;; votes = votes + 1


    ;; === POST-CONDITIONS (The Second Wall) ===
    ;; Post-condition 1: votes == old_votes

    ;; Return success
    i32.const 1
    return
  )

  ;; Export function for access outside module
  (export "vote" (func $vote))

)