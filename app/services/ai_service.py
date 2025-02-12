from openai import OpenAI
from dotenv import load_dotenv
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables")

client = OpenAI(api_key=api_key)

def generate_petition(petition_type: str, details: str) -> str:
    try:
        logger.info(f"Generating petition for type: {petition_type}")
        
        prompt = f"""
        Aşağıdaki konuda resmi bir dilekçe oluştur:
        Dilekçe Türü: {petition_type}
        Detaylar: {details}
        
        Lütfen Türkiye Cumhuriyeti dilekçe formatına uygun, resmi ve profesyonel bir dil kullan.
        """
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sen profesyonel bir hukuk asistanısın. Türk hukuk sistemine uygun resmi dilekçeler oluşturuyorsun."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
        )
        
        logger.info("Successfully generated petition")
        return response.choices[0].message.content
        
    except Exception as e:
        logger.error(f"Error generating petition: {str(e)}")
        raise Exception(f"Failed to generate petition: {str(e)}")