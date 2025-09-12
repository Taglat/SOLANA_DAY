use anchor_lang::prelude::*;

declare_id!("BizReg1111111111111111111111111111111111111");

#[program]
pub mod business_registry {
    use super::*;

    pub fn register_business(
        _ctx: Context<RegisterBusiness>,
        _name: String,
        _category: BusinessCategory,
        _tokens_per_dollar: u64,
    ) -> Result<()> {
        Ok(())
    }

    pub fn update_business_settings(
        _ctx: Context<UpdateBusiness>,
        _tokens_per_dollar: Option<u64>,
        _max_discount: Option<u8>,
    ) -> Result<()> {
        Ok(())
    }
}

#[account]
pub struct Business {
    pub owner: Pubkey,
    pub name: String,
    pub category: BusinessCategory,
    pub tokens_per_dollar: u64,
    pub max_discount: u8,
    pub is_active: bool,
    pub created_at: i64,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone)]
pub enum BusinessCategory {
    Cafe,
    Barbershop,
    Fitness,
    Restaurant,
    Other,
}

#[derive(Accounts)]
pub struct RegisterBusiness {}

#[derive(Accounts)]
pub struct UpdateBusiness {}


