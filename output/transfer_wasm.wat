(module
  ;; Aethel WASM Module: transfer
  ;; Generated: 2026-02-02T00:24:01.900639
  ;; Bundle Hash: 3be8a8cefca097d4...

  ;; Memory: 1 page (64KB) - isolated linear memory
  (memory 1)

  (func $transfer
    (param $sender i32)
    (param $receiver i32)
    (param $amount i32)
    (result i32)

    ;; Local variables for snapshots

    ;; === GUARDS (Pre-conditions) ===
    ;; Guard 1: sender_balance >= amount
    local.get $0  ;; sender_balance
    local.get $2  ;; amount
    i32.ge_s  ;; sender_balance >= amount
    i32.eqz
    if
      unreachable  ;; PANIC: Guard violation
    end
    ;; Guard 2: amount >= min_transfer
    local.get $2  ;; amount
    local.get $0  ;; min_transfer
    i32.ge_s  ;; amount >= min_transfer
    i32.eqz
    if
      unreachable  ;; PANIC: Guard violation
    end
    ;; Guard 3: receiver_balance >= balance_zero
    local.get $0  ;; receiver_balance
    local.get $0  ;; balance_zero
    i32.ge_s  ;; receiver_balance >= balance_zero
    i32.eqz
    if
      unreachable  ;; PANIC: Guard violation
    end
    ;; Guard 4: old_sender_balance == sender_balance
    local.get $0  ;; old_sender_balance
    local.get $0  ;; sender_balance
    i32.eq  ;; old_sender_balance == sender_balance
    i32.eqz
    if
      unreachable  ;; PANIC: Guard violation
    end
    ;; Guard 5: old_receiver_balance == receiver_balance
    local.get $0  ;; old_receiver_balance
    local.get $0  ;; receiver_balance
    i32.eq  ;; old_receiver_balance == receiver_balance
    i32.eqz
    if
      unreachable  ;; PANIC: Guard violation
    end
    ;; Guard 6: old_total_supply == total_supply
    local.get $0  ;; old_total_supply
    local.get $0  ;; total_supply
    i32.eq  ;; old_total_supply == total_supply
    i32.eqz
    if
      unreachable  ;; PANIC: Guard violation
    end

    ;; === BUSINESS LOGIC ===
    ;; sender_balance -= amount
    local.get $0  ;; sender_balance
    local.get $2  ;; amount
    i32.sub
    local.set $0  ;; sender_balance = sender_balance - amount

    ;; receiver_balance += amount
    local.get $0  ;; receiver_balance
    local.get $2  ;; amount
    i32.add
    local.set $0  ;; receiver_balance = receiver_balance + amount


    ;; === POST-CONDITIONS (The Second Wall) ===
    ;; Post-condition 1: sender_balance == old_sender_balance
    ;; Post-condition 2: receiver_balance == old_receiver_balance
    ;; Post-condition 3: total_supply == old_total_supply

    ;; Return success
    i32.const 1
    return
  )

  ;; Export function for access outside module
  (export "transfer" (func $transfer))

)