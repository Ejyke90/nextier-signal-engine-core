"""
Demonstration script for multidimensional risk calculation
Tests the enhanced risk algorithm with climate, mining, and border indicators
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from predictor.services.risk_service import RiskService


def main():
    print("\n" + "="*80)
    print("MULTIDIMENSIONAL RISK INDICATOR DEMONSTRATION")
    print("Testing Enhanced Risk Algorithm with 2026 Nigeria Conflict Patterns")
    print("="*80 + "\n")
    
    # Initialize risk service
    print("Initializing Risk Service...")
    risk_service = RiskService()
    print(f"✓ Loaded {len(risk_service.climate_data)} climate data points")
    print(f"✓ Loaded {len(risk_service.mining_data)} mining sites")
    print(f"✓ Loaded {len(risk_service.border_data)} border zones\n")
    
    # Sample economic data
    econ_data = pd.DataFrame([
        {'State': 'Borno', 'LGA': 'Maiduguri', 'Fuel_Price': 650, 'Inflation': 24.5},
        {'State': 'Sokoto', 'LGA': 'Illela', 'Fuel_Price': 680, 'Inflation': 22.8},
        {'State': 'Adamawa', 'LGA': 'Yola', 'Fuel_Price': 620, 'Inflation': 24.7},
        {'State': 'Zamfara', 'LGA': 'Anka', 'Fuel_Price': 690, 'Inflation': 26.3},
        {'State': 'Kebbi', 'LGA': 'Argungu', 'Fuel_Price': 675, 'Inflation': 23.1}
    ])
    
    # Test 1: Flooding Multiplier
    print("="*80)
    print("TEST 1: FLOODING MULTIPLIER (Climate-Conflict Nexus)")
    print("="*80)
    print("Scenario: Farmer-herder clash in Adamawa/Yola (25.4% farmland flooded)")
    print("-"*80)
    
    event1 = {
        'event_type': 'clash',
        'state': 'Adamawa',
        'lga': 'Yola',
        'severity': 'high',
        'source_title': 'Farmer-Herder Clash in Yola Amid Flooding',
        'source_url': 'https://example.com/yola-clash'
    }
    
    signal1 = risk_service.calculate_risk_score(event1, econ_data)
    if signal1:
        print(f"✓ Risk Score: {signal1.risk_score} ({signal1.risk_level})")
        print(f"✓ Flood Inundation: {signal1.flood_inundation_index}%")
        print(f"✓ Vegetation Health: {signal1.vegetation_health_index}")
        print(f"✓ Trigger Reason: {signal1.trigger_reason}\n")
    
    # Test 2: Mining Proximity
    print("="*80)
    print("TEST 2: MINING MULTIPLIER (Illicit Economic Activity)")
    print("="*80)
    print("Scenario: Violence near Zamfara Gold Belt mining site")
    print("-"*80)
    
    event2 = {
        'event_type': 'violence',
        'state': 'Zamfara',
        'lga': 'Anka',
        'severity': 'high',
        'latitude': 12.1100,  # Near Zamfara Gold Belt
        'longitude': 5.9280,
        'source_title': 'Armed Violence Near Gold Mining Area',
        'source_url': 'https://example.com/zamfara-mining'
    }
    
    signal2 = risk_service.calculate_risk_score(event2, econ_data)
    if signal2:
        print(f"✓ Risk Score: {signal2.risk_score} ({signal2.risk_level})")
        print(f"✓ Mining Proximity: {signal2.mining_proximity_km:.1f}km from {signal2.mining_site_name}")
        print(f"✓ High Funding Potential: {signal2.high_funding_potential}")
        print(f"✓ Informal Taxation Rate: {signal2.informal_taxation_rate*100:.0f}%")
        print(f"✓ Trigger Reason: {signal2.trigger_reason}\n")
    
    # Test 3: Lakurawa Presence (Sokoto)
    print("="*80)
    print("TEST 3: SAHELIAN MULTIPLIER - Lakurawa Detection (Sokoto)")
    print("="*80)
    print("Scenario: Cross-border conflict in Sokoto-Niger corridor")
    print("-"*80)
    
    event3 = {
        'event_type': 'conflict',
        'state': 'Sokoto',
        'lga': 'Illela',
        'severity': 'critical',
        'source_title': 'Lakurawa Group Attack in Sokoto Border Area',
        'source_url': 'https://example.com/sokoto-lakurawa'
    }
    
    signal3 = risk_service.calculate_risk_score(event3, econ_data)
    if signal3:
        print(f"✓ Risk Score: {signal3.risk_score} ({signal3.risk_level})")
        print(f"✓ Border Activity: {signal3.border_activity}")
        print(f"✓ Lakurawa Presence: {signal3.lakurawa_presence}")
        print(f"✓ Group Affiliation: {signal3.group_affiliation}")
        print(f"✓ Border Permeability: {signal3.border_permeability_score*100:.0f}%")
        print(f"✓ Sophisticated IED Usage: {signal3.sophisticated_ied_usage}")
        print(f"✓ Trigger Reason: {signal3.trigger_reason}\n")
    
    # Test 4: Lakurawa Presence (Kebbi)
    print("="*80)
    print("TEST 4: SAHELIAN MULTIPLIER - Lakurawa Detection (Kebbi)")
    print("="*80)
    print("Scenario: Cross-border clash in Kebbi-Niger border")
    print("-"*80)
    
    event4 = {
        'event_type': 'clash',
        'state': 'Kebbi',
        'lga': 'Argungu',
        'severity': 'high',
        'source_title': 'Cross-Border Clash in Kebbi',
        'source_url': 'https://example.com/kebbi-border'
    }
    
    signal4 = risk_service.calculate_risk_score(event4, econ_data)
    if signal4:
        print(f"✓ Risk Score: {signal4.risk_score} ({signal4.risk_level})")
        print(f"✓ Border Activity: {signal4.border_activity}")
        print(f"✓ Lakurawa Presence: {signal4.lakurawa_presence}")
        print(f"✓ Group Affiliation: {signal4.group_affiliation}")
        print(f"✓ Trigger Reason: {signal4.trigger_reason}\n")
    
    # Test 5: Combined Multipliers
    print("="*80)
    print("TEST 5: COMBINED MULTIPLIERS (Multi-Factor Risk)")
    print("="*80)
    print("Scenario: Clash in flooded area with high inflation")
    print("-"*80)
    
    event5 = {
        'event_type': 'clash',
        'state': 'Adamawa',
        'lga': 'Yola',
        'severity': 'critical',
        'latitude': 9.2000,
        'longitude': 12.4800,
        'source_title': 'Multi-Factor Conflict in Adamawa',
        'source_url': 'https://example.com/multi-factor'
    }
    
    signal5 = risk_service.calculate_risk_score(event5, econ_data)
    if signal5:
        print(f"✓ Risk Score: {signal5.risk_score} ({signal5.risk_level})")
        print(f"✓ Flood Inundation: {signal5.flood_inundation_index}%")
        print(f"✓ Inflation: {signal5.inflation}%")
        print(f"✓ Fuel Price: ₦{signal5.fuel_price}")
        print(f"✓ Trigger Reason: {signal5.trigger_reason}\n")
    
    # Summary
    print("="*80)
    print("DEMONSTRATION COMPLETE - GEOSPATIAL EARLY WARNING SYSTEM")
    print("="*80)
    print("\nKey Capabilities Demonstrated:")
    print("✓ Climate-Conflict Nexus: Flooding multiplier for resource competition")
    print("✓ Illicit Economic Activity: Mining proximity flags high funding potential")
    print("✓ Transnational Threats: Lakurawa presence detection in Sokoto/Kebbi")
    print("✓ Explainable AI: Detailed trigger_reason for each risk assessment")
    print("✓ Multidimensional Analysis: Combined climate, economic, and security factors")
    print("\nThis PoC demonstrates a holistic geospatial early warning system that")
    print("goes beyond news scraping to integrate climate, economic, and border data.")
    print("="*80 + "\n")


if __name__ == '__main__':
    main()
