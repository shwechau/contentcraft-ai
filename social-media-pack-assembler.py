"""
Social Media Pack Assembler - Day 3 Implementation
Handles packaging of content + visuals into complete YouTube social media packs
"""

import json
import base64
import zipfile
import io
from datetime import datetime
from typing import Dict, List, Any
import os

class SocialMediaPackAssembler:
    def __init__(self):
        self.pack_templates = {
            'youtube': {
                'content_files': ['title.txt', 'description.txt', 'script.txt', 'hashtags.txt'],
                'visual_files': ['thumbnail_ai.png', 'thumbnail_text.png', 'thumbnail_minimal.png'],
                'metadata_file': 'pack_metadata.json'
            }
        }
    
    def create_youtube_pack(self, content_data: Dict, visual_data: Dict, user_input: Dict) -> Dict:
        """
        Assembles complete YouTube social media pack
        """
        try:
            pack_id = f"youtube_pack_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Create pack structure
            pack_data = {
                'pack_id': pack_id,
                'platform': 'youtube',
                'created_at': datetime.now().isoformat(),
                'brand_name': user_input.get('brand_name', ''),
                'topic': user_input.get('topic', ''),
                'content': self._format_content_files(content_data),
                'visuals': self._format_visual_files(visual_data),
                'metadata': self._create_pack_metadata(content_data, visual_data, user_input),
                'download_ready': True
            }
            
            # Generate downloadable zip
            zip_buffer = self._create_downloadable_zip(pack_data)
            pack_data['download_url'] = f"/download/{pack_id}.zip"
            pack_data['zip_size'] = len(zip_buffer)
            
            return {
                'success': True,
                'pack': pack_data,
                'zip_buffer': zip_buffer
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Pack assembly failed: {str(e)}"
            }
    
    def _format_content_files(self, content_data: Dict) -> Dict:
        """Format content data into file structure"""
        return {
            'title': {
                'filename': 'title.txt',
                'content': content_data.get('title', ''),
                'character_count': len(content_data.get('title', ''))
            },
            'description': {
                'filename': 'description.txt',
                'content': content_data.get('description', ''),
                'word_count': len(content_data.get('description', '').split())
            },
            'script': {
                'filename': 'script.txt',
                'content': content_data.get('script', ''),
                'estimated_duration': self._estimate_video_duration(content_data.get('script', ''))
            },
            'hashtags': {
                'filename': 'hashtags.txt',
                'content': '\n'.join(content_data.get('hashtags', [])),
                'tag_count': len(content_data.get('hashtags', []))
            }
        }
    
    def _format_visual_files(self, visual_data: Dict) -> Dict:
        """Format visual data into file structure"""
        visuals = {}
        
        for variant_name, variant_data in visual_data.get('variants', {}).items():
            visuals[variant_name] = {
                'filename': f'thumbnail_{variant_name}.png',
                'image_data': variant_data.get('image_data', ''),
                'style': variant_data.get('style', ''),
                'dimensions': variant_data.get('dimensions', '1280x720'),
                'file_size': len(base64.b64decode(variant_data.get('image_data', ''))) if variant_data.get('image_data') else 0
            }
        
        return visuals
    
    def _create_pack_metadata(self, content_data: Dict, visual_data: Dict, user_input: Dict) -> Dict:
        """Create comprehensive pack metadata"""
        return {
            'brand_info': {
                'name': user_input.get('brand_name', ''),
                'colors': user_input.get('brand_colors', []),
                'style': user_input.get('style_preference', '')
            },
            'content_specs': {
                'topic': user_input.get('topic', ''),
                'tone': user_input.get('tone', ''),
                'video_length': user_input.get('video_length', ''),
                'target_audience': user_input.get('target_audience', '')
            },
            'generated_assets': {
                'content_files': len(content_data),
                'visual_variants': len(visual_data.get('variants', {})),
                'total_hashtags': len(content_data.get('hashtags', []))
            },
            'usage_guidelines': {
                'platform': 'YouTube',
                'optimal_posting_time': self._suggest_posting_time(user_input.get('tone', '')),
                'engagement_tips': self._generate_engagement_tips(content_data, user_input)
            }
        }
    
    def _create_downloadable_zip(self, pack_data: Dict) -> bytes:
        """Create downloadable zip file with all assets"""
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Add content files
            for content_type, content_info in pack_data['content'].items():
                zip_file.writestr(
                    content_info['filename'],
                    content_info['content']
                )
            
            # Add visual files
            for visual_type, visual_info in pack_data['visuals'].items():
                if visual_info.get('image_data'):
                    image_bytes = base64.b64decode(visual_info['image_data'])
                    zip_file.writestr(
                        visual_info['filename'],
                        image_bytes
                    )
            
            # Add metadata file
            zip_file.writestr(
                'pack_metadata.json',
                json.dumps(pack_data['metadata'], indent=2)
            )
            
            # Add usage guide
            usage_guide = self._create_usage_guide(pack_data)
            zip_file.writestr('USAGE_GUIDE.txt', usage_guide)
        
        zip_buffer.seek(0)
        return zip_buffer.getvalue()
    
    def _estimate_video_duration(self, script: str) -> str:
        """Estimate video duration based on script length"""
        words = len(script.split())
        # Average speaking rate: 150-160 words per minute
        minutes = words / 155
        
        if minutes < 1:
            return f"{int(minutes * 60)} seconds"
        elif minutes < 60:
            return f"{minutes:.1f} minutes"
        else:
            hours = int(minutes // 60)
            mins = int(minutes % 60)
            return f"{hours}h {mins}m"
    
    def _suggest_posting_time(self, tone: str) -> str:
        """Suggest optimal posting times based on content tone"""
        suggestions = {
            'professional': '9 AM - 11 AM EST (Business hours)',
            'casual': '7 PM - 9 PM EST (Evening leisure)',
            'educational': '2 PM - 4 PM EST (Afternoon learning)',
            'entertaining': '6 PM - 8 PM EST (Prime time)'
        }
        return suggestions.get(tone.lower(), '7 PM - 9 PM EST (General optimal)')
    
    def _generate_engagement_tips(self, content_data: Dict, user_input: Dict) -> List[str]:
        """Generate platform-specific engagement tips"""
        tips = [
            "Pin your best comment to encourage discussion",
            "Respond to comments within first 2 hours for better reach",
            "Use end screens to promote related videos",
            "Add timestamps in description for longer videos"
        ]
        
        # Add tone-specific tips
        tone = user_input.get('tone', '').lower()
        if tone == 'educational':
            tips.append("Include key takeaways in description")
        elif tone == 'entertaining':
            tips.append("Create cliffhangers to increase watch time")
        elif tone == 'professional':
            tips.append("Include relevant industry hashtags")
        
        return tips
    
    def _create_usage_guide(self, pack_data: Dict) -> str:
        """Create comprehensive usage guide"""
        guide = f"""
YOUTUBE SOCIAL MEDIA PACK - USAGE GUIDE
=====================================

Pack ID: {pack_data['pack_id']}
Created: {pack_data['created_at']}
Brand: {pack_data['brand_name']}

CONTENTS:
---------
✓ title.txt - Video title ({pack_data['content']['title']['character_count']} characters)
✓ description.txt - Video description ({pack_data['content']['description']['word_count']} words)
✓ script.txt - Video script (Est. duration: {pack_data['content']['script']['estimated_duration']})
✓ hashtags.txt - Relevant hashtags ({pack_data['content']['hashtags']['tag_count']} tags)
✓ thumbnail_ai.png - AI-generated thumbnail
✓ thumbnail_text.png - Text-based thumbnail
✓ thumbnail_minimal.png - Minimal design thumbnail

USAGE INSTRUCTIONS:
------------------
1. Upload your video to YouTube
2. Copy title from title.txt to video title field
3. Copy description from description.txt (includes hashtags)
4. Choose your preferred thumbnail variant
5. Use script.txt for video creation or voiceover

OPTIMIZATION TIPS:
-----------------
"""
        
        for tip in pack_data['metadata']['usage_guidelines']['engagement_tips']:
            guide += f"• {tip}\n"
        
        guide += f"\nOPTIMAL POSTING TIME: {pack_data['metadata']['usage_guidelines']['optimal_posting_time']}\n"
        
        return guide

# Example usage and testing
if __name__ == "__main__":
    assembler = SocialMediaPackAssembler()
    
    # Test data
    sample_content = {
        'title': 'How to Master YouTube Content Creation in 2024',
        'description': 'Learn the essential strategies for creating engaging YouTube content...',
        'script': 'Welcome to today\'s video where we\'ll explore...',
        'hashtags': ['#YouTube', '#ContentCreation', '#VideoMarketing']
    }
    
    sample_visuals = {
        'variants': {
            'ai': {'image_data': 'base64_encoded_image_data', 'style': 'AI Generated'},
            'text': {'image_data': 'base64_encoded_image_data', 'style': 'Text Based'},
            'minimal': {'image_data': 'base64_encoded_image_data', 'style': 'Minimal'}
        }
    }
    
    sample_input = {
        'brand_name': 'TechTutorials',
        'topic': 'YouTube Growth',
        'tone': 'educational',
        'video_length': 'medium'
    }
    
    result = assembler.create_youtube_pack(sample_content, sample_visuals, sample_input)
    print(f"Pack assembly result: {result['success']}")