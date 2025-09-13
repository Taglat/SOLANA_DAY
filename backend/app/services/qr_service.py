import qrcode
import io
import base64
from typing import Dict, Any


class QRService:
    def __init__(self):
        self.qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
    
    def generate_qr_code(self, data: Dict[str, Any]) -> str:
        """Генерация QR кода и возврат base64 строки"""
        import json
        
        # Конвертируем данные в JSON строку
        json_data = json.dumps(data, ensure_ascii=False)
        
        # Создаем QR код
        self.qr.clear()
        self.qr.add_data(json_data)
        self.qr.make(fit=True)
        
        # Создаем изображение
        img = self.qr.make_image(fill_color="black", back_color="white")
        
        # Конвертируем в base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return img_str
    
    def generate_qr_code_for_purchase(
        self, 
        business_id: str, 
        amount_usd: float, 
        user_wallet: str
    ) -> str:
        """Генерация QR кода для покупки"""
        data = {
            "type": "purchase",
            "business_id": business_id,
            "amount_usd": amount_usd,
            "user_wallet": user_wallet,
            "timestamp": int(__import__('time').time())
        }
        return self.generate_qr_code(data)
    
    def generate_qr_code_for_redemption(
        self, 
        business_id: str, 
        discount_percentage: int, 
        user_wallet: str
    ) -> str:
        """Генерация QR кода для скидки"""
        data = {
            "type": "redemption",
            "business_id": business_id,
            "discount_percentage": discount_percentage,
            "user_wallet": user_wallet,
            "timestamp": int(__import__('time').time())
        }
        return self.generate_qr_code(data)
