use anchor_lang::prelude::*;

declare_id!("TxnProg11111111111111111111111111111111111");

#[program]
pub mod transaction_program {
    use super::*;

    pub fn record_purchase(_ctx: Context<RecordPurchase>, _amount_usd: u64) -> Result<()> {
        Ok(())
    }

    pub fn record_redemption(
        _ctx: Context<RecordRedemption>,
        _tokens_used: u64,
        _discount_amount: u64,
    ) -> Result<()> {
        Ok(())
    }
}

#[account]
pub struct TransactionRecord {
    pub customer: Pubkey,
    pub business: Pubkey,
    pub transaction_type: TransactionType,
    pub amount_usd: u64,
    pub tokens_amount: u64,
    pub timestamp: i64,
    pub signature: String,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone)]
pub enum TransactionType {
    Earn,
    Redeem,
}

#[derive(Accounts)]
pub struct RecordPurchase {}

#[derive(Accounts)]
pub struct RecordRedemption {}


