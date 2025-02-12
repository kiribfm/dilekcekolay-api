from openai import OpenAI, OpenAIError
from app.core.config import settings
from app.core.exceptions import AIServiceError, ValidationError, get_error_message
from app.schemas.petition import PetitionType
from typing import Dict, Any, Optional
from app.core.logger import ai_logger
import logging
import json

# Logger yapılandırması
logger = logging.getLogger(__name__)

class AIHandler:
    """AI servisi ile iletişimi yöneten sınıf"""

    def __init__(self):
        """OpenAI client'ı başlat"""
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.AI_MODEL_BASIC
        self.max_tokens = settings.AI_MAX_TOKENS
        self.temperature = settings.AI_TEMPERATURE

    def generate_petition(self, petition_type: PetitionType, data: Dict[str, Any]) -> str:
        """
        AI ile dilekçe içeriği oluşturur.

        Args:
            petition_type: Dilekçe tipi
            data: Dilekçe verileri

        Returns:
            str: Oluşturulan dilekçe içeriği

        Raises:
            ValidationError: Geçersiz veri
            AIServiceError: AI servisi hatası
        """
        try:
            self._validate_data(data)
            prompt = self._create_prompt(petition_type, data)
            
            ai_logger.info("Generating petition", type=petition_type.value)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            content = response.choices[0].message.content
            ai_logger.info("Petition generated successfully")
            return self._format_response(content)
            
        except ValidationError as e:
            ai_logger.error("Validation error", error=str(e))
            raise
        except OpenAIError as e:
            ai_logger.error("OpenAI API error", error=str(e))
            raise AIServiceError(detail=get_error_message("AI_SERVICE_ERROR"))
        except Exception as e:
            ai_logger.error("Unexpected error", error=str(e))
            raise AIServiceError(detail=get_error_message("AI_SERVICE_ERROR"))

    def _validate_data(self, data: Dict[str, Any]) -> None:
        """
        Dilekçe verilerini doğrular.

        Args:
            data: Doğrulanacak veriler

        Raises:
            ValidationError: Eksik veya geçersiz veri
        """
        required_fields = {
            'full_name': str,
            'id_number': str,
            'incident_date': str,
            'incident_details': str
        }
        
        for field, field_type in required_fields.items():
            if field not in data:
                raise ValidationError(detail=f"Missing required field: {field}")
            if not isinstance(data[field], field_type):
                raise ValidationError(detail=f"Invalid type for field: {field}")
            if not data[field]:
                raise ValidationError(detail=f"Empty value for field: {field}")

    def _create_prompt(self, petition_type: PetitionType, data: Dict[str, Any]) -> str:
        """
        AI için prompt oluşturur.

        Args:
            petition_type: Dilekçe tipi
            data: Dilekçe verileri

        Returns:
            str: Oluşturulan prompt
        """
        return f"""
        Lütfen aşağıdaki bilgilere göre bir {PetitionType.get_description(petition_type)} hazırla:
        
        Ad Soyad: {data['full_name']}
        TC Kimlik No: {data['id_number']}
        Olay Tarihi: {data['incident_date']}
        Olay Detayı: {data['incident_details']}
        
        Dilekçeyi resmi formatta ve tüm gerekli bölümleriyle hazırla.
        """

    def _format_response(self, content: str) -> str:
        """
        AI yanıtını formatlar.

        Args:
            content: AI yanıtı

        Returns:
            str: Formatlanmış içerik
        """
        # Gereksiz boşlukları temizle
        content = ' '.join(content.split())
        
        # Paragrafları düzenle
        paragraphs = content.split('\n')
        formatted_paragraphs = [p.strip() for p in paragraphs if p.strip()]
        
        return '\n\n'.join(formatted_paragraphs)

    def update_model(self, is_premium: bool) -> None:
        """
        Kullanıcı tipine göre AI modelini günceller.

        Args:
            is_premium: Premium kullanıcı mı
        """
        self.model = settings.AI_MODEL_PREMIUM if is_premium else settings.AI_MODEL_BASIC 