"""
Main Application - Day 3 Implementation
Complete Flask web application integrating all components
"""

from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import json
import base64
import io
import os
from datetime import datetime

# Import our agents and assembler
from agent1_youtube_generator import YouTubeContentAgent
from agent2_visual_generator import VisualContentAgent
from agent_orchestrator import AgentOrchestrator
from social_pack_assembler import SocialPackAssembler

app = Flask(__name__)
CORS(app)

# Initialize components
orchestrator = AgentOrchestrator()
pack_assembler = SocialPackAssembler()

# Store for active packs (in production, use database)
active_packs = {}

@app.route('/')
def index():
    """Serve the main intake form"""
    return render_template('index.html')

@app.route('/api/generate-content', methods=['POST'])
def generate_content():
    """
    Main endpoint for content generation workflow
    Handles: User Input → Agent 1 → Agent 2 → Pack Assembly
    """
    try:
        # Get user input from form
        user_input = request.json
        
        # Validate required fields
        required_fields = ['brand_name', 'topic', 'tone']
        for field in required_fields:
            if not user_input.get(field):
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Step 1: Generate content with Agent 1
        print("🚀 Starting content generation workflow...")
        content_result = orchestrator.generate_content(user_input)
        
        if not content_result['success']:
            return jsonify({
                'success': False,
                'error': f'Content generation failed: {content_result["error"]}'
            }), 500
        
        # Step 2: Generate visuals with Agent 2
        print("🎨 Generating visuals...")
        visual_result = orchestrator.generate_visuals(
            content_result['content_data'], 
            user_input
        )
        
        if not visual_result['success']:
            return jsonify({
                'success': False,
                'error': f'Visual generation failed: {visual_result["error"]}'
            }), 500
        
        # Step 3: Assemble social media pack
        print("📦 Assembling social media pack...")
        pack_result = pack_assembler.create_youtube_pack(
            content_result['content_data'],
            visual_result['visual_data'],
            user_input
        )
        
        if not pack_result['success']:
            return jsonify({
                'success': False,
                'error': f'Pack assembly failed: {pack_result["error"]}'
            }), 500
        
        # Store pack for download
        pack_id = pack_result['pack_data']['pack_id']
        active_packs[pack_id] = pack_result['pack_data']
        
        # Return complete pack data
        return jsonify({
            'success': True,
            'pack_id': pack_id,
            'pack_data': pack_result['pack_data'],
            'message': 'Complete YouTube social media pack generated successfully!'
        })
        
    except Exception as e:
        print(f"❌ Error in content generation: {e}")
        return jsonify({
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }), 500

@app.route('/api/pack/<pack_id>')
def get_pack(pack_id):
    """Get pack data by ID"""
    if pack_id not in active_packs:
        return jsonify({
            'success': False,
            'error': 'Pack not found'
        }), 404
    
    return jsonify({
        'success': True,
        'pack_data': active_packs[pack_id]
    })

@app.route('/api/download/<pack_id>')
def download_pack(pack_id):
    """Download pack as ZIP file"""
    if pack_id not in active_packs:
        return jsonify({
            'success': False,
            'error': 'Pack not found'
        }), 404
    
    try:
        pack_data = active_packs[pack_id]
        zip_base64 = pack_data.get('download_bundle', '')
        
        if not zip_base64:
            return jsonify({
                'success': False,
                'error': 'Download bundle not available'
            }), 500
        
        # Decode base64 ZIP data
        zip_data = base64.b64decode(zip_base64)
        zip_buffer = io.BytesIO(zip_data)
        
        return send_file(
            zip_buffer,
            as_attachment=True,
            download_name=f'{pack_id}.zip',
            mimetype='application/zip'
        )
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Download failed: {str(e)}'
        }), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'active_packs': len(active_packs)
    })

@app.route('/pack/<pack_id>')
def view_pack(pack_id):
    """View pack in browser"""
    if pack_id not in active_packs:
        return "Pack not found", 404
    
    return render_template('pack_viewer.html', pack_id=pack_id)

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    print("🚀 Starting Content Generation Platform...")
    print("📝 Intake Form: http://localhost:5000")
    print("🏥 Health Check: http://localhost:5000/api/health")
    print("📚 API Documentation:")
    print("  POST /api/generate-content - Generate complete social media pack")
    print("  GET  /api/pack/<pack_id> - Get pack data")
    print("  GET  /api/download/<pack_id> - Download pack as ZIP")
    print("  GET  /pack/<pack_id> - View pack in browser")
    
    app.run(debug=True, host='0.0.0.0', port=5000)