use anchor_lang::prelude::*;

declare_id!("LoTyTokn111111111111111111111111111111111");

#[program]
pub mod loyalty_token_program {
    use super::*;

    pub fn initialize(_ctx: Context<Initialize>) -> Result<()> {
        Ok(())
    }

    pub fn mint_loyalty_tokens(
        _ctx: Context<MintTokens>,
        _amount: u64,
        _business_id: Pubkey,
    ) -> Result<()> {
        Ok(())
    }

    pub fn burn_for_discount(
        _ctx: Context<BurnTokens>,
        _amount: u64,
        _discount_percentage: u8,
    ) -> Result<()> {
        Ok(())
    }
}

#[derive(Accounts)]
pub struct Initialize {}

#[derive(Accounts)]
pub struct MintTokens {}

#[derive(Accounts)]
pub struct BurnTokens {}


