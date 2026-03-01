#!/usr/bin/env python3
"""
Day 4: Workflow Optimization Module
Performance improvements and optimization for the content generation platform
"""

import time
import hashlib
import json
import redis
from functools import wraps
from typing import Dict, Any, Optional
import logging
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WorkflowOptimizer:
    """Optimization layer for the content generation workflow"""
    
    def __init__(self, redis_host='localhost', redis_port=6379, redis_db=0):
        """Initialize optimizer with Redis caching"""
        try:
            self.redis_client = redis.Redis(
                host=redis_host, 
                port=redis_port, 
                db=redis_db,
                decode_responses=True
            )
            self.redis_client.ping()
            logger.info("✅ Redis connection established")
        except redis.ConnectionError:
            logger.warning("⚠️  Redis not available, using in-memory cache")
            self.redis_client = None
            self._memory_cache = {}
    
    def generate_cache_key(self, data: Dict[str, Any]) -> str:
        """Generate consistent cache key from input data"""
        # Sort keys for consistent hashing
        sorted_data = json.dumps(data, sort_keys=True)
        return hashlib.md5(sorted_data.encode()).hexdigest()
    
    def get_cached_result(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached result"""
        try:
            if self.redis_client:
                cached = self.redis_client.get(f"content:{cache_key}")
                if cached:
                    logger.info(f"✅ Cache hit for key: {cache_key[:8]}...")
                    return json.loads(cached)
            else:
                # In-memory fallback
                if cache_key in self._memory_cache:
                    cached_data, timestamp = self._memory_cache[cache_key]
                    # Check if cache is still valid (1 hour)
                    if datetime.now() - timestamp < timedelta(hours=1):
                        logger.info(f"✅ Memory cache hit for key: {cache_key[:8]}...")
                        return cached_data
                    else:
                        del self._memory_cache[cache_key]
        except Exception as e:
            logger.error(f"Cache retrieval error: {e}")
        
        return None
    
    def cache_result(self, cache_key: str, result: Dict[str, Any], ttl: int = 3600):
        """Cache result with TTL"""
        try:
            if self.redis_client:
                self.redis_client.setex(
                    f"content:{cache_key}", 
                    ttl, 
                    json.dumps(result)
                )
                logger.info(f"✅ Result cached for key: {cache_key[:8]}...")
            else:
                # In-memory fallback
                self._memory_cache[cache_key] = (result, datetime.now())
                logger.info(f"✅ Result cached in memory for key: {cache_key[:8]}...")
        except Exception as e:
            logger.error(f"Cache storage error: {e}")
    
    def cache_decorator(self, ttl: int = 3600):
        """Decorator for caching function results"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Generate cache key from function arguments
                cache_data = {
                    'func': func.__name__,
                    'args': args,
                    'kwargs': kwargs
                }
                cache_key = self.generate_cache_key(cache_data)
                
                # Try to get cached result
                cached_result = self.get_cached_result(cache_key)
                if cached_result:
                    return cached_result
                
                # Execute function and cache result
                start_time = time.time()
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                # Add performance metadata
                if isinstance(result, dict):
                    result['_performance'] = {
                        'execution_time': execution_time,
                        'cached': False,
                        'timestamp': datetime.now().isoformat()
                    }
                
                # Cache the result
                self.cache_result(cache_key, result, ttl)
                
                logger.info(f"✅ Function {func.__name__} executed in {execution_time:.2f}s")
                return result
            
            return wrapper
        return decorator
    
    def optimize_content_generation(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize content generation with intelligent caching"""
        cache_key = self.generate_cache_key(content_data)
        
        # Check for similar content (fuzzy matching)
        similar_content = self.find_similar_content(content_data)
        if similar_content:
            logger.info("✅ Using optimized similar content")
            return self.adapt_similar_content(similar_content, content_data)
        
        return None
    
    def find_similar_content(self, content_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find similar cached content for optimization"""
        try:
            if not self.redis_client:
                return None
            
            # Get all content keys
            keys = self.redis_client.keys("content:*")
            
            for key in keys:
                cached_data = self.redis_client.get(key)
                if cached_data:
                    cached_content = json.loads(cached_data)
                    
                    # Simple similarity check (can be enhanced with ML)
                    if self.is_similar_content(content_data, cached_content):
                        return cached_content
        
        except Exception as e:
            logger.error(f"Similar content search error: {e}")
        
        return None
    
    def is_similar_content(self, new_data: Dict[str, Any], cached_data: Dict[str, Any]) -> bool:
        """Check if content is similar enough for optimization"""
        # Simple similarity metrics
        similarity_score = 0
        
        # Brand name match
        if new_data.get('brand_name') == cached_data.get('metadata', {}).get('brand_name'):
            similarity_score += 0.3
        
        # Topic similarity (basic keyword matching)
        new_topic = new_data.get('topic', '').lower()
        cached_topic = cached_data.get('metadata', {}).get('topic', '').lower()
        
        if new_topic and cached_topic:
            common_words = set(new_topic.split()) & set(cached_topic.split())
            if len(common_words) > 0:
                similarity_score += 0.4
        
        # Tone match
        if new_data.get('tone') == cached_data.get('metadata', {}).get('tone'):
            similarity_score += 0.3
        
        return similarity_score >= 0.7
    
    def adapt_similar_content(self, similar_content: Dict[str, Any], new_data: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt similar content to new requirements"""
        adapted_content = similar_content.copy()
        
        # Update metadata
        adapted_content['metadata'].update({
            'brand_name': new_data.get('brand_name'),
            'topic': new_data.get('topic'),
            'adapted_from_cache': True,
            'adaptation_time': datetime.now().isoformat()
        })
        
        # Basic content adaptation (can be enhanced with AI)
        if 'content' in adapted_content:
            content = adapted_content['content']
            
            # Replace brand name in title and description
            old_brand = similar_content.get('metadata', {}).get('brand_name', '')
            new_brand = new_data.get('brand_name', '')
            
            if old_brand and new_brand:
                content['title'] = content['title'].replace(old_brand, new_brand)
                content['description'] = content['description'].replace(old_brand, new_brand)
        
        return adapted_content
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for the system"""
        try:
            if self.redis_client:
                # Redis-based metrics
                cache_keys = self.redis_client.keys("content:*")
                cache_size = len(cache_keys)
                
                # Calculate hit rate (simplified)
                hit_count = self.redis_client.get("cache:hits") or 0
                miss_count = self.redis_client.get("cache:misses") or 0
                total_requests = int(hit_count) + int(miss_count)
                hit_rate = (int(hit_count) / total_requests * 100) if total_requests > 0 else 0
                
                return {
                    'cache_size': cache_size,
                    'hit_rate': f"{hit_rate:.1f}%",
                    'total_requests': total_requests,
                    'cache_type': 'Redis'
                }
            else:
                # Memory cache metrics
                return {
                    'cache_size': len(self._memory_cache),
                    'cache_type': 'Memory',
                    'hit_rate': 'N/A'
                }
        
        except Exception as e:
            logger.error(f"Metrics error: {e}")
            return {'error': str(e)}
    
    def clear_cache(self):
        """Clear all cached content"""
        try:
            if self.redis_client:
                keys = self.redis_client.keys("content:*")
                if keys:
                    self.redis_client.delete(*keys)
                logger.info(f"✅ Cleared {len(keys)} cached items from Redis")
            else:
                self._memory_cache.clear()
                logger.info("✅ Cleared memory cache")
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
    
    def warmup_cache(self, common_requests: list):
        """Pre-populate cache with common requests"""
        logger.info("🔥 Starting cache warmup...")
        
        for request_data in common_requests:
            cache_key = self.generate_cache_key(request_data)
            
            # Check if already cached
            if not self.get_cached_result(cache_key):
                # This would typically call the actual content generation
                # For warmup, we create placeholder data
                placeholder_result = {
                    'pack_id': f"warmup_{cache_key[:8]}",
                    'content': {
                        'title': f"Sample content for {request_data.get('topic', 'general')}",
                        'description': f"Generated for {request_data.get('brand_name', 'brand')}",
                        'hashtags': ['#sample', '#warmup']
                    },
                    'metadata': request_data,
                    'warmed_up': True
                }
                
                self.cache_result(cache_key, placeholder_result)
        
        logger.info(f"✅ Cache warmup completed for {len(common_requests)} requests")


class PerformanceMonitor:
    """Monitor and log performance metrics"""
    
    def __init__(self):
        self.metrics = {
            'requests_processed': 0,
            'total_processing_time': 0,
            'average_processing_time': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'errors': 0
        }
    
    def record_request(self, processing_time: float, cache_hit: bool = False, error: bool = False):
        """Record request metrics"""
        self.metrics['requests_processed'] += 1
        self.metrics['total_processing_time'] += processing_time
        self.metrics['average_processing_time'] = (
            self.metrics['total_processing_time'] / self.metrics['requests_processed']
        )
        
        if cache_hit:
            self.metrics['cache_hits'] += 1
        else:
            self.metrics['cache_misses'] += 1
        
        if error:
            self.metrics['errors'] += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        total_cache_requests = self.metrics['cache_hits'] + self.metrics['cache_misses']
        cache_hit_rate = (
            (self.metrics['cache_hits'] / total_cache_requests * 100) 
            if total_cache_requests > 0 else 0
        )
        
        return {
            **self.metrics,
            'cache_hit_rate': f"{cache_hit_rate:.1f}%",
            'error_rate': f"{(self.metrics['errors'] / max(self.metrics['requests_processed'], 1) * 100):.1f}%"
        }
    
    def reset_metrics(self):
        """Reset all metrics"""
        self.metrics = {
            'requests_processed': 0,
            'total_processing_time': 0,
            'average_processing_time': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'errors': 0
        }


# Global instances
optimizer = WorkflowOptimizer()
performance_monitor = PerformanceMonitor()

def optimize_workflow(func):
    """Decorator to optimize workflow functions"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        cache_hit = False
        error = False
        
        try:
            # Try optimization first
            if len(args) > 0 and isinstance(args[0], dict):
                optimized_result = optimizer.optimize_content_generation(args[0])
                if optimized_result:
                    cache_hit = True
                    processing_time = time.time() - start_time
                    performance_monitor.record_request(processing_time, cache_hit)
                    return optimized_result
            
            # Execute original function
            result = func(*args, **kwargs)
            processing_time = time.time() - start_time
            performance_monitor.record_request(processing_time, cache_hit)
            
            return result
        
        except Exception as e:
            error = True
            processing_time = time.time() - start_time
            performance_monitor.record_request(processing_time, cache_hit, error)
            raise e
    
    return wrapper


if __name__ == "__main__":
    # Test optimization features
    print("🔧 Testing Workflow Optimization")
    
    # Test cache functionality
    test_data = {
        'brand_name': 'TestBrand',
        'topic': 'AI Technology',
        'tone': 'professional'
    }
    
    cache_key = optimizer.generate_cache_key(test_data)
    print(f"Generated cache key: {cache_key}")
    
    # Test performance monitoring
    performance_monitor.record_request(1.5, cache_hit=False)
    performance_monitor.record_request(0.3, cache_hit=True)
    
    metrics = performance_monitor.get_metrics()
    print(f"Performance metrics: {metrics}")
    
    print("✅ Optimization module ready!")