from app.core.config import settings
import asyncio
import random
import string
import uuid
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models.nft import Achievement, UserAchievement, UserNFT, NFTPuzzle
from app.models.transaction import Transaction
from app.models.business import Business


class NFTService:
    def __init__(self):
        # Для MVP используем заглушки
        pass

    async def mint_nft(self, user_wallet: str, metadata: Dict[str, Any]) -> str:
        """Чеканка NFT (заглушка для MVP)"""
        await asyncio.sleep(0.3)  # Имитируем время чеканки
        return f"nft_{''.join(random.choices(string.ascii_lowercase + string.digits, k=44))}"

    async def check_achievement_requirements(
        self, 
        user_wallet: str, 
        requirements: Dict[str, Any], 
        db: Session
    ) -> bool:
        """Проверка выполнения требований для получения пазла"""
        try:
            # Проверяем различные типы требований
            if "min_transactions" in requirements:
                min_tx = requirements["min_transactions"]
                tx_count = db.query(Transaction).filter(
                    Transaction.customer_wallet == user_wallet,
                    Transaction.transaction_type == "EARN"
                ).count()
                
                if tx_count < min_tx:
                    return False
            
            if "min_spent_usd" in requirements:
                min_spent = requirements["min_spent_usd"]
                total_spent = db.query(Transaction).filter(
                    Transaction.customer_wallet == user_wallet,
                    Transaction.transaction_type == "EARN"
                ).with_entities(
                    db.func.sum(Transaction.amount_usd)
                ).scalar() or 0
                
                if total_spent < min_spent:
                    return False
            
            if "business_categories" in requirements:
                required_categories = requirements["business_categories"]
                user_categories = db.query(Business.category).join(Transaction).filter(
                    Transaction.customer_wallet == user_wallet,
                    Transaction.transaction_type == "EARN"
                ).distinct().all()
                
                user_category_list = [cat[0] for cat in user_categories]
                if not all(cat in user_category_list for cat in required_categories):
                    return False
            
            return True
            
        except Exception as e:
            print(f"Error checking achievement requirements: {e}")
            return False

    async def check_and_update_achievements(
        self, 
        user_wallet: str, 
        db: Session
    ) -> List[str]:
        """Проверка и обновление достижений пользователя"""
        updated_achievements = []
        
        try:
            # Получаем все активные достижения
            achievements = db.query(Achievement).filter(Achievement.is_active == True).all()
            
            for achievement in achievements:
                # Проверяем прогресс достижения
                progress = await self._calculate_achievement_progress(
                    user_wallet, achievement, db
                )
                
                # Получаем или создаем запись о достижении пользователя
                user_achievement = db.query(UserAchievement).filter(
                    UserAchievement.user_wallet == user_wallet,
                    UserAchievement.achievement_id == achievement.id
                ).first()
                
                if not user_achievement:
                    user_achievement = UserAchievement(
                        id=str(uuid.uuid4()),
                        user_wallet=user_wallet,
                        achievement_id=achievement.id,
                        progress=progress
                    )
                    db.add(user_achievement)
                else:
                    user_achievement.progress = progress
                
                # Если достижение завершено и раньше не было завершено
                if progress >= 100 and user_achievement.progress < 100:
                    updated_achievements.append(achievement.name)
                
                db.commit()
            
            return updated_achievements
            
        except Exception as e:
            print(f"Error checking achievements: {e}")
            db.rollback()
            return []

    async def _calculate_achievement_progress(
        self, 
        user_wallet: str, 
        achievement: Achievement, 
        db: Session
    ) -> int:
        """Расчет прогресса конкретного достижения"""
        try:
            condition = achievement.required_condition
            progress = 0
            
            if condition.get("type") == "transaction_count":
                required = condition.get("value", 0)
                actual = db.query(Transaction).filter(
                    Transaction.customer_wallet == user_wallet,
                    Transaction.transaction_type == "EARN"
                ).count()
                progress = min(100, int((actual / required) * 100)) if required > 0 else 0
            
            elif condition.get("type") == "spent_amount":
                required = condition.get("value", 0)
                actual = db.query(Transaction).filter(
                    Transaction.customer_wallet == user_wallet,
                    Transaction.transaction_type == "EARN"
                ).with_entities(
                    db.func.sum(Transaction.amount_usd)
                ).scalar() or 0
                progress = min(100, int((actual / required) * 100)) if required > 0 else 0
            
            elif condition.get("type") == "business_categories":
                required_categories = condition.get("categories", [])
                user_categories = db.query(Business.category).join(Transaction).filter(
                    Transaction.customer_wallet == user_wallet,
                    Transaction.transaction_type == "EARN"
                ).distinct().all()
                
                user_category_list = [cat[0] for cat in user_categories]
                completed_categories = sum(1 for cat in required_categories if cat in user_category_list)
                progress = int((completed_categories / len(required_categories)) * 100) if required_categories else 0
            
            return max(0, min(100, progress))
            
        except Exception as e:
            print(f"Error calculating achievement progress: {e}")
            return 0

    def create_espresso_day_puzzles(self, db: Session) -> List[str]:
        """Создание пазлов для картинки ESPRESSO DAY"""
        puzzle_ids = []
        
        try:
            # Создаем 9 пазлов (3x3 сетка)
            puzzles_data = [
                {
                    "puzzle_name": "espresso_day_1",
                    "position_x": 0, "position_y": 0,
                    "rarity": "common",
                    "required_achievements": {"min_transactions": 1}
                },
                {
                    "puzzle_name": "espresso_day_2", 
                    "position_x": 1, "position_y": 0,
                    "rarity": "common",
                    "required_achievements": {"min_transactions": 3}
                },
                {
                    "puzzle_name": "espresso_day_3",
                    "position_x": 2, "position_y": 0,
                    "rarity": "rare",
                    "required_achievements": {"min_transactions": 5}
                },
                {
                    "puzzle_name": "espresso_day_4",
                    "position_x": 0, "position_y": 1,
                    "rarity": "common",
                    "required_achievements": {"min_spent_usd": 50}
                },
                {
                    "puzzle_name": "espresso_day_5",
                    "position_x": 1, "position_y": 1,
                    "rarity": "epic",
                    "required_achievements": {"min_spent_usd": 100, "business_categories": ["Cafe"]}
                },
                {
                    "puzzle_name": "espresso_day_6",
                    "position_x": 2, "position_y": 1,
                    "rarity": "rare",
                    "required_achievements": {"min_spent_usd": 150}
                },
                {
                    "puzzle_name": "espresso_day_7",
                    "position_x": 0, "position_y": 2,
                    "rarity": "epic",
                    "required_achievements": {"business_categories": ["Cafe", "Barbershop"]}
                },
                {
                    "puzzle_name": "espresso_day_8",
                    "position_x": 1, "position_y": 2,
                    "rarity": "legendary",
                    "required_achievements": {"min_spent_usd": 200, "business_categories": ["Cafe", "Barbershop", "Fitness"]}
                },
                {
                    "puzzle_name": "espresso_day_9",
                    "position_x": 2, "position_y": 2,
                    "rarity": "legendary",
                    "required_achievements": {"min_transactions": 10, "min_spent_usd": 300}
                }
            ]
            
            for puzzle_data in puzzles_data:
                from app.models.nft import NFTPuzzle
                puzzle = NFTPuzzle(
                    id=str(uuid.uuid4()),
                    puzzle_name=puzzle_data["puzzle_name"],
                    image_url=f"https://example.com/puzzles/{puzzle_data['puzzle_name']}.png",
                    position_x=puzzle_data["position_x"],
                    position_y=puzzle_data["position_y"],
                    rarity=puzzle_data["rarity"],
                    required_achievements=puzzle_data["required_achievements"]
                )
                
                db.add(puzzle)
                puzzle_ids.append(puzzle.id)
            
            db.commit()
            return puzzle_ids
            
        except Exception as e:
            print(f"Error creating puzzles: {e}")
            db.rollback()
            return []

    async def check_achievements_and_mint_nft(
        self, 
        user_wallet: str, 
        business_id: str, 
        tokens_amount: int,
        db: Session
    ) -> str:
        """Проверка достижений и чеканка NFT после покупки"""
        try:
            # Проверяем достижения
            updated_achievements = await self.check_and_update_achievements(user_wallet, db)
            
            if not updated_achievements:
                return None
            
            # Получаем все завершенные достижения
            completed_achievements = db.query(UserAchievement).filter(
                UserAchievement.user_wallet == user_wallet,
                UserAchievement.progress >= 100
            ).all()
            
            # Ищем подходящий пазл для чеканки
            for achievement in completed_achievements:
                achievement_obj = db.query(Achievement).filter(
                    Achievement.id == achievement.achievement_id
                ).first()
                
                if achievement_obj and achievement_obj.reward_puzzle_id:
                    # Проверяем, не получил ли пользователь уже этот пазл
                    existing_nft = db.query(UserNFT).filter(
                        UserNFT.user_wallet == user_wallet,
                        UserNFT.puzzle_id == achievement_obj.reward_puzzle_id
                    ).first()
                    
                    if not existing_nft:
                        # Чеканим NFT
                        nft_id = await self.mint_nft(user_wallet, {
                            "puzzle_id": achievement_obj.reward_puzzle_id,
                            "achievement_id": achievement_obj.id,
                            "business_id": business_id,
                            "tokens_earned": tokens_amount
                        })
                        
                        # Сохраняем NFT в БД
                        user_nft = UserNFT(
                            id=str(uuid.uuid4()),
                            user_wallet=user_wallet,
                            puzzle_id=achievement_obj.reward_puzzle_id,
                            nft_metadata={
                                "achievement": achievement_obj.name,
                                "minted_at": str(uuid.uuid4()),
                                "business_id": business_id
                            },
                            solana_signature=nft_id
                        )
                        
                        db.add(user_nft)
                        db.commit()
                        
                        return nft_id
            
            return None
            
        except Exception as e:
            print(f"Error checking achievements and minting NFT: {e}")
            db.rollback()
            return None

    def create_coffee_collection_puzzles(self, db: Session) -> List[str]:
        """Создание пазлов для коллекции кофейни (3 картинки)"""
        puzzle_ids = []
        
        try:
            # Коллекция 1: Coffee Bean Collection
            coffee_bean_puzzles = [
                {
                    "puzzle_name": "coffee_bean_1",
                    "image_name": "coffee_beans/coffee_bean_1",
                    "position_x": 0, "position_y": 0,
                    "rarity": "common",
                    "required_achievements": {"min_transactions": 1, "business_categories": ["Cafe"]}
                },
                {
                    "puzzle_name": "coffee_bean_2", 
                    "image_name": "coffee_beans/coffee_bean_2",
                    "position_x": 1, "position_y": 0,
                    "rarity": "common",
                    "required_achievements": {"min_transactions": 2, "business_categories": ["Cafe"]}
                },
                {
                    "puzzle_name": "coffee_bean_3",
                    "image_name": "coffee_beans/coffee_bean_3",
                    "position_x": 2, "position_y": 0,
                    "rarity": "rare",
                    "required_achievements": {"min_transactions": 3, "business_categories": ["Cafe"]}
                }
            ]
            
            # Коллекция 2: Espresso Collection  
            espresso_puzzles = [
                {
                    "puzzle_name": "espresso_1",
                    "image_name": "espresso/espresso_1",
                    "position_x": 0, "position_y": 0,
                    "rarity": "common",
                    "required_achievements": {"min_spent_usd": 25, "business_categories": ["Cafe"]}
                },
                {
                    "puzzle_name": "espresso_2",
                    "image_name": "espresso/espresso_2", 
                    "position_x": 1, "position_y": 0,
                    "rarity": "rare",
                    "required_achievements": {"min_spent_usd": 50, "business_categories": ["Cafe"]}
                },
                {
                    "puzzle_name": "espresso_3",
                    "image_name": "espresso/espresso_3",
                    "position_x": 2, "position_y": 0,
                    "rarity": "epic",
                    "required_achievements": {"min_spent_usd": 100, "business_categories": ["Cafe"]}
                }
            ]
            
            # Коллекция 3: Latte Art Collection
            latte_puzzles = [
                {
                    "puzzle_name": "latte_art_1",
                    "image_name": "latte_art/latte_art_1",
                    "position_x": 0, "position_y": 0,
                    "rarity": "rare",
                    "required_achievements": {"min_transactions": 5, "min_spent_usd": 75, "business_categories": ["Cafe"]}
                },
                {
                    "puzzle_name": "latte_art_2",
                    "image_name": "latte_art/latte_art_2",
                    "position_x": 1, "position_y": 0,
                    "rarity": "epic",
                    "required_achievements": {"min_transactions": 7, "min_spent_usd": 150, "business_categories": ["Cafe"]}
                },
                {
                    "puzzle_name": "latte_art_3",
                    "image_name": "latte_art/latte_art_3",
                    "position_x": 2, "position_y": 0,
                    "rarity": "legendary",
                    "required_achievements": {"min_transactions": 10, "min_spent_usd": 250, "business_categories": ["Cafe"]}
                }
            ]
            
            all_puzzles = coffee_bean_puzzles + espresso_puzzles + latte_puzzles
            
            for puzzle_data in all_puzzles:
                puzzle = NFTPuzzle(
                    id=str(uuid.uuid4()),
                    puzzle_name=puzzle_data["puzzle_name"],
                    image_url=f"/images/nft_pictures/{puzzle_data['image_name']}.jpg",
                    position_x=puzzle_data["position_x"],
                    position_y=puzzle_data["position_y"],
                    rarity=puzzle_data["rarity"],
                    required_achievements=puzzle_data["required_achievements"]
                )
                
                db.add(puzzle)
                puzzle_ids.append(puzzle.id)
            
            db.commit()
            return puzzle_ids
            
        except Exception as e:
            print(f"Error creating coffee collection puzzles: {e}")
            db.rollback()
            return []
