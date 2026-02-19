"""
Example client for PharmaGuard REST API
Shows how to use the API from Python code
"""
import requests
import time
from typing import Optional, Dict, Any
import json

class PharmaGuardClient:
    """Client for PharmaGuard REST API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize client"""
        self.base_url = base_url
        self.session = requests.Session()
    
    def health(self) -> Dict[str, Any]:
        """Check API health"""
        response = self.session.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    def upload_vcf(self, file_path: str) -> str:
        """
        Upload a VCF file
        
        Args:
            file_path: Path to VCF file
            
        Returns:
            file_id: Unique file identifier
        """
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = self.session.post(
                f"{self.base_url}/upload",
                files=files
            )
        response.raise_for_status()
        return response.json()['file_id']
    
    def start_analysis(self, file_id: str, drugs: list = None) -> str:
        """
        Start analysis of uploaded file
        
        Args:
            file_id: File ID to analyze
            drugs: List of drugs (optional)
            
        Returns:
            analysis_id: Unique analysis identifier
        """
        if drugs is None:
            drugs = ["Codeine", "Warfarin"]
        
        payload = {
            "file_id": file_id,
            "drugs": drugs
        }
        
        response = self.session.post(
            f"{self.base_url}/analyze",
            json=payload
        )
        response.raise_for_status()
        return response.json()['analysis_id']
    
    def get_results(self, analysis_id: str) -> Dict[str, Any]:
        """
        Get analysis results
        
        Args:
            analysis_id: Analysis ID
            
        Returns:
            results: Analysis results
        """
        response = self.session.get(
            f"{self.base_url}/results/{analysis_id}"
        )
        response.raise_for_status()
        return response.json()
    
    def wait_for_results(
        self, 
        analysis_id: str, 
        timeout: int = 300,
        poll_interval: int = 2
    ) -> Dict[str, Any]:
        """
        Wait for analysis to complete
        
        Args:
            analysis_id: Analysis ID
            timeout: Max wait time in seconds
            poll_interval: Poll interval in seconds
            
        Returns:
            results: Analysis results when complete
            
        Raises:
            TimeoutError: If analysis takes too long
        """
        elapsed = 0
        
        while elapsed < timeout:
            result = self.get_results(analysis_id)
            status = result['status']
            
            if status == "completed":
                return result
            elif status == "error":
                raise Exception(f"Analysis failed: {result['error']}")
            
            print(f"  Status: {status} (elapsed: {elapsed}s)")
            time.sleep(poll_interval)
            elapsed += poll_interval
        
        raise TimeoutError(f"Analysis did not complete within {timeout} seconds")
    
    def analyze_vcf(
        self,
        file_path: str,
        drugs: list = None,
        wait: bool = True,
        timeout: int = 300
    ) -> Dict[str, Any]:
        """
        Complete workflow: upload, analyze, and get results
        
        Args:
            file_path: Path to VCF file
            drugs: List of drugs to analyze
            wait: Wait for completion before returning
            timeout: Max wait time
            
        Returns:
            results: Complete analysis results
        """
        print(f"Uploading {file_path}...")
        file_id = self.upload_vcf(file_path)
        print(f"  File ID: {file_id}")
        
        print(f"Starting analysis...")
        analysis_id = self.start_analysis(file_id, drugs)
        print(f"  Analysis ID: {analysis_id}")
        
        if wait:
            print(f"Waiting for results...")
            return self.wait_for_results(analysis_id, timeout)
        else:
            return {"analysis_id": analysis_id, "status": "processing"}


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

def example_1_complete_workflow():
    """Example 1: Complete workflow in one call"""
    print("\n" + "="*80)
    print("EXAMPLE 1: Complete Workflow")
    print("="*80)
    
    client = PharmaGuardClient()
    
    try:
        # Check health
        health = client.health()
        print(f"API Status: {health['status']}")
        print(f"LLM Available: {health['llm_available']}")
        
        # Analyze VCF file
        results = client.analyze_vcf(
            "sample_vcf/warfarin_dose.vcf",
            drugs=["Warfarin"],
            wait=True,
            timeout=120
        )
        
        print(f"\n✅ Analysis Complete!")
        print(f"Drugs analyzed: {results['drugs_analyzed']}")
        
        if results['results']:
            for drug_result in results['results']:
                print(f"\nDrug: {drug_result['drug']}")
                print(f"Risk: {drug_result['risk_assessment']['risk_label']}")
                
                if 'llm_generated_explanation' in drug_result:
                    llm = drug_result['llm_generated_explanation']
                    print(f"LLM Source: {llm['source']}")
    
    except Exception as e:
        print(f"❌ Error: {e}")


def example_2_manual_workflow():
    """Example 2: Manual step-by-step workflow"""
    print("\n" + "="*80)
    print("EXAMPLE 2: Manual Step-by-Step Workflow")
    print("="*80)
    
    client = PharmaGuardClient()
    
    try:
        # Step 1: Upload
        print("\nStep 1: Upload VCF file")
        file_id = client.upload_vcf("sample_vcf/codeine_risk.vcf")
        print(f"  ✓ File uploaded: {file_id}")
        
        # Step 2: Start analysis
        print("\nStep 2: Start analysis")
        analysis_id = client.start_analysis(file_id, ["Codeine"])
        print(f"  ✓ Analysis started: {analysis_id}")
        
        # Step 3: Check status
        print("\nStep 3: Check status")
        for i in range(5):
            result = client.get_results(analysis_id)
            status = result['status']
            print(f"  Attempt {i+1}: {status}")
            
            if status == "completed":
                print(f"  ✓ Analysis complete!")
                break
            elif status == "error":
                print(f"  ✗ Analysis failed: {result['error']}")
                break
            
            time.sleep(3)
    
    except Exception as e:
        print(f"❌ Error: {e}")


def example_3_async_analysis():
    """Example 3: Async workflow - start and check later"""
    print("\n" + "="*80)
    print("EXAMPLE 3: Async Workflow")
    print("="*80)
    
    client = PharmaGuardClient()
    
    try:
        # Start analysis (don't wait)
        print("Starting analysis (async)...")
        file_id = client.upload_vcf("sample_vcf/comprehensive_test.vcf")
        analysis_id = client.start_analysis(file_id)
        print(f"  Analysis ID: {analysis_id}")
        print("  (Can close this program and check later)")
        
        # Later, check results
        import time as time_module
        time_module.sleep(2)
        
        print("\nChecking results...")
        result = client.get_results(analysis_id)
        print(f"  Status: {result['status']}")
        
        if result['status'] == "completed" and result['results']:
            print(f"  Found {len(result['results'])} drug assessments")
    
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    print("""
    PharmaGuard REST API Client Examples
    
    Make sure the API is running:
        python api.py
    
    Choose an example to run:
        python example=1  # Complete workflow
        python example=2  # Step-by-step
        python example=3  # Async
    
    Or run this file directly to see all examples.
    """)
    
    try:
        import sys
        if len(sys.argv) > 1:
            example_num = int(sys.argv[1].split('=')[1])
            if example_num == 1:
                example_1_complete_workflow()
            elif example_num == 2:
                example_2_manual_workflow()
            elif example_num == 3:
                example_3_async_analysis()
        else:
            # Try to run all examples
            try:
                example_1_complete_workflow()
            except Exception as e:
                print(f"Example 1 failed: {e}")
            
            try:
                example_2_manual_workflow()
            except Exception as e:
                print(f"Example 2 failed: {e}")
            
            try:
                example_3_async_analysis()
            except Exception as e:
                print(f"Example 3 failed: {e}")
    
    except KeyboardInterrupt:
        print("\n\nExamples interrupted")
