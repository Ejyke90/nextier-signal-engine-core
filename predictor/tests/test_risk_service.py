import pytest
import pandas as pd
from unittest.mock import patch
from predictor.services.risk_service import RiskService
from predictor.models import RiskSignal


class TestRiskService:
    """Test cases for RiskService"""
    
    @pytest.fixture
    def risk_service(self):
        """Create RiskService instance for testing"""
        return RiskService()
    
    @pytest.fixture
    def sample_economic_data(self):
        """Sample economic data for testing"""
        return pd.DataFrame([
            {"State": "Lagos", "LGA": "Ikeja", "Fuel_Price": 700, "Inflation": 22},
            {"State": "Lagos", "LGA": "Victoria Island", "Fuel_Price": 650, "Inflation": 18},
            {"State": "Abuja", "LGA": "Maitama", "Fuel_Price": 680, "Inflation": 20}
        ])
    
    @pytest.fixture
    def sample_event(self):
        """Sample event for testing"""
        return {
            "event_type": "clash",
            "state": "Lagos",
            "lga": "Ikeja",
            "severity": "high",
            "source_title": "Test Article",
            "source_url": "https://test.com/article"
        }
    
    def test_find_economic_data_exact_match(self, risk_service, sample_economic_data):
        """Test finding economic data with exact match"""
        event = {"state": "Lagos", "lga": "Ikeja"}
        
        result = risk_service.find_economic_data(event, sample_economic_data)
        
        assert result is not None
        assert result["fuel_price"] == 700.0
        assert result["inflation"] == 22.0
    
    def test_find_economic_data_state_match_only(self, risk_service, sample_economic_data):
        """Test finding economic data with state match only"""
        event = {"state": "Lagos", "lga": "UnknownLGA"}
        
        result = risk_service.find_economic_data(event, sample_economic_data)
        
        assert result is not None
        # Should return first Lagos entry
        assert result["fuel_price"] == 700.0
        assert result["inflation"] == 22.0
    
    def test_find_economic_data_no_match(self, risk_service, sample_economic_data):
        """Test finding economic data with no match"""
        event = {"state": "UnknownState", "lga": "UnknownLGA"}
        
        result = risk_service.find_economic_data(event, sample_economic_data)
        
        assert result is None
    
    def test_calculate_risk_score_clash_high_inflation(self, risk_service, sample_economic_data, sample_event):
        """Test risk calculation for clash event with high inflation"""
        result = risk_service.calculate_risk_score(sample_event, sample_economic_data)
        
        assert result is not None
        assert isinstance(result, RiskSignal)
        assert result.event_type == "clash"
        assert result.state == "Lagos"
        assert result.lga == "Ikeja"
        assert result.severity == "high"
        assert result.fuel_price == 700.0
        assert result.inflation == 22.0
        assert result.risk_score >= 81  # Special rule for clash + high inflation
        assert result.risk_level == "Critical"
    
    def test_calculate_risk_score_low_risk_event(self, risk_service, sample_economic_data):
        """Test risk calculation for low risk event"""
        event = {
            "event_type": "sports",
            "state": "Lagos",
            "lga": "Victoria Island",
            "severity": "low",
            "source_title": "Sports Article",
            "source_url": "https://test.com/sports"
        }
        
        result = risk_service.calculate_risk_score(event, sample_economic_data)
        
        assert result is not None
        assert result.event_type == "sports"
        assert result.risk_score < 50  # Should be low risk
        assert result.risk_level in ["Minimal", "Low"]
    
    def test_calculate_risk_score_no_economic_data(self, risk_service, sample_event):
        """Test risk calculation with no economic data"""
        empty_df = pd.DataFrame()
        
        result = risk_service.calculate_risk_score(sample_event, empty_df)
        
        assert result is None
    
    def test_calculate_risk_score_economic_modifiers(self, risk_service, sample_economic_data):
        """Test economic modifiers in risk calculation"""
        event = {
            "event_type": "conflict",
            "state": "Lagos",
            "lga": "Ikeja",
            "severity": "medium",
            "source_title": "Conflict Article",
            "source_url": "https://test.com/conflict"
        }
        
        result = risk_service.calculate_risk_score(event, sample_economic_data)
        
        assert result is not None
        # Base score (30) + event_type (35) + severity (10) + inflation bonus (>20%)
        assert result.risk_score > 75
    
    def test_calculate_risk_score_bounds(self, risk_service, sample_economic_data):
        """Test risk score bounds (0-100)"""
        # Test very high risk scenario
        high_risk_event = {
            "event_type": "clash",
            "state": "Lagos",
            "lga": "Ikeja",
            "severity": "critical",
            "source_title": "High Risk Article",
            "source_url": "https://test.com/high"
        }
        
        result = risk_service.calculate_risk_score(high_risk_event, sample_economic_data)
        
        assert result is not None
        assert result.risk_score <= 100
        assert result.risk_score >= 0
    
    def test_calculate_risk_scores_batch(self, risk_service, sample_economic_data):
        """Test batch risk calculation"""
        events = [
            {
                "event_type": "clash",
                "state": "Lagos",
                "lga": "Ikeja",
                "severity": "high",
                "source_title": "Article 1",
                "source_url": "https://test.com/1"
            },
            {
                "event_type": "sports",
                "state": "Lagos",
                "lga": "Victoria Island",
                "severity": "low",
                "source_title": "Article 2",
                "source_url": "https://test.com/2"
            },
            {
                "event_type": "unknown",
                "state": "UnknownState",
                "lga": "UnknownLGA",
                "severity": "unknown",
                "source_title": "Article 3",
                "source_url": "https://test.com/3"
            }
        ]
        
        results = risk_service.calculate_risk_scores_batch(events, sample_economic_data)
        
        assert len(results) == 2  # Only 2 should have economic data
        assert all(isinstance(result, RiskSignal) for result in results)
        
        # Check that clash event has higher risk than sports event
        clash_risk = next(r for r in results if r.event_type == "clash")
        sports_risk = next(r for r in results if r.event_type == "sports")
        assert clash_risk.risk_score > sports_risk.score
    
    def test_risk_level_determination(self, risk_service, sample_economic_data):
        """Test risk level determination based on score"""
        test_cases = [
            ({"event_type": "clash", "severity": "critical"}, "Critical"),
            ({"event_type": "conflict", "severity": "high"}, "High"),
            ({"event_type": "protest", "severity": "medium"}, "Medium"),
            ({"event_type": "sports", "severity": "low"}, "Low"),
        ]
        
        for event_data, expected_level in test_cases:
            event = {
                **event_data,
                "state": "Lagos",
                "lga": "Ikeja",
                "source_title": "Test",
                "source_url": "https://test.com"
            }
            
            result = risk_service.calculate_risk_score(event, sample_economic_data)
            
            assert result is not None
            assert result.risk_level == expected_level


class TestRiskSignalModel:
    """Test cases for RiskSignal model"""
    
    def test_risk_signal_model_valid(self):
        """Test valid RiskSignal model creation"""
        signal = RiskSignal(
            event_type="clash",
            state="Lagos",
            lga="Ikeja",
            severity="high",
            fuel_price=700.0,
            inflation=22.0,
            risk_score=85.5,
            risk_level="Critical",
            source_title="Test Article",
            source_url="https://test.com/article"
        )
        
        assert signal.event_type == "clash"
        assert signal.state == "Lagos"
        assert signal.lga == "Ikeja"
        assert signal.severity == "high"
        assert signal.fuel_price == 700.0
        assert signal.inflation == 22.0
        assert signal.risk_score == 85.5
        assert signal.risk_level == "Critical"
        assert signal.source_title == "Test Article"
        assert signal.source_url == "https://test.com/article"
        assert signal.calculated_at is not None
    
    def test_risk_signal_model_invalid_risk_score(self):
        """Test RiskSignal model with invalid risk score"""
        with pytest.raises(ValueError):
            RiskSignal(
                event_type="clash",
                state="Lagos",
                lga="Ikeja",
                severity="high",
                fuel_price=700.0,
                inflation=22.0,
                risk_score=150.0,  # Above 100
                risk_level="Critical",
                source_title="Test Article",
                source_url="https://test.com/article"
            )
    
    def test_risk_signal_model_invalid_risk_level(self):
        """Test RiskSignal model with invalid risk level"""
        with pytest.raises(ValueError):
            RiskSignal(
                event_type="clash",
                state="Lagos",
                lga="Ikeja",
                severity="high",
                fuel_price=700.0,
                inflation=22.0,
                risk_score=85.5,
                risk_level="Invalid",  # Invalid risk level
                source_title="Test Article",
                source_url="https://test.com/article"
            )
