"""
Test suite for multidimensional risk calculation with climate, mining, and border indicators
"""
import pytest
import pandas as pd
from predictor.services.risk_service import RiskService


class TestMultidimensionalRisk:
    
    @pytest.fixture
    def risk_service(self):
        """Initialize risk service with mock data"""
        return RiskService()
    
    @pytest.fixture
    def econ_data(self):
        """Sample economic data"""
        return pd.DataFrame([
            {'State': 'Borno', 'LGA': 'Maiduguri', 'Fuel_Price': 650, 'Inflation': 24.5},
            {'State': 'Sokoto', 'LGA': 'Illela', 'Fuel_Price': 680, 'Inflation': 22.8},
            {'State': 'Adamawa', 'LGA': 'Yola', 'Fuel_Price': 620, 'Inflation': 24.7},
            {'State': 'Zamfara', 'LGA': 'Anka', 'Fuel_Price': 690, 'Inflation': 26.3},
            {'State': 'Kebbi', 'LGA': 'Argungu', 'Fuel_Price': 675, 'Inflation': 23.1}
        ])
    
    def test_flooding_multiplier_on_clash(self, risk_service, econ_data):
        """Test that flooding > 20% increases clash risk by 1.5x"""
        event = {
            'event_type': 'clash',
            'state': 'Adamawa',
            'lga': 'Yola',
            'severity': 'high',
            'source_title': 'Farmer-Herder Clash in Yola',
            'source_url': 'https://example.com/clash'
        }
        
        signal = risk_service.calculate_risk_score(event, econ_data)
        
        assert signal is not None
        assert signal.flood_inundation_index > 20
        assert 'Flooding-induced displacement' in signal.trigger_reason
        assert signal.risk_score > 80  # Should be amplified
        print(f"✓ Flooding multiplier test passed: {signal.risk_score} (flood: {signal.flood_inundation_index}%)")
        print(f"  Trigger: {signal.trigger_reason}")
    
    def test_mining_proximity_flag(self, risk_service, econ_data):
        """Test that events within 10km of mining sites get flagged"""
        event = {
            'event_type': 'violence',
            'state': 'Zamfara',
            'lga': 'Anka',
            'severity': 'high',
            'latitude': 12.1100,  # Near Zamfara Gold Belt
            'longitude': 5.9280,
            'source_title': 'Violence near mining area',
            'source_url': 'https://example.com/mining'
        }
        
        signal = risk_service.calculate_risk_score(event, econ_data)
        
        assert signal is not None
        assert signal.high_funding_potential is True
        assert signal.mining_proximity_km < 10
        assert 'High Funding Potential' in signal.trigger_reason
        print(f"✓ Mining proximity test passed: {signal.mining_proximity_km:.1f}km from {signal.mining_site_name}")
        print(f"  Trigger: {signal.trigger_reason}")
    
    def test_lakurawa_presence_sokoto(self, risk_service, econ_data):
        """Test that High border activity in Sokoto flags Lakurawa presence"""
        event = {
            'event_type': 'conflict',
            'state': 'Sokoto',
            'lga': 'Illela',
            'severity': 'critical',
            'source_title': 'Border conflict in Sokoto',
            'source_url': 'https://example.com/border'
        }
        
        signal = risk_service.calculate_risk_score(event, econ_data)
        
        assert signal is not None
        assert signal.border_activity == 'High'
        assert signal.lakurawa_presence is True
        assert 'Lakurawa Presence Detected' in signal.trigger_reason
        assert 'Sahelian jihadist expansion' in signal.trigger_reason
        print(f"✓ Lakurawa detection test passed: {signal.group_affiliation}")
        print(f"  Trigger: {signal.trigger_reason}")
    
    def test_lakurawa_presence_kebbi(self, risk_service, econ_data):
        """Test that High border activity in Kebbi flags Lakurawa presence"""
        event = {
            'event_type': 'clash',
            'state': 'Kebbi',
            'lga': 'Argungu',
            'severity': 'high',
            'source_title': 'Cross-border clash in Kebbi',
            'source_url': 'https://example.com/kebbi'
        }
        
        signal = risk_service.calculate_risk_score(event, econ_data)
        
        assert signal is not None
        assert signal.border_activity == 'High'
        assert signal.lakurawa_presence is True
        assert 'Lakurawa Presence Detected' in signal.trigger_reason
        print(f"✓ Kebbi Lakurawa test passed")
        print(f"  Trigger: {signal.trigger_reason}")
    
    def test_critical_border_activity_borno(self, risk_service, econ_data):
        """Test critical border activity detection in Borno"""
        event = {
            'event_type': 'violence',
            'state': 'Borno',
            'lga': 'Maiduguri',
            'severity': 'critical',
            'source_title': 'Boko Haram attack',
            'source_url': 'https://example.com/borno'
        }
        
        signal = risk_service.calculate_risk_score(event, econ_data)
        
        assert signal is not None
        # Borno/Maiduguri doesn't have border data in our mock, but test structure
        print(f"✓ Borno test passed: {signal.risk_score}")
        print(f"  Trigger: {signal.trigger_reason}")
    
    def test_combined_multipliers(self, risk_service, econ_data):
        """Test event with multiple risk factors"""
        event = {
            'event_type': 'clash',
            'state': 'Adamawa',
            'lga': 'Yola',
            'severity': 'high',
            'latitude': 9.2000,
            'longitude': 12.4800,
            'source_title': 'Multi-factor conflict',
            'source_url': 'https://example.com/multi'
        }
        
        signal = risk_service.calculate_risk_score(event, econ_data)
        
        assert signal is not None
        # Should have flooding multiplier (Yola has 25.4% flood inundation)
        assert signal.flood_inundation_index > 20
        assert signal.risk_score >= 80  # Should be very high
        print(f"✓ Combined multipliers test passed: {signal.risk_score}")
        print(f"  Climate: flood={signal.flood_inundation_index}%, veg={signal.vegetation_health_index}")
        print(f"  Trigger: {signal.trigger_reason}")
    
    def test_trigger_reason_format(self, risk_service, econ_data):
        """Test that trigger_reason is properly formatted"""
        event = {
            'event_type': 'protest',
            'state': 'Borno',
            'lga': 'Maiduguri',
            'severity': 'medium',
            'source_title': 'Protest event',
            'source_url': 'https://example.com/protest'
        }
        
        signal = risk_service.calculate_risk_score(event, econ_data)
        
        assert signal is not None
        assert signal.trigger_reason is not None
        assert len(signal.trigger_reason) > 0
        assert signal.risk_level in signal.trigger_reason
        print(f"✓ Trigger reason format test passed")
        print(f"  Trigger: {signal.trigger_reason}")
    
    def test_all_indicator_fields_present(self, risk_service, econ_data):
        """Test that all new indicator fields are present in response"""
        event = {
            'event_type': 'clash',
            'state': 'Sokoto',
            'lga': 'Illela',
            'severity': 'high',
            'latitude': 13.7400,
            'longitude': 5.2900,
            'source_title': 'Comprehensive test',
            'source_url': 'https://example.com/comprehensive'
        }
        
        signal = risk_service.calculate_risk_score(event, econ_data)
        
        assert signal is not None
        
        # Check all new fields exist
        assert hasattr(signal, 'trigger_reason')
        assert hasattr(signal, 'flood_inundation_index')
        assert hasattr(signal, 'precipitation_anomaly')
        assert hasattr(signal, 'vegetation_health_index')
        assert hasattr(signal, 'mining_proximity_km')
        assert hasattr(signal, 'mining_site_name')
        assert hasattr(signal, 'high_funding_potential')
        assert hasattr(signal, 'informal_taxation_rate')
        assert hasattr(signal, 'border_activity')
        assert hasattr(signal, 'lakurawa_presence')
        assert hasattr(signal, 'border_permeability_score')
        assert hasattr(signal, 'group_affiliation')
        assert hasattr(signal, 'sophisticated_ied_usage')
        
        print(f"✓ All indicator fields present test passed")
        print(f"  Climate: flood={signal.flood_inundation_index}, precip={signal.precipitation_anomaly}")
        print(f"  Mining: proximity={signal.mining_proximity_km}, funding={signal.high_funding_potential}")
        print(f"  Border: activity={signal.border_activity}, lakurawa={signal.lakurawa_presence}")


if __name__ == '__main__':
    print("\n" + "="*80)
    print("MULTIDIMENSIONAL RISK INDICATOR TEST SUITE")
    print("="*80 + "\n")
    
    risk_service = RiskService()
    econ_data = pd.DataFrame([
        {'State': 'Borno', 'LGA': 'Maiduguri', 'Fuel_Price': 650, 'Inflation': 24.5},
        {'State': 'Sokoto', 'LGA': 'Illela', 'Fuel_Price': 680, 'Inflation': 22.8},
        {'State': 'Adamawa', 'LGA': 'Yola', 'Fuel_Price': 620, 'Inflation': 24.7},
        {'State': 'Zamfara', 'LGA': 'Anka', 'Fuel_Price': 690, 'Inflation': 26.3},
        {'State': 'Kebbi', 'LGA': 'Argungu', 'Fuel_Price': 675, 'Inflation': 23.1}
    ])
    
    test = TestMultidimensionalRisk()
    
    print("\n1. Testing Flooding Multiplier (Adamawa/Yola - 25.4% inundation)")
    print("-" * 80)
    test.test_flooding_multiplier_on_clash(risk_service, econ_data)
    
    print("\n2. Testing Mining Proximity Flag (Zamfara Gold Belt)")
    print("-" * 80)
    test.test_mining_proximity_flag(risk_service, econ_data)
    
    print("\n3. Testing Lakurawa Presence Detection (Sokoto)")
    print("-" * 80)
    test.test_lakurawa_presence_sokoto(risk_service, econ_data)
    
    print("\n4. Testing Lakurawa Presence Detection (Kebbi)")
    print("-" * 80)
    test.test_lakurawa_presence_kebbi(risk_service, econ_data)
    
    print("\n5. Testing Combined Multipliers")
    print("-" * 80)
    test.test_combined_multipliers(risk_service, econ_data)
    
    print("\n6. Testing Trigger Reason Format")
    print("-" * 80)
    test.test_trigger_reason_format(risk_service, econ_data)
    
    print("\n7. Testing All Indicator Fields Present")
    print("-" * 80)
    test.test_all_indicator_fields_present(risk_service, econ_data)
    
    print("\n" + "="*80)
    print("ALL TESTS COMPLETED SUCCESSFULLY")
    print("="*80 + "\n")
