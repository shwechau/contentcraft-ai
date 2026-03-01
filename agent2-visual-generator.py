import openai
import requests
import json
import redis
import os
from typing import Dict, List, Optional
import base64
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import colorsys

class Agent2VisualGenerator:
    def __init__(self, openai_api_key: str, redis_host: str = 'localhost', redis_port: int = 6379):
        self.openai_client = openai.OpenAI(api_key=openai_api_key)
        self.redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
        
    def generate_visuals(self, content_data: Dict) -> Dict:
        """
        Generate YouTube thumbnails and graphics based on Agent 1 content
        """
        try:
            # Extract content information
            title = content_data.get('title', '')
            description = content_data.get('description', '')
            topic = content_data.get('topic', '')
            tone = content_data.get('tone', 'professional')
            brand_colors = content_data.get('brand_colors', ['#FF0000', '#FFFFFF'])
            style_preference = content_data.get('style_preference', 'modern')
            
            # Generate multiple visual variants
            variants = []
            
            # Variant 1: AI-generated thumbnail
            ai_thumbnail = self._generate_ai_thumbnail(title, topic, tone, style_preference)
            if ai_thumbnail:
                variants.append({
                    'type': 'ai_generated',
                    'image_url': ai_thumbnail,
                    'description': 'AI-generated YouTube thumbnail'
                })
            
            # Variant 2: Text-based thumbnail with brand colors
            text_thumbnail = self._generate_text_thumbnail(title, brand_colors, style_preference)
            if text_thumbnail:
                variants.append({
                    'type': 'text_based',
                    'image_data': text_thumbnail,
                    'description': 'Brand-colored text thumbnail'
                })
            
            # Variant 3: Minimalist design
            minimal_thumbnail = self._generate_minimal_thumbnail(title, topic, brand_colors)
            if minimal_thumbnail:
                variants.append({
                    'type': 'minimal',
                    'image_data': minimal_thumbnail,
                    'description': 'Minimalist design thumbnail'
                })
            
            # Package visual output
            visual_output = {
                'status': 'success',
                'variants': variants,
                'metadata': {
                    'brand_colors': brand_colors,
                    'style_preference': style_preference,
                    'content_title': title,
                    'generation_timestamp': content_data.get('timestamp')
                }
            }
            
            return visual_output
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'variants': []
            }
    
    def _generate_ai_thumbnail(self, title: str, topic: str, tone: str, style: str) -> Optional[str]:
        """Generate thumbnail using DALL-E API"""
        try:
            # Create detailed prompt for thumbnail generation
            prompt = f"""
            Create a YouTube thumbnail for a video titled "{title}" about {topic}.
            Style: {style}, Tone: {tone}
            Requirements:
            - High contrast and eye-catching
            - YouTube thumbnail dimensions (1280x720)
            - Bold, readable text elements
            - Engaging visual composition
            - Professional quality
            """
            
            response = self.openai_client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1792x1024",  # Closest to 16:9 ratio
                quality="standard",
                n=1
            )
            
            return response.data[0].url
            
        except Exception as e:
            print(f"AI thumbnail generation error: {e}")
            return None
    
    def _generate_text_thumbnail(self, title: str, brand_colors: List[str], style: str) -> Optional[str]:
        """Generate text-based thumbnail with brand colors"""
        try:
            # Create 1280x720 image (YouTube thumbnail size)
            img = Image.new('RGB', (1280, 720), color=brand_colors[0])
            draw = ImageDraw.Draw(img)
            
            # Try to load a font, fallback to default
            try:
                font_size = 80 if len(title) < 30 else 60
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                font = ImageFont.load_default()
            
            # Calculate text position for centering
            text_bbox = draw.textbbox((0, 0), title, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            
            x = (1280 - text_width) // 2
            y = (720 - text_height) // 2
            
            # Add text shadow for better readability
            shadow_color = '#000000' if brand_colors[0] != '#000000' else '#FFFFFF'
            draw.text((x+3, y+3), title, font=font, fill=shadow_color)
            
            # Main text
            text_color = brand_colors[1] if len(brand_colors) > 1 else '#FFFFFF'
            draw.text((x, y), title, font=font, fill=text_color)
            
            # Add decorative elements based on style
            if style == 'modern':
                # Add geometric shapes
                draw.rectangle([50, 50, 150, 150], fill=brand_colors[1] if len(brand_colors) > 1 else '#FFFFFF')
                draw.rectangle([1130, 570, 1230, 670], fill=brand_colors[1] if len(brand_colors) > 1 else '#FFFFFF')
            
            # Convert to base64 for easy transmission
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            img_str = base64.b64encode(buffer.getvalue()).decode()
            
            return img_str
            
        except Exception as e:
            print(f"Text thumbnail generation error: {e}")
            return None
    
    def _generate_minimal_thumbnail(self, title: str, topic: str, brand_colors: List[str]) -> Optional[str]:
        """Generate minimalist thumbnail design"""
        try:
            # Create clean, minimal design
            img = Image.new('RGB', (1280, 720), color='#FFFFFF')
            draw = ImageDraw.Draw(img)
            
            # Use primary brand color for accent
            accent_color = brand_colors[0] if brand_colors else '#FF0000'
            
            # Draw minimal geometric elements
            draw.rectangle([0, 0, 1280, 100], fill=accent_color)  # Top bar
            draw.rectangle([0, 620, 1280, 720], fill=accent_color)  # Bottom bar
            
            # Title text
            try:
                font = ImageFont.truetype("arial.ttf", 70)
            except:
                font = ImageFont.load_default()
            
            # Center the title
            text_bbox = draw.textbbox((0, 0), title, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            x = (1280 - text_width) // 2
            y = 300
            
            draw.text((x, y), title, font=font, fill='#333333')
            
            # Add topic subtitle
            try:
                subtitle_font = ImageFont.truetype("arial.ttf", 40)
            except:
                subtitle_font = ImageFont.load_default()
            
            subtitle_bbox = draw.textbbox((0, 0), topic, font=subtitle_font)
            subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
            subtitle_x = (1280 - subtitle_width) // 2
            
            draw.text((subtitle_x, y + 100), topic, font=subtitle_font, fill='#666666')
            
            # Convert to base64
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            img_str = base64.b64encode(buffer.getvalue()).decode()
            
            return img_str
            
        except Exception as e:
            print(f"Minimal thumbnail generation error: {e}")
            return None
    
    def process_agent1_output(self, agent1_job_id: str) -> Dict:
        """
        Process output from Agent 1 and generate visuals
        """
        try:
            # Retrieve Agent 1 output from Redis
            agent1_output = self.redis_client.get(f"agent1_output:{agent1_job_id}")
            
            if not agent1_output:
                return {
                    'status': 'error',
                    'error': 'Agent 1 output not found'
                }
            
            content_data = json.loads(agent1_output)
            
            # Generate visuals based on content
            visual_result = self.generate_visuals(content_data)
            
            # Store Agent 2 output in Redis
            agent2_job_id = f"agent2_{agent1_job_id}"
            self.redis_client.setex(
                f"agent2_output:{agent2_job_id}",
                3600,  # 1 hour expiry
                json.dumps(visual_result)
            )
            
            # Update job status
            self.redis_client.setex(
                f"job_status:{agent2_job_id}",
                3600,
                json.dumps({
                    'status': 'completed',
                    'agent': 'agent2',
                    'timestamp': content_data.get('timestamp'),
                    'variants_count': len(visual_result.get('variants', []))
                })
            )
            
            return {
                'status': 'success',
                'agent2_job_id': agent2_job_id,
                'visual_result': visual_result
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }

# Example usage and testing
if __name__ == "__main__":
    # Initialize Agent 2
    agent2 = Agent2VisualGenerator(openai_api_key=os.environ.get('OPENAI_API_KEY', ''))
    
    # Test data (simulating Agent 1 output)
    test_content = {
        'title': 'How to Master Python in 30 Days',
        'description': 'Complete Python tutorial for beginners',
        'topic': 'Python Programming',
        'tone': 'educational',
        'brand_colors': ['#3776AB', '#FFFFFF'],
        'style_preference': 'modern',
        'timestamp': '2024-02-24T00:11:23.213Z'
    }
    
    # Generate visuals
    result = agent2.generate_visuals(test_content)
    print(json.dumps(result, indent=2))