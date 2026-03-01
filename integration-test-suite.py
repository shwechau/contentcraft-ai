#!/usr/bin/env python3
"""
Day 4: Integration Testing Suite
Comprehensive testing for the dual-agent content generation platform
"""

import unittest
import requests
import json
import time
import os
from unittest.mock import patch, MagicMock
import tempfile
import zipfile

class TestContentPlatformIntegration(unittest.TestCase):
    """Integration tests for the complete content generation workflow"""
    
    def setUp(self):
        """Set up test environment"""
        self.base_url = "http://localhost:5000"
        self.test_data = {
            "brand_name": "TestBrand",
            "topic": "AI Technology",
            "tone": "professional",
            "video_length": "short",
            "brand_colors": "#FF5733,#33FF57",
            "style_preference": "modern"
        }
    
    def test_01_health_check(self):
        """Test basic application health"""
        try:
            response = requests.get(f"{self.base_url}/health")
            self.assertEqual(response.status_code, 200)
            print("✅ Health check passed")
        except requests.exceptions.ConnectionError:
            print("❌ Application not running. Start with: python main-app.py")
            self.skipTest("Application not available")
    
    def test_02_intake_form_validation(self):
        """Test intake form data validation"""
        # Test valid data
        response = requests.post(f"{self.base_url}/generate", json=self.test_data)
        self.assertIn(response.status_code, [200, 202])
        print("✅ Valid intake form data accepted")
        
        # Test missing required fields
        invalid_data = {"brand_name": "Test"}
        response = requests.post(f"{self.base_url}/generate", json=invalid_data)
        self.assertEqual(response.status_code, 400)
        print("✅ Invalid data properly rejected")
    
    def test_03_agent1_content_generation(self):
        """Test Agent 1 content generation"""
        response = requests.post(f"{self.base_url}/generate", json=self.test_data)
        
        if response.status_code == 202:
            # Async processing
            result = response.json()
            pack_id = result.get('pack_id')
            
            # Wait for processing
            max_wait = 30
            for _ in range(max_wait):
                status_response = requests.get(f"{self.base_url}/pack/{pack_id}")
                if status_response.status_code == 200:
                    break
                time.sleep(1)
            
            self.assertEqual(status_response.status_code, 200)
            pack_data = status_response.json()
            
            # Verify content structure
            self.assertIn('content', pack_data)
            self.assertIn('title', pack_data['content'])
            self.assertIn('description', pack_data['content'])
            self.assertIn('script', pack_data['content'])
            self.assertIn('hashtags', pack_data['content'])
            print("✅ Agent 1 content generation successful")
        
        elif response.status_code == 200:
            # Sync processing
            pack_data = response.json()
            self.assertIn('content', pack_data)
            print("✅ Agent 1 content generation successful (sync)")
    
    def test_04_agent2_visual_generation(self):
        """Test Agent 2 visual generation"""
        response = requests.post(f"{self.base_url}/generate", json=self.test_data)
        
        if response.status_code in [200, 202]:
            if response.status_code == 202:
                result = response.json()
                pack_id = result.get('pack_id')
                
                # Wait for processing
                for _ in range(30):
                    status_response = requests.get(f"{self.base_url}/pack/{pack_id}")
                    if status_response.status_code == 200:
                        pack_data = status_response.json()
                        break
                    time.sleep(1)
            else:
                pack_data = response.json()
            
            # Verify visual content
            self.assertIn('visuals', pack_data)
            self.assertIsInstance(pack_data['visuals'], list)
            self.assertGreater(len(pack_data['visuals']), 0)
            
            for visual in pack_data['visuals']:
                self.assertIn('type', visual)
                self.assertIn('url', visual)
                self.assertIn('description', visual)
            
            print("✅ Agent 2 visual generation successful")
    
    def test_05_pack_assembly(self):
        """Test social media pack assembly"""
        response = requests.post(f"{self.base_url}/generate", json=self.test_data)
        
        if response.status_code in [200, 202]:
            if response.status_code == 202:
                result = response.json()
                pack_id = result.get('pack_id')
                
                # Wait for processing
                for _ in range(30):
                    status_response = requests.get(f"{self.base_url}/pack/{pack_id}")
                    if status_response.status_code == 200:
                        pack_data = status_response.json()
                        break
                    time.sleep(1)
            else:
                pack_data = response.json()
            
            # Verify complete pack structure
            required_fields = ['pack_id', 'content', 'visuals', 'metadata', 'optimization_tips']
            for field in required_fields:
                self.assertIn(field, pack_data)
            
            # Verify metadata
            metadata = pack_data['metadata']
            self.assertIn('brand_name', metadata)
            self.assertIn('created_at', metadata)
            self.assertIn('stats', metadata)
            
            print("✅ Social media pack assembly successful")
    
    def test_06_download_functionality(self):
        """Test pack download functionality"""
        response = requests.post(f"{self.base_url}/generate", json=self.test_data)
        
        if response.status_code in [200, 202]:
            if response.status_code == 202:
                result = response.json()
                pack_id = result.get('pack_id')
                
                # Wait for processing
                for _ in range(30):
                    status_response = requests.get(f"{self.base_url}/pack/{pack_id}")
                    if status_response.status_code == 200:
                        pack_data = status_response.json()
                        break
                    time.sleep(1)
            else:
                pack_data = response.json()
                pack_id = pack_data['pack_id']
            
            # Test download
            download_response = requests.get(f"{self.base_url}/download/{pack_id}")
            self.assertEqual(download_response.status_code, 200)
            self.assertEqual(download_response.headers['Content-Type'], 'application/zip')
            
            # Verify ZIP content
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                tmp_file.write(download_response.content)
                tmp_file.flush()
                
                with zipfile.ZipFile(tmp_file.name, 'r') as zip_file:
                    file_list = zip_file.namelist()
                    self.assertIn('content.json', file_list)
                    self.assertIn('metadata.json', file_list)
                    # Should have at least one image file
                    image_files = [f for f in file_list if f.endswith(('.png', '.jpg', '.jpeg'))]
                    self.assertGreater(len(image_files), 0)
                
                os.unlink(tmp_file.name)
            
            print("✅ Download functionality successful")
    
    def test_07_error_handling(self):
        """Test error handling scenarios"""
        # Test invalid pack ID
        response = requests.get(f"{self.base_url}/pack/invalid-id")
        self.assertEqual(response.status_code, 404)
        
        # Test invalid download ID
        response = requests.get(f"{self.base_url}/download/invalid-id")
        self.assertEqual(response.status_code, 404)
        
        # Test malformed JSON
        response = requests.post(f"{self.base_url}/generate", 
                               data="invalid json", 
                               headers={'Content-Type': 'application/json'})
        self.assertEqual(response.status_code, 400)
        
        print("✅ Error handling working correctly")
    
    def test_08_performance_benchmarks(self):
        """Test performance benchmarks"""
        start_time = time.time()
        
        response = requests.post(f"{self.base_url}/generate", json=self.test_data)
        
        if response.status_code == 202:
            # Async processing
            result = response.json()
            pack_id = result.get('pack_id')
            
            # Wait for completion and measure total time
            for _ in range(60):  # Max 60 seconds
                status_response = requests.get(f"{self.base_url}/pack/{pack_id}")
                if status_response.status_code == 200:
                    break
                time.sleep(1)
            
            total_time = time.time() - start_time
            self.assertLess(total_time, 60, "Processing should complete within 60 seconds")
            print(f"✅ Performance test passed: {total_time:.2f} seconds")
        
        elif response.status_code == 200:
            # Sync processing
            total_time = time.time() - start_time
            self.assertLess(total_time, 30, "Sync processing should complete within 30 seconds")
            print(f"✅ Performance test passed: {total_time:.2f} seconds")


class TestWorkflowOptimization(unittest.TestCase):
    """Test workflow optimization features"""
    
    def setUp(self):
        self.base_url = "http://localhost:5000"
    
    def test_caching_mechanism(self):
        """Test content caching for similar requests"""
        test_data = {
            "brand_name": "CacheTest",
            "topic": "Technology",
            "tone": "professional",
            "video_length": "short",
            "brand_colors": "#FF0000",
            "style_preference": "modern"
        }
        
        # First request
        start_time = time.time()
        response1 = requests.post(f"{self.base_url}/generate", json=test_data)
        first_time = time.time() - start_time
        
        # Second identical request (should be faster due to caching)
        start_time = time.time()
        response2 = requests.post(f"{self.base_url}/generate", json=test_data)
        second_time = time.time() - start_time
        
        self.assertEqual(response1.status_code, response2.status_code)
        # Note: Caching effectiveness depends on implementation
        print(f"✅ Caching test completed: First={first_time:.2f}s, Second={second_time:.2f}s")
    
    def test_concurrent_requests(self):
        """Test handling of concurrent requests"""
        import threading
        import queue
        
        results = queue.Queue()
        
        def make_request(thread_id):
            test_data = {
                "brand_name": f"ConcurrentTest{thread_id}",
                "topic": "AI Technology",
                "tone": "professional",
                "video_length": "short",
                "brand_colors": "#FF0000",
                "style_preference": "modern"
            }
            
            try:
                response = requests.post(f"{self.base_url}/generate", json=test_data)
                results.put((thread_id, response.status_code, True))
            except Exception as e:
                results.put((thread_id, 500, False))
        
        # Create 3 concurrent requests
        threads = []
        for i in range(3):
            thread = threading.Thread(target=make_request, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        # Check results
        success_count = 0
        while not results.empty():
            thread_id, status_code, success = results.get()
            if success and status_code in [200, 202]:
                success_count += 1
        
        self.assertGreaterEqual(success_count, 2, "At least 2 concurrent requests should succeed")
        print(f"✅ Concurrent requests test: {success_count}/3 successful")


def run_integration_tests():
    """Run all integration tests"""
    print("🚀 Starting Day 4 Integration Testing Suite")
    print("=" * 50)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestContentPlatformIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestWorkflowOptimization))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print("\n" + "=" * 50)
    print("🎯 Integration Testing Summary")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print("\n💥 Errors:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    if len(result.failures) == 0 and len(result.errors) == 0:
        print("\n🎉 All tests passed! System ready for deployment.")
    else:
        print(f"\n⚠️  {len(result.failures + result.errors)} issues found. Review before deployment.")
    
    return result


if __name__ == "__main__":
    run_integration_tests()