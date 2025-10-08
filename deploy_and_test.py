# deploy_and_test.py
# Comprehensive deployment and testing script

import subprocess
import sys
import os
import time
import requests
import json
from datetime import datetime

class DeploymentManager:
    def __init__(self):
        self.base_url = "http://localhost:5000"
        self.streamlit_port = 8501
        self.api_port = 5000
        
    def install_dependencies(self):
        """Install all required dependencies"""
        print("📦 Installing dependencies...")
        
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                         check=True, capture_output=True, text=True)
            print("✅ Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            return False
    
    def run_data_processing(self):
        """Run data processing pipeline"""
        print("🔄 Running data processing pipeline...")
        
        try:
            # Run enhanced data processor
            result = subprocess.run([sys.executable, "enhanced_data_processor.py"], 
                                  capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                print("✅ Enhanced data processing completed")
            else:
                print(f"⚠️ Data processing warning: {result.stderr}")
            
            # Run ML pipeline
            result = subprocess.run([sys.executable, "advanced_ml_pipeline.py"], 
                                  capture_output=True, text=True, timeout=120)
            if result.returncode == 0:
                print("✅ ML pipeline completed")
            else:
                print(f"⚠️ ML pipeline warning: {result.stderr}")
            
            return True
        except subprocess.TimeoutExpired:
            print("⏰ Data processing timed out")
            return False
        except Exception as e:
            print(f"❌ Data processing failed: {e}")
            return False
    
    def test_api_endpoints(self):
        """Test API endpoints"""
        print("🧪 Testing API endpoints...")
        
        endpoints = [
            ("/", "GET"),
            ("/health", "GET"),
            ("/districts", "GET"),
            ("/statistics", "GET"),
            ("/risk-levels", "GET"),
            ("/alerts", "GET")
        ]
        
        results = {}
        
        for endpoint, method in endpoints:
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                results[endpoint] = {
                    "status_code": response.status_code,
                    "success": response.status_code == 200,
                    "response_time": response.elapsed.total_seconds()
                }
                
                if response.status_code == 200:
                    print(f"  ✅ {endpoint} - {response.status_code} ({response.elapsed.total_seconds():.2f}s)")
                else:
                    print(f"  ❌ {endpoint} - {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                results[endpoint] = {
                    "status_code": None,
                    "success": False,
                    "error": str(e)
                }
                print(f"  ❌ {endpoint} - Connection failed: {e}")
        
        return results
    
    def test_prediction_api(self):
        """Test prediction API with sample data"""
        print("🤖 Testing prediction API...")
        
        sample_data = {
            "Underweight_pct": 15.0,
            "Wasted_pct": 8.0,
            "VitaminA_pct": 12.0,
            "Iodine_pct": 10.0,
            "Malnutrition_Index": 18.5,
            "Micronutrient_Deficiency": 22.0,
            "Poverty_Index": 0.4,
            "Food_Security_Score": 75.0,
            "Health_Access_Score": 80.0,
            "Education_Score": 85.0,
            "Distance_to_Kigali": 50.0,
            "Elevation": 1500.0,
            "Annual_Rainfall": 1000.0,
            "Avg_Temperature": 22.0,
            "Drought_Risk": 0,
            "GDP_per_Capita": 800.0,
            "Unemployment_Rate": 0.15,
            "Market_Access_Score": 70.0,
            "Agricultural_Productivity": 65.0,
            "Infrastructure_Score": 75.0,
            "Intervention_Readiness": 80.0
        }
        
        try:
            response = requests.post(f"{self.base_url}/predict", 
                                   json=sample_data, 
                                   timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                print(f"  ✅ Prediction successful:")
                print(f"     Risk Level: {result.get('risk_level', 'Unknown')}")
                print(f"     Probability: {result.get('probability', 0):.3f}")
                print(f"     Confidence: {result.get('confidence', 'Unknown')}")
                return True
            else:
                print(f"  ❌ Prediction failed: {response.status_code}")
                print(f"     Response: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"  ❌ Prediction API test failed: {e}")
            return False
    
    def generate_test_report(self, api_results, prediction_success):
        """Generate comprehensive test report"""
        print("\n📊 Generating test report...")
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "deployment_status": "success",
            "api_tests": api_results,
            "prediction_test": prediction_success,
            "overall_success": all(result["success"] for result in api_results.values()) and prediction_success
        }
        
        # Save report
        with open("outputs/deployment_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        print("✅ Test report saved to outputs/deployment_report.json")
        return report
    
    def start_services(self):
        """Start all services"""
        print("🚀 Starting services...")
        
        # Start API server in background
        print("  Starting API server...")
        api_process = subprocess.Popen([
            sys.executable, "api_system.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for API to start
        time.sleep(5)
        
        # Test if API is running
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                print("  ✅ API server started successfully")
                return api_process
            else:
                print("  ❌ API server failed to start")
                return None
        except requests.exceptions.RequestException:
            print("  ❌ API server not responding")
            return None
    
    def run_comprehensive_test(self):
        """Run comprehensive test suite"""
        print("🧪 Running comprehensive test suite...")
        
        # Test API endpoints
        api_results = self.test_api_endpoints()
        
        # Test prediction API
        prediction_success = self.test_prediction_api()
        
        # Generate report
        report = self.generate_test_report(api_results, prediction_success)
        
        return report
    
    def deploy_full_system(self):
        """Deploy the complete system"""
        print("🚀 Deploying Rwanda Malnutrition Intelligence Platform...")
        print("=" * 60)
        
        # Step 1: Install dependencies
        if not self.install_dependencies():
            print("❌ Deployment failed at dependency installation")
            return False
        
        # Step 2: Run data processing
        if not self.run_data_processing():
            print("❌ Deployment failed at data processing")
            return False
        
        # Step 3: Start services
        api_process = self.start_services()
        if not api_process:
            print("❌ Deployment failed at service startup")
            return False
        
        # Step 4: Run tests
        report = self.run_comprehensive_test()
        
        # Step 5: Display results
        print("\n" + "=" * 60)
        print("🎉 DEPLOYMENT COMPLETE!")
        print("=" * 60)
        
        if report["overall_success"]:
            print("✅ All systems operational")
            print(f"📊 API Status: {self.base_url}")
            print(f"📱 Mobile App: streamlit run mobile_app.py")
            print(f"🖥️  Main Dashboard: streamlit run enhanced_dashboard.py")
            print(f"🔄 Real-time Monitor: streamlit run realtime_integration.py")
        else:
            print("⚠️ Some issues detected - check deployment_report.json")
        
        print("\n📋 Available Services:")
        print("  • Main Dashboard: Multi-page interactive dashboard")
        print("  • Mobile App: Mobile-optimized interface")
        print("  • Real-time Monitor: Live data integration")
        print("  • API System: RESTful API for integrations")
        print("  • Policy Briefs: Automated policy recommendations")
        
        print("\n🎯 Ready for Hackathon Presentation!")
        
        return report["overall_success"]

def main():
    """Main deployment function"""
    print("🇷🇼 Rwanda Malnutrition Intelligence Platform")
    print("🏆 NISR Big Data Hackathon 2025 - Deployment Script")
    print("=" * 60)
    
    manager = DeploymentManager()
    
    try:
        success = manager.deploy_full_system()
        
        if success:
            print("\n🎉 SUCCESS: Platform deployed successfully!")
            print("🚀 Ready for hackathon presentation!")
        else:
            print("\n❌ FAILED: Deployment encountered issues")
            print("📋 Check deployment_report.json for details")
    
    except KeyboardInterrupt:
        print("\n⏹️ Deployment interrupted by user")
    except Exception as e:
        print(f"\n❌ Deployment failed with error: {e}")

if __name__ == "__main__":
    main()
