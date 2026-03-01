"""
Flask Application Integration - Day 3 Implementation
Complete web application integrating all components
"""

from flask import Flask, request, jsonify, render_template_string, send_file
from flask_cors import CORS
import json
import io
import os
from datetime import datetime

# Import our components
import sys
sys.path.append('.')

# Mock imports - in real implementation these would be actual imports
# from agent1_youtube_generator import YouTubeContentGenerator
# from agent2_visual_generator import VisualContentGenerator
# from agent_orchestrator import AgentOrchestrator
# from social_media_pack_assembler import SocialMediaPackAssembler

app = Flask(__name__)
CORS(app)

# Initialize components
class MockYouTubeContentGenerator:
    def generate_content(self, user_input):
        return {
            'title': f"{user_input['topic']} - Complete Guide for {user_input['brand_name']}",
            'description': f"In this comprehensive guide, we'll explore {user_input['topic']} and show you exactly how to implement these strategies for your business. Perfect for {user_input.get('target_audience', 'content creators')} looking to grow their presence.\n\n🔥 What you'll learn:\n✅ Key strategies for {user_input['topic']}\n✅ Step-by-step implementation\n✅ Real-world examples\n✅ Pro tips and tricks\n\n👍 Like this video if it helped you!\n🔔 Subscribe for more {user_input['tone']} content!\n💬 Comment your questions below!\n\n#YouTube #ContentCreation #VideoMarketing #DigitalMarketing #SocialMedia #{user_input['topic'].replace(' ', '')}\n\n---\nCreated by {user_input['brand_name']} | Follow us for more amazing content!",
            'script': f"Welcome back to {user_input['brand_name']}! I'm so excited to share this with you today.\n\nIn today's video, we're diving deep into {user_input['topic']}. This is going to be an incredible journey where you'll learn practical strategies that you can implement right away.\n\n[INTRO HOOK]\nBy the end of this video, you'll have a complete understanding of {user_input['topic']} and exactly how to use it to grow your {user_input.get('target_audience', 'business')}.\n\n[MAIN CONTENT]\nLet's start with the fundamentals. {user_input['topic']} is crucial because...\n\n[Point 1] First, we need to understand...\n[Point 2] Next, let's look at...\n[Point 3] Finally, the most important aspect is...\n\n[CALL TO ACTION]\nIf you found this valuable, make sure to hit that like button, subscribe for more {user_input['tone']} content, and ring the notification bell so you never miss our latest videos!\n\n[OUTRO]\nThanks for watching, and I'll see you in the next one!",
            'hashtags': ['#YouTube', '#ContentCreation', '#VideoMarketing', '#DigitalMarketing', '#SocialMedia', f"#{user_input['topic'].replace(' ', '')}", f"#{user_input['brand_name'].replace(' ', '')}"],
            'metadata': {
                'tone': user_input['tone'],
                'target_audience': user_input.get('target_audience', 'general'),
                'video_length': user_input.get('video_length', 'medium'),
                'brand_colors': user_input.get('brand_colors', [])
            }
        }

class MockVisualContentGenerator:
    def generate_visuals(self, content_data, user_input):
        return {
            'variants': {
                'ai': {
                    'image_data': 'mock_base64_ai_thumbnail',
                    'style': 'AI Generated',
                    'dimensions': '1280x720',
                    'description': f"AI-generated thumbnail featuring {user_input['topic']} with dynamic visuals"
                },
                'text': {
                    'image_data': 'mock_base64_text_thumbnail',
                    'style': 'Text Based',
                    'dimensions': '1280x720',
                    'description': f"Bold text-based design highlighting '{content_data['title']}'"
                },
                'minimal': {
                    'image_data': 'mock_base64_minimal_thumbnail',
                    'style': 'Minimal Design',
                    'dimensions': '1280x720',
                    'description': f"Clean, minimal design with {user_input['brand_name']} branding"
                }
            }
        }

class MockSocialMediaPackAssembler:
    def create_youtube_pack(self, content_data, visual_data, user_input):
        pack_id = f"youtube_pack_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return {
            'success': True,
            'pack': {
                'pack_id': pack_id,
                'platform': 'youtube',
                'created_at': datetime.now().isoformat(),
                'brand_name': user_input.get('brand_name', ''),
                'topic': user_input.get('topic', ''),
                'content': {
                    'title': {
                        'content': content_data['title'],
                        'character_count': len(content_data['title'])
                    },
                    'description': {
                        'content': content_data['description'],
                        'word_count': len(content_data['description'].split())
                    },
                    'script': {
                        'content': content_data['script'],
                        'estimated_duration': self._estimate_duration(content_data['script'])
                    },
                    'hashtags': {
                        'content': ' '.join(content_data['hashtags']),
                        'tag_count': len(content_data['hashtags'])
                    }
                },
                'visuals': visual_data['variants'],
                'metadata': {
                    'brand_info': {
                        'name': user_input.get('brand_name', ''),
                        'colors': user_input.get('brand_colors', []),
                        'style': user_input.get('style_preference', '')
                    },
                    'usage_guidelines': {
                        'optimal_posting_time': self._get_optimal_time(user_input.get('tone', '')),
                        'engagement_tips': [
                            'Pin your best comment to encourage discussion',
                            'Respond to comments within first 2 hours for better reach',
                            'Use end screens to promote related videos',
                            'Add timestamps in description for longer videos',
                            'Create compelling thumbnails that stand out',
                            'Include a strong call-to-action in your video'
                        ]
                    }
                },
                'download_url': f'/download/{pack_id}.zip',
                'zip_size': 2048576  # Mock size
            }
        }
    
    def _estimate_duration(self, script):
        words = len(script.split())
        minutes = words / 155  # Average speaking rate
        if minutes < 1:
            return f"{int(minutes * 60)} seconds"
        elif minutes < 60:
            return f"{minutes:.1f} minutes"
        else:
            hours = int(minutes // 60)
            mins = int(minutes % 60)
            return f"{hours}h {mins}m"
    
    def _get_optimal_time(self, tone):
        times = {
            'professional': '9 AM - 11 AM EST (Business hours)',
            'casual': '7 PM - 9 PM EST (Evening leisure)',
            'educational': '2 PM - 4 PM EST (Afternoon learning)',
            'entertaining': '6 PM - 8 PM EST (Prime time)'
        }
        return times.get(tone.lower(), '7 PM - 9 PM EST (General optimal)')

# Initialize mock components
content_generator = MockYouTubeContentGenerator()
visual_generator = MockVisualContentGenerator()
pack_assembler = MockSocialMediaPackAssembler()

# Store generated packs temporarily (in production, use proper database)
generated_packs = {}

@app.route('/')
def index():
    """Serve the main application interface"""
    with open('complete-ui-interface.html', 'r') as f:
        return f.read()

@app.route('/api/generate-pack', methods=['POST'])
def generate_pack():
    """Main API endpoint for generating social media packs"""
    try:
        user_input = request.json
        
        # Validate required fields
        required_fields = ['brandName', 'topic', 'tone']
        for field in required_fields:
            if not user_input.get(field):
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Normalize input data
        normalized_input = {
            'brand_name': user_input['brandName'],
            'topic': user_input['topic'],
            'tone': user_input['tone'],
            'video_length': user_input.get('videoLength', 'medium'),
            'target_audience': user_input.get('targetAudience', ''),
            'brand_colors': [
                user_input.get('primaryColor', '#667eea'),
                user_input.get('secondaryColor', '#764ba2'),
                user_input.get('accentColor', '#FF6B6B')
            ],
            'style_preference': user_input.get('stylePreference', 'modern')
        }
        
        # Step 1: Generate content with Agent 1
        content_data = content_generator.generate_content(normalized_input)
        
        # Step 2: Generate visuals with Agent 2
        visual_data = visual_generator.generate_visuals(content_data, normalized_input)
        
        # Step 3: Assemble complete pack
        pack_result = pack_assembler.create_youtube_pack(content_data, visual_data, normalized_input)
        
        if pack_result['success']:
            # Store pack for download
            pack_id = pack_result['pack']['pack_id']
            generated_packs[pack_id] = pack_result['pack']
            
            return jsonify(pack_result)
        else:
            return jsonify(pack_result), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Pack generation failed: {str(e)}'
        }), 500

@app.route('/api/pack-status/<pack_id>')
def get_pack_status(pack_id):
    """Get status of a generated pack"""
    if pack_id in generated_packs:
        return jsonify({
            'success': True,
            'pack': generated_packs[pack_id]
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Pack not found'
        }), 404

@app.route('/download/<pack_id>.zip')
def download_pack(pack_id):
    """Download complete social media pack as ZIP"""
    pack_id_clean = pack_id.replace('.zip', '')
    
    if pack_id_clean not in generated_packs:
        return jsonify({'error': 'Pack not found'}), 404
    
    pack_data = generated_packs[pack_id_clean]
    
    # Create ZIP file in memory
    zip_buffer = io.BytesIO()
    
    # In real implementation, this would use the actual pack assembler
    # For now, create a simple text file with pack info
    pack_info = f"""
YOUTUBE SOCIAL MEDIA PACK
========================

Pack ID: {pack_data['pack_id']}
Brand: {pack_data['brand_name']}
Topic: {pack_data['topic']}
Created: {pack_data['created_at']}

TITLE:
{pack_data['content']['title']['content']}

DESCRIPTION:
{pack_data['content']['description']['content']}

SCRIPT:
{pack_data['content']['script']['content']}

HASHTAGS:
{pack_data['content']['hashtags']['content']}

THUMBNAILS:
- AI Generated: {pack_data['visuals']['ai']['description']}
- Text Based: {pack_data['visuals']['text']['description']}
- Minimal: {pack_data['visuals']['minimal']['description']}

USAGE TIPS:
{chr(10).join('- ' + tip for tip in pack_data['metadata']['usage_guidelines']['engagement_tips'])}

Optimal Posting Time: {pack_data['metadata']['usage_guidelines']['optimal_posting_time']}
"""
    
    zip_buffer.write(pack_info.encode('utf-8'))
    zip_buffer.seek(0)
    
    return send_file(
        io.BytesIO(zip_buffer.getvalue()),
        mimetype='application/zip',
        as_attachment=True,
        download_name=f'{pack_id}.zip'
    )

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'components': {
            'content_generator': 'active',
            'visual_generator': 'active',
            'pack_assembler': 'active'
        }
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Ensure required files exist
    required_files = ['complete-ui-interface.html']
    for file in required_files:
        if not os.path.exists(file):
            print(f"Warning: {file} not found. Please ensure all files are in the same directory.")
    
    print("🚀 YouTube Content Creator API starting...")
    print("📱 Frontend available at: http://localhost:5000")
    print("🔗 API endpoints:")
    print("   POST /api/generate-pack - Generate social media pack")
    print("   GET  /api/pack-status/<id> - Get pack status")
    print("   GET  /download/<id>.zip - Download pack")
    print("   GET  /api/health - Health check")
    
    app.run(debug=True, host='0.0.0.0', port=5000)