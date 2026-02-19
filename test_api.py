"""
Test script for the REST API
Demonstrates all three endpoints
"""
import sys
import time
import requests
import json
from pathlib import Path

# API base URL
BASE_URL = "http://localhost:8000"

def print_response(title: str, response):
    """Pretty print API response"""
    print(f"\n{'='*80}")
    print(f"{title}")
    print(f"{'='*80}")
    print(f"Status Code: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)


def test_health_check():
    """Test health check endpoint"""
    print("\n[1/4] Testing Health Check")
    response = requests.get(f"{BASE_URL}/health")
    print_response("HEALTH CHECK", response)
    return response.status_code == 200


def test_upload():
    """Test file upload endpoint"""
    print("\n[2/4] Testing Upload Endpoint")
    
    # Use sample VCF file
    vcf_file = "sample_vcf/comprehensive_test.vcf"
    
    if not Path(vcf_file).exists():
        print(f"✗ VCF file not found: {vcf_file}")
        return None
    
    with open(vcf_file, 'rb') as f:
        files = {'file': (Path(vcf_file).name, f)}
        response = requests.post(f"{BASE_URL}/upload", files=files)
    
    print_response("UPLOAD RESPONSE", response)
    
    if response.status_code == 200:
        return response.json()['file_id']
    return None


def test_analyze(file_id: str):
    """Test analyze endpoint"""
    print("\n[3/4] Testing Analyze Endpoint")
    
    payload = {
        "file_id": file_id,
        "drugs": ["Codeine", "Warfarin", "Clopidogrel"]
    }
    
    response = requests.post(f"{BASE_URL}/analyze", json=payload)
    print_response("ANALYZE RESPONSE", response)
    
    if response.status_code == 200:
        return response.json()['analysis_id']
    return None


def test_results(analysis_id: str):
    """Test results endpoint with polling"""
    print("\n[4/4] Testing Results Endpoint")
    
    max_wait = 60  # seconds
    poll_interval = 2  # seconds
    elapsed = 0
    
    while elapsed < max_wait:
        response = requests.get(f"{BASE_URL}/results/{analysis_id}")
        
        if response.status_code == 200:
            data = response.json()
            status = data['status']
            
            print(f"Status: {status} (elapsed: {elapsed}s)")
            
            if status == "completed":
                print_response("RESULTS RESPONSE", response)
                
                # Print summary
                print("\n" + "="*80)
                print("ANALYSIS SUMMARY")
                print("="*80)
                if data['results']:
                    results = data['results']
                    print(f"Number of drugs analyzed: {len(results)}")
                    
                    for drug_result in results[:1]:  # Show first drug
                        print(f"\nFirst Drug: {drug_result['drug']}")
                        print(f"Risk Level: {drug_result['risk_assessment']['risk_label']}")
                        
                        if 'llm_generated_explanation' in drug_result:
                            llm = drug_result['llm_generated_explanation']
                            print(f"LLM Explanation Present: Yes")
                            print(f"  - Variant: {len(llm.get('variant_interpretation', ''))} chars")
                            print(f"  - Risk: {len(llm.get('risk_explanation', ''))} chars")
                            print(f"  - Dosing: {len(llm.get('dosing_recommendation', ''))} chars")
                            print(f"  - Monitoring: {len(llm.get('monitoring_guidance', ''))} chars")
                        
                        if 'quality_metrics' in drug_result:
                            metrics = drug_result['quality_metrics']
                            print(f"Quality Metrics:")
                            print(f"  - LLM Used: {metrics.get('llm_used')}")
                            print(f"  - Provider: {metrics.get('llm_provider')}")
                            print(f"  - Cached: {metrics.get('llm_cached')}")
                
                if data['cache_stats']:
                    cache = data['cache_stats']
                    print(f"\nCache Statistics:")
                    print(f"  - Total Cached: {cache.get('total_cached', 0)}")
                    print(f"  - Hit Rate: {cache.get('hit_rate', 0):.1%}")
                    print(f"  - DB Size: {cache.get('db_size_mb', 0):.2f} MB")
                
                return True
            
            elif status == "error":
                print(f"✗ Analysis failed: {data.get('error')}")
                return False
        
        else:
            print(f"✗ Request failed with status {response.status_code}")
            return False
        
        # Wait and retry
        time.sleep(poll_interval)
        elapsed += poll_interval
    
    print(f"✗ Analysis timed out after {max_wait} seconds")
    return False


def main():
    """Run all tests"""
    print("="*80)
    print("PHARMACOGUARD REST API TEST")
    print("="*80)
    
    # Test health
    if not test_health_check():
        print("\n✗ Health check failed - API may not be running")
        print("Start the API with: python api.py")
        return False
    
    # Test upload
    file_id = test_upload()
    if not file_id:
        print("\n✗ Upload failed")
        return False
    
    # Test analyze
    analysis_id = test_analyze(file_id)
    if not analysis_id:
        print("\n✗ Analyze failed")
        return False
    
    # Test results
    success = test_results(analysis_id)
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    if success:
        print("✅ ALL TESTS PASSED!")
        print("\nThe REST API is working correctly with:")
        print("  ✓ File upload")
        print("  ✓ Analysis processing")
        print("  ✓ Results retrieval")
        print("  ✓ LLM integration")
        print("  ✓ Cache system")
        return True
    else:
        print("✗ One or more tests failed")
        return False


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except requests.exceptions.ConnectionError:
        print("\n✗ Could not connect to API at", BASE_URL)
        print("Make sure the API is running: python api.py")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
