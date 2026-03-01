import json
import redis
import os
import uuid
from datetime import datetime
from typing import Dict, Optional
import asyncio
import threading
from agent1_youtube_generator import Agent1YouTubeGenerator
from agent2_visual_generator import Agent2VisualGenerator

class AgentOrchestrator:
    def __init__(self, openai_api_key: str, redis_host: str = 'localhost', redis_port: int = 6379):
        self.redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
        self.agent1 = Agent1YouTubeGenerator(openai_api_key)
        self.agent2 = Agent2VisualGenerator(openai_api_key, redis_host, redis_port)
        
    def create_job(self, form_data: Dict) -> str:
        """
        Create a new job and initiate the agent workflow
        """
        job_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        # Store initial job data
        job_data = {
            'job_id': job_id,
            'status': 'initiated',
            'timestamp': timestamp,
            'form_data': form_data,
            'workflow_stage': 'agent1_processing'
        }
        
        # Store in Redis with 1 hour expiry
        self.redis_client.setex(
            f"job:{job_id}",
            3600,
            json.dumps(job_data)
        )
        
        # Start workflow in background thread
        threading.Thread(
            target=self._execute_workflow,
            args=(job_id, form_data),
            daemon=True
        ).start()
        
        return job_id
    
    def _execute_workflow(self, job_id: str, form_data: Dict):
        """
        Execute the complete Agent 1 → Agent 2 workflow
        """
        try:
            # Update job status
            self._update_job_status(job_id, 'agent1_processing', 'Agent 1 generating content...')
            
            # Step 1: Agent 1 generates content
            agent1_result = self.agent1.generate_content(form_data)
            
            if agent1_result['status'] != 'success':
                self._update_job_status(job_id, 'failed', f"Agent 1 failed: {agent1_result.get('error')}")
                return
            
            # Store Agent 1 output for Agent 2
            agent1_output = agent1_result['content']
            agent1_output.update({
                'brand_colors': form_data.get('brand_colors', ['#FF0000', '#FFFFFF']),
                'style_preference': form_data.get('style_preference', 'modern'),
                'timestamp': datetime.utcnow().isoformat()
            })
            
            self.redis_client.setex(
                f"agent1_output:{job_id}",
                3600,
                json.dumps(agent1_output)
            )
            
            # Update job status
            self._update_job_status(job_id, 'agent2_processing', 'Agent 2 generating visuals...')
            
            # Step 2: Agent 2 generates visuals
            agent2_result = self.agent2.process_agent1_output(job_id)
            
            if agent2_result['status'] != 'success':
                self._update_job_status(job_id, 'failed', f"Agent 2 failed: {agent2_result.get('error')}")
                return
            
            # Step 3: Package final result
            final_package = self._create_social_media_pack(
                agent1_output,
                agent2_result['visual_result']
            )
            
            # Store final package
            self.redis_client.setex(
                f"final_package:{job_id}",
                3600,
                json.dumps(final_package)
            )
            
            # Update job status to completed
            self._update_job_status(job_id, 'completed', 'Social media pack ready!')
            
        except Exception as e:
            self._update_job_status(job_id, 'failed', f"Workflow error: {str(e)}")
    
    def _update_job_status(self, job_id: str, status: str, message: str = ''):
        """Update job status in Redis"""
        try:
            job_data = self.redis_client.get(f"job:{job_id}")
            if job_data:
                job_info = json.loads(job_data)
                job_info.update({
                    'status': status,
                    'message': message,
                    'last_updated': datetime.utcnow().isoformat()
                })
                
                self.redis_client.setex(
                    f"job:{job_id}",
                    3600,
                    json.dumps(job_info)
                )
        except Exception as e:
            print(f"Error updating job status: {e}")
    
    def _create_social_media_pack(self, content: Dict, visuals: Dict) -> Dict:
        """
        Package content and visuals into a complete social media pack
        """
        return {
            'pack_type': 'youtube_content_pack',
            'content': {
                'title': content.get('title'),
                'description': content.get('description'),
                'script': content.get('script'),
                'hashtags': content.get('hashtags'),
                'seo_tags': content.get('seo_tags')
            },
            'visuals': {
                'thumbnail_variants': visuals.get('variants', []),
                'brand_colors': visuals.get('metadata', {}).get('brand_colors'),
                'style_preference': visuals.get('metadata', {}).get('style_preference')
            },
            'metadata': {
                'generated_at': datetime.utcnow().isoformat(),
                'content_length': content.get('estimated_duration'),
                'optimization_tips': content.get('optimization_tips', []),
                'visual_variants_count': len(visuals.get('variants', []))
            },
            'usage_instructions': {
                'title': 'Use as YouTube video title (60 chars max)',
                'description': 'Copy to YouTube description with hashtags',
                'script': 'Use as video script or talking points',
                'thumbnails': 'Choose preferred thumbnail variant for upload'
            }
        }
    
    def get_job_status(self, job_id: str) -> Dict:
        """Get current job status"""
        try:
            job_data = self.redis_client.get(f"job:{job_id}")
            if not job_data:
                return {'status': 'not_found', 'error': 'Job not found'}
            
            return json.loads(job_data)
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def get_final_package(self, job_id: str) -> Optional[Dict]:
        """Retrieve the final social media pack"""
        try:
            package_data = self.redis_client.get(f"final_package:{job_id}")
            if not package_data:
                return None
            
            return json.loads(package_data)
        except Exception as e:
            print(f"Error retrieving package: {e}")
            return None
    
    def cleanup_job(self, job_id: str):
        """Clean up job data from Redis"""
        keys_to_delete = [
            f"job:{job_id}",
            f"agent1_output:{job_id}",
            f"agent2_output:agent2_{job_id}",
            f"final_package:{job_id}",
            f"job_status:agent2_{job_id}"
        ]
        
        for key in keys_to_delete:
            self.redis_client.delete(key)

# Flask API endpoints for the orchestrator
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Initialize orchestrator (you'll need to set your OpenAI API key)
orchestrator = AgentOrchestrator(openai_api_key=os.environ.get('OPENAI_API_KEY', ''))

@app.route('/api/generate-content', methods=['POST'])
def generate_content():
    """API endpoint to start content generation workflow"""
    try:
        form_data = request.json
        
        # Validate required fields
        required_fields = ['brand_name', 'topic', 'tone']
        for field in required_fields:
            if field not in form_data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create job and start workflow
        job_id = orchestrator.create_job(form_data)
        
        return jsonify({
            'status': 'success',
            'job_id': job_id,
            'message': 'Content generation started'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/job-status/<job_id>', methods=['GET'])
def get_job_status(job_id):
    """Get job status"""
    status = orchestrator.get_job_status(job_id)
    return jsonify(status)

@app.route('/api/download-pack/<job_id>', methods=['GET'])
def download_pack(job_id):
    """Download the final social media pack"""
    package = orchestrator.get_final_package(job_id)
    
    if not package:
        return jsonify({'error': 'Package not found or not ready'}), 404
    
    return jsonify({
        'status': 'success',
        'package': package
    })

@app.route('/api/cleanup/<job_id>', methods=['DELETE'])
def cleanup_job(job_id):
    """Clean up job data"""
    orchestrator.cleanup_job(job_id)
    return jsonify({'status': 'success', 'message': 'Job cleaned up'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)