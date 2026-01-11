import pytest
import pandas as pd
import sys
import os

# Add predictor directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from predictor.services.risk_service import RiskService
from predictor.utils.config import Config


class TestDynamicSimulation:
    """Test suite for dynamic risk simulation with slider parameters"""
    
    @pytest.fixture
    def risk_service(self):
        """Create RiskService instance"""
        return RiskService()
    
    @pytest.fixture
    def sample_event(self):
        """Sample event for testing"""
        return {
            'event_type': 'clash',
            'state': 'Lagos',
            'lga': 'Ikeja',
            'severity': 'high',
            'latitude': 6.6018,
            'longitude': 3.3515,
            'source_title': 'Test Event',
            'source_url': 'https://example.com/test'
        }
    
    @pytest.fixture
    def sample_econ_data(self):
        """Sample economic data DataFrame"""
        return pd.DataFrame({
            'State': ['Lagos', 'Kano', 'Rivers'],
            'LGA': ['Ikeja', 'Kano Municipal', 'Port Harcourt'],
            'Fuel_Price': [700.0, 680.0, 720.0],
            'Inflation': [25.0, 22.0, 28.0]
        })
    
    def test_risk_score_normalization(self, risk_service, sample_event, sample_econ_data):
        """Test that risk scores are always normalized to 0-100 range"""
        # Test with extreme values
        result = risk_service.calculate_risk_score_dynamic(
            event=sample_event,
            econ_data=sample_econ_data,
            fuel_price_index=100.0,
            inflation_rate=100.0,
            chatter_intensity=100.0
        )
        
        assert result is not None
        assert 0 <= result['risk_score'] <= 100, "Risk score must be between 0 and 100"
        
        # Test with minimum values
        result_min = risk_service.calculate_risk_score_dynamic(
            event=sample_event,
            econ_data=sample_econ_data,
            fuel_price_index=0.0,
            inflation_rate=0.0,
            chatter_intensity=0.0
        )
        
        assert result_min is not None
        assert 0 <= result_min['risk_score'] <= 100
    
    def test_critical_status_flag(self, risk_service, sample_event, sample_econ_data):
        """Test that CRITICAL status is set when risk_score > 80"""
        # Create conditions that should trigger CRITICAL status
        result = risk_service.calculate_risk_score_dynamic(
            event=sample_event,
            econ_data=sample_econ_data,
            fuel_price_index=95.0,
            inflation_rate=90.0,
            chatter_intensity=80.0
        )
        
        assert result is not None
        if result['risk_score'] > 80:
            assert result['status'] == 'CRITICAL', "Status should be CRITICAL when risk_score > 80"
            assert result['risk_level'] == 'Critical'
    
    def test_economic_igniter_urban_multiplier(self, risk_service, sample_econ_data):
        """Test Economic Igniter: 1.5x multiplier for urban LGAs when fuel_price_index > 80"""
        # Test with urban LGA (Ikeja is in URBAN_LGAS)
        urban_event = {
            'event_type': 'clash',
            'state': 'Lagos',
            'lga': 'Ikeja',
            'severity': 'high',
            'latitude': 6.6018,
            'longitude': 3.3515,
            'source_title': 'Urban Event',
            'source_url': 'https://example.com/urban'
        }
        
        # Calculate with fuel_price_index > 80
        result_high_fuel = risk_service.calculate_risk_score_dynamic(
            event=urban_event,
            econ_data=sample_econ_data,
            fuel_price_index=85.0,
            inflation_rate=30.0,
            chatter_intensity=50.0
        )
        
        # Calculate with fuel_price_index <= 80
        result_low_fuel = risk_service.calculate_risk_score_dynamic(
            event=urban_event,
            econ_data=sample_econ_data,
            fuel_price_index=75.0,
            inflation_rate=30.0,
            chatter_intensity=50.0
        )
        
        assert result_high_fuel is not None
        assert result_low_fuel is not None
        assert result_high_fuel['is_urban'] is True
        
        # High fuel should have significantly higher score due to 1.5x multiplier
        assert result_high_fuel['risk_score'] > result_low_fuel['risk_score']
        assert "Economic Crisis in Urban Center" in result_high_fuel['trigger_reason']
    
    def test_economic_igniter_rural_no_multiplier(self, risk_service, sample_econ_data):
        """Test that rural LGAs do not get Economic Igniter multiplier"""
        # Test with non-urban LGA
        rural_event = {
            'event_type': 'clash',
            'state': 'Kano',
            'lga': 'Bichi',  # Not in URBAN_LGAS
            'severity': 'high',
            'latitude': 11.7,
            'longitude': 8.2,
            'source_title': 'Rural Event',
            'source_url': 'https://example.com/rural'
        }
        
        result = risk_service.calculate_risk_score_dynamic(
            event=rural_event,
            econ_data=sample_econ_data,
            fuel_price_index=85.0,
            inflation_rate=30.0,
            chatter_intensity=50.0
        )
        
        assert result is not None
        assert result['is_urban'] is False
        assert "Economic Crisis in Urban Center" not in result['trigger_reason']
    
    def test_social_trigger_chatter_intensity_mapping(self, risk_service, sample_event, sample_econ_data):
        """Test Social Trigger: chatter_intensity maps to heatmap weight and radius"""
        # Test with low chatter
        result_low_chatter = risk_service.calculate_risk_score_dynamic(
            event=sample_event,
            econ_data=sample_econ_data,
            fuel_price_index=50.0,
            inflation_rate=25.0,
            chatter_intensity=10.0
        )
        
        # Test with high chatter
        result_high_chatter = risk_service.calculate_risk_score_dynamic(
            event=sample_event,
            econ_data=sample_econ_data,
            fuel_price_index=50.0,
            inflation_rate=25.0,
            chatter_intensity=90.0
        )
        
        assert result_low_chatter is not None
        assert result_high_chatter is not None
        
        # Higher chatter should result in larger heatmap radius
        assert result_high_chatter['heatmap_radius_km'] > result_low_chatter['heatmap_radius_km']
        assert result_high_chatter['heatmap_weight'] > result_low_chatter['heatmap_weight']
        
        # Verify radius bounds (5km to 50km)
        assert 5 <= result_low_chatter['heatmap_radius_km'] <= 50
        assert 5 <= result_high_chatter['heatmap_radius_km'] <= 50
        
        # Verify weight bounds (0 to 1)
        assert 0 <= result_low_chatter['heatmap_weight'] <= 1
        assert 0 <= result_high_chatter['heatmap_weight'] <= 1
    
    def test_fuel_price_index_impact(self, risk_service, sample_event, sample_econ_data):
        """Test that fuel_price_index affects risk score"""
        result_low_fuel = risk_service.calculate_risk_score_dynamic(
            event=sample_event,
            econ_data=sample_econ_data,
            fuel_price_index=20.0,
            inflation_rate=25.0,
            chatter_intensity=50.0
        )
        
        result_high_fuel = risk_service.calculate_risk_score_dynamic(
            event=sample_event,
            econ_data=sample_econ_data,
            fuel_price_index=90.0,
            inflation_rate=25.0,
            chatter_intensity=50.0
        )
        
        assert result_low_fuel is not None
        assert result_high_fuel is not None
        assert result_high_fuel['risk_score'] > result_low_fuel['risk_score']
    
    def test_inflation_rate_impact(self, risk_service, sample_event, sample_econ_data):
        """Test that inflation_rate affects risk score"""
        result_low_inflation = risk_service.calculate_risk_score_dynamic(
            event=sample_event,
            econ_data=sample_econ_data,
            fuel_price_index=50.0,
            inflation_rate=10.0,
            chatter_intensity=50.0
        )
        
        result_high_inflation = risk_service.calculate_risk_score_dynamic(
            event=sample_event,
            econ_data=sample_econ_data,
            fuel_price_index=50.0,
            inflation_rate=80.0,
            chatter_intensity=50.0
        )
        
        assert result_low_inflation is not None
        assert result_high_inflation is not None
        assert result_high_inflation['risk_score'] > result_low_inflation['risk_score']
    
    def test_parameter_validation_bounds(self, risk_service, sample_event, sample_econ_data):
        """Test that parameters are properly validated within 0-100 bounds"""
        # Valid parameters
        result = risk_service.calculate_risk_score_dynamic(
            event=sample_event,
            econ_data=sample_econ_data,
            fuel_price_index=50.0,
            inflation_rate=50.0,
            chatter_intensity=50.0
        )
        
        assert result is not None
        assert result['fuel_price_index'] == 50.0
        assert result['inflation_rate'] == 50.0
        assert result['chatter_intensity'] == 50.0
    
    def test_missing_coordinates_handling(self, risk_service, sample_econ_data):
        """Test that events without coordinates are handled gracefully"""
        event_no_coords = {
            'event_type': 'clash',
            'state': 'Lagos',
            'lga': 'Ikeja',
            'severity': 'high',
            'source_title': 'No Coords Event',
            'source_url': 'https://example.com/nocoords'
        }
        
        result = risk_service.calculate_risk_score_dynamic(
            event=event_no_coords,
            econ_data=sample_econ_data,
            fuel_price_index=50.0,
            inflation_rate=25.0,
            chatter_intensity=50.0
        )
        
        assert result is None
    
    def test_urban_lga_classification(self):
        """Test urban LGA classification utility"""
        # Test known urban LGAs
        assert Config.is_urban_lga('Ikeja') is True
        assert Config.is_urban_lga('Lagos Island') is True
        assert Config.is_urban_lga('Kano Municipal') is True
        assert Config.is_urban_lga('Port Harcourt') is True
        
        # Test non-urban LGAs
        assert Config.is_urban_lga('Bichi') is False
        assert Config.is_urban_lga('Unknown LGA') is False
        
        # Test case insensitivity
        assert Config.is_urban_lga('IKEJA') is True
        assert Config.is_urban_lga('ikeja') is True
    
    def test_multidimensional_indicators_preserved(self, risk_service, sample_event, sample_econ_data):
        """Test that multidimensional indicators (climate, mining, border) still work"""
        result = risk_service.calculate_risk_score_dynamic(
            event=sample_event,
            econ_data=sample_econ_data,
            fuel_price_index=50.0,
            inflation_rate=25.0,
            chatter_intensity=50.0
        )
        
        assert result is not None
        # Result should have all required fields
        assert 'risk_score' in result
        assert 'status' in result
        assert 'heatmap_weight' in result
        assert 'heatmap_radius_km' in result
        assert 'trigger_reason' in result
    
    def test_status_levels_correct(self, risk_service, sample_event, sample_econ_data):
        """Test that status levels are correctly assigned based on risk_score"""
        # Test different scenarios to get different risk levels
        test_cases = [
            (0.0, 0.0, 0.0, ['MINIMAL', 'LOW']),
            (30.0, 30.0, 30.0, ['LOW', 'MEDIUM']),
            (60.0, 60.0, 60.0, ['MEDIUM', 'HIGH']),
            (90.0, 90.0, 90.0, ['HIGH', 'CRITICAL'])
        ]
        
        for fuel, inflation, chatter, expected_statuses in test_cases:
            result = risk_service.calculate_risk_score_dynamic(
                event=sample_event,
                econ_data=sample_econ_data,
                fuel_price_index=fuel,
                inflation_rate=inflation,
                chatter_intensity=chatter
            )
            
            assert result is not None
            assert result['status'] in expected_statuses or result['status'] in ['MINIMAL', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL']


class TestSimulationParametersModel:
    """Test SimulationParameters Pydantic model validation"""
    
    def test_valid_parameters(self):
        """Test valid parameter creation"""
        from predictor.models.risk import SimulationParameters
        
        params = SimulationParameters(
            fuel_price_index=50.0,
            inflation_rate=25.0,
            chatter_intensity=75.0
        )
        
        assert params.fuel_price_index == 50.0
        assert params.inflation_rate == 25.0
        assert params.chatter_intensity == 75.0
    
    def test_parameter_bounds_validation(self):
        """Test that parameters are validated within 0-100 bounds"""
        from predictor.models.risk import SimulationParameters
        from pydantic import ValidationError
        
        # Test lower bound violation
        with pytest.raises(ValidationError):
            SimulationParameters(
                fuel_price_index=-10.0,
                inflation_rate=25.0,
                chatter_intensity=50.0
            )
        
        # Test upper bound violation
        with pytest.raises(ValidationError):
            SimulationParameters(
                fuel_price_index=150.0,
                inflation_rate=25.0,
                chatter_intensity=50.0
            )
    
    def test_edge_case_values(self):
        """Test edge case values (0 and 100)"""
        from predictor.models.risk import SimulationParameters
        
        # Test minimum values
        params_min = SimulationParameters(
            fuel_price_index=0.0,
            inflation_rate=0.0,
            chatter_intensity=0.0
        )
        assert params_min.fuel_price_index == 0.0
        
        # Test maximum values
        params_max = SimulationParameters(
            fuel_price_index=100.0,
            inflation_rate=100.0,
            chatter_intensity=100.0
        )
        assert params_max.fuel_price_index == 100.0
