#!/usr/bin/env python3
import requests
import time
import sys

def check_health(url, service_name):
    """Check health of a service"""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"✅ {service_name}: Healthy")
            return True
        else:
            print(f"❌ {service_name}: Unhealthy (Status {response.status_code})")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ {service_name}: Unavailable ({str(e)})")
        return False

def main():
    services = [
        ("http://localhost:8000/health", "Scraper"),
        ("http://localhost:8001/health", "Intelligence API"),
        ("http://localhost:8002/health", "Predictor"),
        ("http://localhost:8080/health", "UI")
    ]
    
    print("🔍 Checking service health...")
    
    all_healthy = True
    for url, name in services:
        if not check_health(url, name):
            all_healthy = False
    
    if all_healthy:
        print("\n✅ All services are healthy!")
        return 0
    else:
        print("\n⚠️ Some services are unhealthy")
        return 1

if __name__ == "__main__":
    sys.exit(main())
