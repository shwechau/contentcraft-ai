"""
Social Media Pack Assembler - Day 3 Implementation
Packages content + visuals into complete YouTube social media bundles
"""

import json
import base64
import zipfile
import io
from datetime import datetime
from typing import Dict, List, Any
import os

class SocialPackAssembler:
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
                'tone': user_input.get('tone', ''),
                'content': self._format_content(content_data),
                'visuals': self._format_visuals(visual_data),
                'metadata': self._create_metadata(user_input, content_data, visual_data),
                'download_ready': True
            }
            
            # Generate downloadable files
            pack_data['download_bundle'] = self._create_download_bundle(pack_data)
            
            return {
                'success': True,
                'pack_data': pack_data,
                'message': f'YouTube pack {pack_id} assembled successfully'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Pack assembly failed: {str(e)}',
                'pack_data': None
            }
    
    def _format_content(self, content_data: Dict) -> Dict:
        """Format content for pack display"""
        return {
            'title': {
                'text': content_data.get('title', ''),
                'character_count': len(content_data.get('title', '')),
                'seo_optimized': True
            },
            'description': {
                'text': content_data.get('description', ''),
                'character_count': len(content_data.get('description', '')),
                'includes_hashtags': '#' in content_data.get('description', '')
            },
            'script': {
                'text': content_data.get('script', ''),
                'word_count': len(content_data.get('script', '').split()),
                'estimated_duration': self._estimate_video_duration(content_data.get('script', ''))
            },
            'hashtags': {
                'tags': content_data.get('hashtags', []),
                'count': len(content_data.get('hashtags', [])),
                'trending_score': content_data.get('hashtag_scores', {})
            }
        }
    
    def _format_visuals(self, visual_data: Dict) -> Dict:
        """Format visuals for pack display"""
        return {
            'thumbnails': {
                'ai_generated': {
                    'image_data': visual_data.get('ai_thumbnail', ''),
                    'style': 'AI Generated',
                    'description': 'Creative AI-generated thumbnail'
                },
                'text_based': {
                    'image_data': visual_data.get('text_thumbnail', ''),
                    'style': 'Text Overlay',
                    'description': 'Bold text-focused design'
                },
                'minimal': {
                    'image_data': visual_data.get('minimal_thumbnail', ''),
                    'style': 'Minimal',
                    'description': 'Clean, minimal aesthetic'
                }
            },
            'total_variants': 3,
            'recommended': 'ai_generated'
        }
    
    def _create_metadata(self, user_input: Dict, content_data: Dict, visual_data: Dict) -> Dict:
        """Create comprehensive pack metadata"""
        return {
            'user_preferences': {
                'brand_name': user_input.get('brand_name', ''),
                'topic': user_input.get('topic', ''),
                'tone': user_input.get('tone', ''),
                'video_length': user_input.get('video_length', ''),
                'brand_colors': user_input.get('brand_colors', ''),
                'style_preference': user_input.get('style_preference', '')
            },
            'content_stats': {
                'title_length': len(content_data.get('title', '')),
                'description_length': len(content_data.get('description', '')),
                'script_word_count': len(content_data.get('script', '').split()),
                'hashtag_count': len(content_data.get('hashtags', []))
            },
            'visual_stats': {
                'thumbnail_variants': 3,
                'style_variations': ['AI Generated', 'Text Overlay', 'Minimal']
            },
            'optimization_tips': self._generate_optimization_tips(content_data, visual_data),
            'publishing_checklist': self._create_publishing_checklist()
        }
    
    def _estimate_video_duration(self, script: str) -> str:
        """Estimate video duration based on script word count"""
        word_count = len(script.split())
        # Average speaking rate: 150-160 words per minute
        minutes = word_count / 155
        
        if minutes < 1:
            return f"{int(minutes * 60)} seconds"
        elif minutes < 60:
            return f"{int(minutes)} minutes"
        else:
            hours = int(minutes // 60)
            mins = int(minutes % 60)
            return f"{hours}h {mins}m"
    
    def _generate_optimization_tips(self, content_data: Dict, visual_data: Dict) -> List[str]:
        """Generate optimization tips for the content pack"""
        tips = []
        
        title = content_data.get('title', '')
        if len(title) > 60:
            tips.append("Consider shortening title for better mobile display")
        
        description = content_data.get('description', '')
        if len(description) < 125:
            tips.append("Add more detail to description for better SEO")
        
        hashtags = content_data.get('hashtags', [])
        if len(hashtags) < 3:
            tips.append("Consider adding more relevant hashtags")
        
        tips.extend([
            "Upload thumbnail before publishing video",
            "Add end screens and cards for engagement",
            "Schedule publication during peak audience hours",
            "Create engaging first 15 seconds to reduce drop-off"
        ])
        
        return tips
    
    def _create_publishing_checklist(self) -> List[Dict]:
        """Create publishing checklist for user"""
        return [
            {"task": "Upload video file to YouTube", "completed": False},
            {"task": "Add generated title", "completed": False},
            {"task": "Paste description with hashtags", "completed": False},
            {"task": "Upload custom thumbnail", "completed": False},
            {"task": "Set video visibility (public/unlisted)", "completed": False},
            {"task": "Add to relevant playlists", "completed": False},
            {"task": "Schedule or publish immediately", "completed": False},
            {"task": "Share on other social platforms", "completed": False}
        ]
    
    def _create_download_bundle(self, pack_data: Dict) -> str:
        """Create downloadable ZIP bundle"""
        try:
            # Create in-memory ZIP file
            zip_buffer = io.BytesIO()
            
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                # Add content files
                content = pack_data['content']
                zip_file.writestr('title.txt', content['title']['text'])
                zip_file.writestr('description.txt', content['description']['text'])
                zip_file.writestr('script.txt', content['script']['text'])
                zip_file.writestr('hashtags.txt', '\n'.join(content['hashtags']['tags']))
                
                # Add metadata
                zip_file.writestr('pack_metadata.json', json.dumps(pack_data['metadata'], indent=2))
                
                # Add publishing checklist
                checklist_text = '\n'.join([f"☐ {item['task']}" for item in pack_data['metadata']['publishing_checklist']])
                zip_file.writestr('publishing_checklist.txt', checklist_text)
                
                # Add optimization tips
                tips_text = '\n'.join([f"• {tip}" for tip in pack_data['metadata']['optimization_tips']])
                zip_file.writestr('optimization_tips.txt', tips_text)
            
            # Convert to base64 for storage/transmission
            zip_buffer.seek(0)
            zip_base64 = base64.b64encode(zip_buffer.getvalue()).decode('utf-8')
            
            return zip_base64
            
        except Exception as e:
            print(f"Error creating download bundle: {e}")
            return ""

# Example usage and testing
if __name__ == "__main__":
    assembler = SocialPackAssembler()
    
    # Test data
    sample_user_input = {
        'brand_name': 'TechReviews Pro',
        'topic': 'iPhone 15 Review',
        'tone': 'professional',
        'video_length': 'medium',
        'brand_colors': '#FF6B6B, #4ECDC4',
        'style_preference': 'modern'
    }
    
    sample_content = {
        'title': 'iPhone 15 Pro Max: Complete Review & Camera Test',
        'description': 'Comprehensive iPhone 15 Pro Max review covering camera, performance, battery life, and value. Is it worth the upgrade? #iPhone15 #TechReview #Apple',
        'script': 'Welcome back to TechReviews Pro! Today we\'re diving deep into the iPhone 15 Pro Max...',
        'hashtags': ['#iPhone15', '#TechReview', '#Apple', '#Smartphone', '#CameraTest']
    }
    
    sample_visuals = {
        'ai_thumbnail': 'base64_image_data_here',
        'text_thumbnail': 'base64_image_data_here',
        'minimal_thumbnail': 'base64_image_data_here'
    }
    
    # Test pack assembly
    result = assembler.create_youtube_pack(sample_content, sample_visuals, sample_user_input)
    
    if result['success']:
        print("✅ Pack assembled successfully!")
        print(f"Pack ID: {result['pack_data']['pack_id']}")
        print(f"Content files: {len(result['pack_data']['content'])}")
        print(f"Visual variants: {result['pack_data']['visuals']['total_variants']}")
    else:
        print(f"❌ Pack assembly failed: {result['error']}")