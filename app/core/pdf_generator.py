from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
from typing import Optional, Dict, Any
import os
from app.core.logger import api_logger  # Yeni import

class PDFGenerator:
    """PDF oluşturma sınıfı"""

    def __init__(self):
        """Font ve stil ayarlarını başlat"""
        # Türkçe karakter desteği için font ekle
        font_path = os.path.join(os.path.dirname(__file__), "fonts", "DejaVuSans.ttf")
        pdfmetrics.registerFont(TTFont("DejaVuSans", font_path))

        # Stiller
        self.styles = getSampleStyleSheet()
        self.styles.add(ParagraphStyle(
            name='Turkish',
            fontName='DejaVuSans',
            fontSize=11,
            leading=14,
            alignment=4  # Justified alignment
        ))

    def create_pdf(
        self,
        content: str,
        output_path: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        PDF dosyası oluşturur.

        Args:
            content: Dilekçe içeriği
            output_path: Çıktı dosya yolu
            metadata: PDF metadata bilgileri

        Raises:
            Exception: PDF oluşturma hatası
        """
        try:
            api_logger.info("Creating PDF", output_path=output_path)  # Yeni log
            
            # PDF dokümanı oluştur
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=2*cm,
                leftMargin=2*cm,
                topMargin=2*cm,
                bottomMargin=2*cm
            )

            # Metadata ekle
            if metadata:
                doc.setAuthor(metadata.get("author", ""))
                doc.setTitle(metadata.get("title", ""))
                doc.setSubject(metadata.get("subject", ""))

            # İçerik elemanları
            elements = []

            # Başlık
            title = metadata.get("title", "DİLEKÇE") if metadata else "DİLEKÇE"
            elements.append(Paragraph(title, self.styles["Heading1"]))
            elements.append(Spacer(1, 12))

            # Tarih
            date_str = datetime.now().strftime("%d/%m/%Y")
            elements.append(Paragraph(f"Tarih: {date_str}", self.styles["Normal"]))
            elements.append(Spacer(1, 12))

            # Ana içerik
            content_paragraphs = content.split('\n')
            for paragraph in content_paragraphs:
                if paragraph.strip():
                    elements.append(Paragraph(paragraph, self.styles["Turkish"]))
                    elements.append(Spacer(1, 6))

            # İmza tablosu
            signature_data = [
                ["Ad Soyad:", "_________________"],
                ["İmza:", "_________________"]
            ]
            signature_table = Table(
                signature_data,
                colWidths=[100, 200],
                style=TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSans'),
                    ('FONTSIZE', (0, 0), (-1, -1), 11),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ])
            )
            elements.append(Spacer(1, 30))
            elements.append(signature_table)

            # PDF oluştur
            doc.build(elements)

            api_logger.info("PDF created successfully")  # Yeni log
        except Exception as e:
            api_logger.error("PDF creation failed", error=str(e))  # Güncellendi
            raise Exception(f"PDF oluşturma hatası: {str(e)}")

    def add_watermark(self, pdf_path: str, watermark_text: str) -> None:
        """
        PDF'e filigran ekler.

        Args:
            pdf_path: PDF dosya yolu
            watermark_text: Filigran metni
        
        Not: Bu metod henüz implement edilmedi
        """
        pass  # TODO: Implement watermark functionality

    def merge_pdfs(self, pdf_paths: list, output_path: str) -> None:
        """
        Birden fazla PDF'i birleştirir.

        Args:
            pdf_paths: PDF dosya yolları listesi
            output_path: Çıktı dosya yolu
        
        Not: Bu metod henüz implement edilmedi
        """
        pass  # TODO: Implement PDF merging functionality 