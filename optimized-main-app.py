#!/usr/bin/env python3
"""
Day 4: Optimized Main Application
Enhanced version with performance optimizations and comprehensive testing
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import json
import uuid
import os
import time
from datetime import datetime
import logging
from typing import Dict, Any

# Import our optimization modules
from workflow_optimizer import optimizer, performance_monitor, optimize_workflow
from agent1_youtube_generator import YouTubeContentGenerator
from agent2_visual_generator import VisualContentGenerator
from social_pack_assembler import SocialMediaPackAssembler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Initialize components
content_generator = YouTubeContentGenerator()
visual_generator = VisualContentGenerator()
pack_assembler = SocialMediaPackAssembler()

# Storage for packs (in production, use proper database)
packs_storage = {}

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/metrics', methods=['GET'])
def get_metrics():
    """Get performance metrics"""
    app_metrics = performance_monitor.get_metrics()
    cache_metrics = optimizer.get_performance_metrics()
    
    return jsonify({
        'performance': app_metrics,
        'cache': cache_metrics,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/cache/clear', methods=['POST'])
def clear_cache():
    """Clear application cache"""
    try:
        optimizer.clear_cache()
        performance_monitor.reset_metrics()
        return jsonify({
            'status': 'success',
            'message': 'Cache cleared successfully'
        })
    except Exception as e:
        logger.error(f"Cache clear error: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/cache/warmup', methods=['POST'])
def warmup_cache():
    """Warmup cache with common requests"""
    try:
        common_requests = [
            {
                'brand_name': 'TechCorp',
                'topic': 'AI Technology',
                'tone': 'professional',
                'video_length': 'short',
                'brand_colors': '#0066CC',
                'style_preference': 'modern'
            },
            {
                'brand_name': 'CreativeStudio',
                'topic': 'Design Tips',
                'tone': 'fun',
                'video_length': 'medium',
                'brand_colors': '#FF6B6B',
                'style_preference': 'creative'
            },
            {
                'brand_name': 'FitnessGuru',
                'topic': 'Health & Wellness',
                'tone': 'inspirational',
                'video_length': 'long',
                'brand_colors': '#4ECDC4',
                'style_preference': 'energetic'
            }
        ]
        
        optimizer.warmup_cache(common_requests)
        
        return jsonify({
            'status': 'success',
            'message': f'Cache warmed up with {len(common_requests)} common requests'
        })
    except Exception as e:
        logger.error(f"Cache warmup error: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/generate', methods=['POST'])
@optimize_workflow
def generate_content():
    """Generate complete social media pack with optimization"""
    start_time = time.time()
    
    try:
        # Validate input
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        required_fields = ['brand_name', 'topic', 'tone']
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            return jsonify({
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
        
        logger.info(f"Processing request for brand: {data.get('brand_name')}")
        
        # Generate unique pack ID
        pack_id = str(uuid.uuid4())
        
        # Check for optimized/cached content first
        cache_key = optimizer.generate_cache_key(data)
        cached_result = optimizer.get_cached_result(cache_key)
        
        if cached_result:
            # Use cached result but update pack_id and timestamp
            cached_result['pack_id'] = pack_id
            cached_result['metadata']['created_at'] = datetime.now().isoformat()
            cached_result['metadata']['from_cache'] = True
            
            packs_storage[pack_id] = cached_result
            
            processing_time = time.time() - start_time
            logger.info(f"✅ Served cached content in {processing_time:.2f}s")
            
            return jsonify(cached_result)
        
        # Generate new content
        logger.info("Generating new content...")
        
        # Step 1: Generate content with Agent 1
        content_result = content_generator.generate_content(
            brand_name=data['brand_name'],
            topic=data['topic'],
            tone=data['tone'],
            video_length=data.get('video_length', 'medium')
        )
        
        if not content_result.get('success'):
            return jsonify({
                'error': 'Content generation failed',
                'details': content_result.get('error')
            }), 500
        
        # Step 2: Generate visuals with Agent 2
        visual_result = visual_generator.generate_visuals(
            content_data=content_result['content'],
            brand_colors=data.get('brand_colors', '#0066CC'),
            style_preference=data.get('style_preference', 'modern')
        )
        
        if not visual_result.get('success'):
            logger.warning("Visual generation failed, continuing with content only")
            visual_result = {
                'success': True,
                'visuals': [{
                    'type': 'placeholder',
                    'url': '/static/placeholder.png',
                    'description': 'Placeholder thumbnail'
                }]
            }
        
        # Step 3: Assemble complete pack
        pack_result = pack_assembler.create_pack(
            pack_id=pack_id,
            content=content_result['content'],
            visuals=visual_result['visuals'],
            metadata={
                'brand_name': data['brand_name'],
                'topic': data['topic'],
                'tone': data['tone'],
                'video_length': data.get('video_length', 'medium'),
                'brand_colors': data.get('brand_colors'),
                'style_preference': data.get('style_preference'),
                'created_at': datetime.now().isoformat(),
                'from_cache': False
            }
        )
        
        if not pack_result.get('success'):
            return jsonify({
                'error': 'Pack assembly failed',
                'details': pack_result.get('error')
            }), 500
        
        # Store the pack
        final_pack = pack_result['pack']
        packs_storage[pack_id] = final_pack
        
        # Cache the result for future use
        optimizer.cache_result(cache_key, final_pack)
        
        processing_time = time.time() - start_time
        logger.info(f"✅ Generated new content pack in {processing_time:.2f}s")
        
        # Add performance metadata
        final_pack['_performance'] = {
            'processing_time': processing_time,
            'cached': False,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(final_pack)
    
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"Content generation error: {e}")
        
        return jsonify({
            'error': 'Internal server error',
            'details': str(e),
            'processing_time': processing_time
        }), 500

@app.route('/pack/<pack_id>', methods=['GET'])
def get_pack(pack_id):
    """Get specific pack by ID"""
    try:
        if pack_id not in packs_storage:
            return jsonify({'error': 'Pack not found'}), 404
        
        pack = packs_storage[pack_id]
        
        # Add real-time metrics
        pack['_metrics'] = {
            'views': pack.get('_views', 0) + 1,
            'last_accessed': datetime.now().isoformat()
        }
        
        # Update view count
        packs_storage[pack_id]['_views'] = pack['_metrics']['views']
        
        return jsonify(pack)
    
    except Exception as e:
        logger.error(f"Pack retrieval error: {e}")
        return jsonify({
            'error': 'Failed to retrieve pack',
            'details': str(e)
        }), 500

@app.route('/download/<pack_id>', methods=['GET'])
def download_pack(pack_id):
    """Download pack as ZIP file"""
    try:
        if pack_id not in packs_storage:
            return jsonify({'error': 'Pack not found'}), 404
        
        pack = packs_storage[pack_id]
        
        # Create ZIP file
        zip_path = pack_assembler.create_download_zip(pack)
        
        if not zip_path or not os.path.exists(zip_path):
            return jsonify({'error': 'Failed to create download file'}), 500
        
        # Update download count
        pack['_downloads'] = pack.get('_downloads', 0) + 1
        packs_storage[pack_id] = pack
        
        return send_file(
            zip_path,
            as_attachment=True,
            download_name=f"{pack['metadata']['brand_name']}_content_pack.zip",
            mimetype='application/zip'
        )
    
    except Exception as e:
        logger.error(f"Download error: {e}")
        return jsonify({
            'error': 'Download failed',
            'details': str(e)
        }), 500

@app.route('/packs', methods=['GET'])
def list_packs():
    """List all generated packs"""
    try:
        pack_list = []
        for pack_id, pack in packs_storage.items():
            pack_summary = {
                'pack_id': pack_id,
                'brand_name': pack['metadata']['brand_name'],
                'topic': pack['metadata']['topic'],
                'created_at': pack['metadata']['created_at'],
                'views': pack.get('_views', 0),
                'downloads': pack.get('_downloads', 0),
                'from_cache': pack['metadata'].get('from_cache', False)
            }
            pack_list.append(pack_summary)
        
        # Sort by creation date (newest first)
        pack_list.sort(key=lambda x: x['created_at'], reverse=True)
        
        return jsonify({
            'packs': pack_list,
            'total': len(pack_list),
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Pack listing error: {e}")
        return jsonify({
            'error': 'Failed to list packs',
            'details': str(e)
        }), 500

@app.route('/test/load', methods=['POST'])
def load_test():
    """Simple load testing endpoint"""
    try:
        data = request.get_json() or {}
        num_requests = min(data.get('requests', 5), 20)  # Max 20 for safety
        
        results = []
        start_time = time.time()
        
        test_data = {
            'brand_name': 'LoadTest',
            'topic': 'Performance Testing',
            'tone': 'professional',
            'video_length': 'short'
        }
        
        for i in range(num_requests):
            request_start = time.time()
            
            # Simulate content generation
            pack_id = str(uuid.uuid4())
            test_pack = {
                'pack_id': pack_id,
                'content': {
                    'title': f'Load Test Content {i+1}',
                    'description': 'Generated during load testing',
                    'hashtags': ['#loadtest', '#performance']
                },
                'metadata': {
                    **test_data,
                    'created_at': datetime.now().isoformat(),
                    'test_request': True
                }
            }
            
            packs_storage[pack_id] = test_pack
            
            request_time = time.time() - request_start
            results.append({
                'request': i + 1,
                'pack_id': pack_id,
                'processing_time': request_time
            })
        
        total_time = time.time() - start_time
        avg_time = total_time / num_requests
        
        return jsonify({
            'load_test_results': {
                'total_requests': num_requests,
                'total_time': total_time,
                'average_time': avg_time,
                'requests_per_second': num_requests / total_time,
                'results': results
            }
        })
    
    except Exception as e:
        logger.error(f"Load test error: {e}")
        return jsonify({
            'error': 'Load test failed',
            'details': str(e)
        }), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Endpoint not found',
        'available_endpoints': [
            '/health',
            '/metrics',
            '/generate',
            '/pack/<pack_id>',
            '/download/<pack_id>',
            '/packs',
            '/cache/clear',
            '/cache/warmup',
            '/test/load'
        ]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return jsonify({
        'error': 'Internal server error',
        'message': 'Please try again later'
    }), 500

if __name__ == '__main__':
    logger.info("🚀 Starting Optimized Content Generation Platform")
    logger.info("Available endpoints:")
    logger.info("  GET  /health - Health check")
    logger.info("  GET  /metrics - Performance metrics")
    logger.info("  POST /generate - Generate content pack")
    logger.info("  GET  /pack/<id> - Get specific pack")
    logger.info("  GET  /download/<id> - Download pack")
    logger.info("  GET  /packs - List all packs")
    logger.info("  POST /cache/clear - Clear cache")
    logger.info("  POST /cache/warmup - Warmup cache")
    logger.info("  POST /test/load - Load testing")
    
    # Warmup cache on startup
    try:
        logger.info("🔥 Warming up cache...")
        common_requests = [
            {
                'brand_name': 'StartupTech',
                'topic': 'Innovation',
                'tone': 'professional',
                'video_length': 'short'
            }
        ]
        optimizer.warmup_cache(common_requests)
        logger.info("✅ Cache warmup completed")
    except Exception as e:
        logger.warning(f"Cache warmup failed: {e}")
    
    app.run(debug=True, host='0.0.0.0', port=5000)