from PIL import Image, ImageDraw, ImageFont
import os
from django.conf import settings
from .models import Country
from datetime import datetime

class SummaryImageGenerator:
    @staticmethod
    def generate_summary_image():
        """Generate summary image with country statistics"""
        try:
            # Create image
            width, height = 600, 400
            image = Image.new('RGB', (width, height), color='white')
            draw = ImageDraw.Draw(image)
            
            # Try to use a default font (this might need adjustment based on deployment environment)
            try:
                font_large = ImageFont.truetype("arial.ttf", 24)
                font_medium = ImageFont.truetype("arial.ttf", 18)
                font_small = ImageFont.trueType("arial.ttf", 14) # type: ignore
            except:
                # Fallback to default font
                font_large = ImageFont.load_default()
                font_medium = ImageFont.load_default()
                font_small = ImageFont.load_default()
            
            # Get data
            total_countries = Country.objects.count()
            top_countries = Country.objects.exclude(
                estimated_gdp__isnull=True
            ).order_by('-estimated_gdp')[:5]
            
            last_refresh = Country.objects.order_by('-last_refreshed_at').first()
            refresh_time = last_refresh.last_refreshed_at if last_refresh else datetime.now()
            
            # Draw content
            y_position = 20
            
            # Title
            draw.text((20, y_position), "Country GDP Summary", fill='black', font=font_large)
            y_position += 40
            
            # Total countries
            draw.text((20, y_position), f"Total Countries: {total_countries}", fill='black', font=font_medium)
            y_position += 30
            
            # Last refresh
            draw.text((20, y_position), f"Last Refresh: {refresh_time.strftime('%Y-%m-%d %H:%M:%S UTC')}", 
                     fill='black', font=font_medium)
            y_position += 50
            
            # Top 5 countries by GDP
            draw.text((20, y_position), "Top 5 Countries by Estimated GDP:", fill='black', font=font_medium)
            y_position += 30
            
            for i, country in enumerate(top_countries, 1):
                gdp_str = f"{country.estimated_gdp:,.2f}" if country.estimated_gdp else "N/A"
                text = f"{i}. {country.name}: ${gdp_str}"
                draw.text((40, y_position), text, fill='black', font=font_small)
                y_position += 25
            
            # Save image
            image_path = os.path.join(settings.CACHE_DIR, 'summary.png')
            image.save(image_path)
            return image_path
            
        except Exception as e:
            print(f"Error generating image: {e}")
            return None