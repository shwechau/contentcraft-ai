import openai
import json
import redis
import os
from datetime import datetime
from typing import Dict, List
import hashlib

class YouTubeContentAgent:
    def __init__(self, openai_api_key: str, redis_host: str = 'localhost', redis_port: int = 6379):
        self.openai_client = openai.OpenAI(api_key=openai_api_key)
        self.redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
        
    def generate_content(self, form_data: Dict) -> Dict:
        """
        Generate YouTube content based on form input
        """
        try:
            # Extract form data
            brand_name = form_data.get('brandName', '')
            topic = form_data.get('topic', '')
            tone = form_data.get('tone', 'professional')
            video_length = form_data.get('videoLength', 'medium')
            target_audience = form_data.get('targetAudience', 'general audience')
            additional_notes = form_data.get('additionalNotes', '')
            
            # Generate content using OpenAI
            content_result = self._generate_youtube_content(
                brand_name, topic, tone, video_length, target_audience, additional_notes
            )
            
            # Generate hashtags
            hashtags = self._generate_hashtags(topic, tone, brand_name)
            
            # Create job ID for tracking
            job_id = self._create_job_id(form_data)
            
            # Prepare metadata for Agent 2
            metadata = {
                'brand_name': brand_name,
                'topic': topic,
                'tone': tone,
                'brand_colors': form_data.get('brandColors', '#667eea'),
                'style_preference': form_data.get('stylePreference', 'modern'),
                'video_length': video_length
            }
            
            # Package result
            result = {
                'job_id': job_id,
                'content': content_result,
                'hashtags': hashtags,
                'metadata': metadata,
                'timestamp': datetime.now().isoformat(),
                'status': 'content_generated'
            }
            
            # Store in Redis for Agent 2
            self.redis_client.setex(f"job:{job_id}", 3600, json.dumps(result))
            
            # Trigger Agent 2 (in production, this would be a message queue)
            self._notify_agent2(job_id, result)
            
            return result
            
        except Exception as e:
            return {
                'error': str(e),
                'status': 'failed',
                'timestamp': datetime.now().isoformat()
            }
    
    def _generate_youtube_content(self, brand_name: str, topic: str, tone: str, 
                                video_length: str, target_audience: str, notes: str) -> Dict:
        """
        Generate YouTube-specific content using OpenAI
        """
        
        # Determine content length based on video length
        length_specs = {
            'short': 'Keep script concise for 1-3 minute video. Focus on one key point.',
            'medium': 'Create detailed script for 5-10 minute video with 3-4 main points.',
            'long': 'Develop comprehensive script for 15+ minute video with detailed sections.'
        }
        
        prompt = f"""
        Create YouTube content for {brand_name} with the following specifications:
        
        Topic: {topic}
        Tone: {tone}
        Video Length: {video_length}
        Target Audience: {target_audience}
        Additional Notes: {notes}
        
        {length_specs.get(video_length, length_specs['medium'])}
        
        Generate the following in JSON format:
        1. title: Compelling YouTube title (60 characters max)
        2. description: SEO-optimized description (150-200 words)
        3. script: Video script with timestamps
        4. thumbnail_text: Text for thumbnail overlay
        5. key_points: Array of main talking points
        6. call_to_action: Specific CTA for the video
        
        Make sure the tone is {tone} and appeals to {target_audience}.
        """
        
        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a YouTube content creation expert. Generate engaging, SEO-optimized content that drives engagement."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        try:
            content = json.loads(response.choices[0].message.content)
            return content
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return {
                'title': f"{topic} - {brand_name}",
                'description': response.choices[0].message.content[:200],
                'script': response.choices[0].message.content,
                'thumbnail_text': topic.upper(),
                'key_points': [topic],
                'call_to_action': 'Like and subscribe for more content!'
            }
    
    def _generate_hashtags(self, topic: str, tone: str, brand_name: str) -> List[str]:
        """
        Generate relevant YouTube hashtags
        """
        
        # Static trending hashtags database (in production, use YouTube API)
        trending_hashtags = {
            'general': ['#YouTube', '#Content', '#Tutorial', '#Tips', '#Guide'],
            'professional': ['#Business', '#Professional', '#Career', '#Success', '#Growth'],
            'fun': ['#Fun', '#Entertainment', '#Viral', '#Trending', '#Comedy'],
            'inspirational': ['#Motivation', '#Inspiration', '#Success', '#Goals', '#Mindset'],
            'educational': ['#Education', '#Learning', '#Tutorial', '#HowTo', '#Knowledge'],
            'entertaining': ['#Entertainment', '#Fun', '#Viral', '#Comedy', '#Trending']
        }
        
        # Get base hashtags for tone
        base_hashtags = trending_hashtags.get(tone, trending_hashtags['general'])
        
        # Add topic-specific hashtags
        topic_words = topic.lower().split()
        topic_hashtags = [f"#{word.capitalize()}" for word in topic_words if len(word) > 3]
        
        # Add brand hashtag
        brand_hashtag = f"#{brand_name.replace(' ', '')}"
        
        # Combine and limit to 10 hashtags
        all_hashtags = base_hashtags + topic_hashtags + [brand_hashtag]
        return list(set(all_hashtags))[:10]
    
    def _create_job_id(self, form_data: Dict) -> str:
        """
        Create unique job ID for tracking
        """
        data_string = json.dumps(form_data, sort_keys=True)
        timestamp = str(datetime.now().timestamp())
        return hashlib.md5((data_string + timestamp).encode()).hexdigest()[:12]
    
    def _notify_agent2(self, job_id: str, content_data: Dict):
        """
        Notify Agent 2 to start visual generation
        """
        # In production, this would publish to a message queue
        # For now, we'll use Redis pub/sub
        message = {
            'job_id': job_id,
            'action': 'generate_visuals',
            'content_data': content_data
        }
        
        self.redis_client.publish('agent2_queue', json.dumps(message))
        print(f"Notified Agent 2 for job: {job_id}")

# Example usage and API endpoint
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Initialize Agent 1
agent1 = YouTubeContentAgent(openai_api_key=os.environ.get('OPENAI_API_KEY', ''))

@app.route('/api/generate-content', methods=['POST'])
def generate_content():
    try:
        form_data = request.json
        result = agent1.generate_content(form_data)
        
        if 'error' in result:
            return jsonify(result), 500
        
        return jsonify({
            'jobId': result['job_id'],
            'status': 'processing',
            'message': 'Content generation started'
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'failed'
        }), 500

@app.route('/api/status/<job_id>', methods=['GET'])
def get_status(job_id):
    try:
        job_data = agent1.redis_client.get(f"job:{job_id}")
        if job_data:
            return jsonify(json.loads(job_data))
        else:
            return jsonify({'error': 'Job not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)