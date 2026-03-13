// Aethel Artifact v0.2
// Generated from intent: transfer_funds
// Timestamp: 2026-02-24T20:28:19.727729

fn transfer_funds(sender: &mut Account, receiver: &mut Account, amount: Gold) -> Result<(), TransferError> {
    // Guard: Validação de pré-condições
    if sender.balance < amount {
        return Err(TransferError::InsufficientFunds);
    }
    if amount <= 0 {
        return Err(TransferError::InvalidAmount);
    }
    
    let old_balance = sender.balance;
    
    // Solve: Execução otimizada para blockchain
    sender.balance -= amount;
    receiver.balance += amount;
    
    // Verify: Validação de pós-condições
    assert!(sender.balance < old_balance);
    
    Ok(())
}
