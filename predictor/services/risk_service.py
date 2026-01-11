import pandas as pd
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional, List
from functools import lru_cache
from math import radians, cos, sin, asin, sqrt
from ..utils import get_logger, Config
from ..models import RiskSignal

logger = get_logger(__name__)


class RiskService:
    def __init__(self):
        self.climate_data = self._load_climate_data()
        self.mining_data = self._load_mining_data()
        self.border_data = self._load_border_data()
        
        self.event_type_scores = {
            'clash': 40,
            'conflict': 35,
            'violence': 30,
            'protest': 25,
            'political': 20,
            'security': 25,
            'crime': 20,
            'sports': 5,  # Low risk
            'economic': 15,
            'social': 10,
            'unknown': 15
        }
        
        self.severity_modifiers = {
            'high': 20,
            'severe': 25,
            'critical': 30,
            'medium': 10,
            'moderate': 8,
            'low': 5,
            'minor': 3,
            'unknown': 5
        }
    
    def _load_climate_data(self) -> List[Dict[str, Any]]:
        """Load climate indicators from JSON file"""
        try:
            data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'climate_data.json')
            with open(data_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load climate data: {e}")
            return []
    
    def _load_mining_data(self) -> List[Dict[str, Any]]:
        """Load mining activity data from JSON file"""
        try:
            data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'mining_activity.json')
            with open(data_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load mining data: {e}")
            return []
    
    def _load_border_data(self) -> List[Dict[str, Any]]:
        """Load border signals data from JSON file"""
        try:
            data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'border_signals.json')
            with open(data_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load border data: {e}")
            return []
    
    def _haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points in kilometers using Haversine formula"""
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        km = 6371 * c
        return km
    
    def find_climate_data(self, state: str, lga: str) -> Optional[Dict[str, Any]]:
        """Find climate indicators for a given location"""
        for climate in self.climate_data:
            if (climate['state'].lower() == state.lower() and 
                climate['lga'].lower() == lga.lower()):
                return climate
        return None
    
    def find_nearest_mining_site(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find nearest mining site to an event location"""
        event_lat = event.get('latitude')
        event_lon = event.get('longitude')
        
        if not event_lat or not event_lon:
            return None
        
        nearest_site = None
        min_distance = float('inf')
        
        for site in self.mining_data:
            distance = self._haversine_distance(
                event_lat, event_lon,
                site['latitude'], site['longitude']
            )
            if distance < min_distance:
                min_distance = distance
                nearest_site = {**site, 'distance_km': distance}
        
        return nearest_site
    
    def find_border_data(self, state: str, lga: str) -> Optional[Dict[str, Any]]:
        """Find border signals for a given location"""
        for border in self.border_data:
            if (border['state'].lower() == state.lower() and 
                border['lga'].lower() == lga.lower()):
                return border
        return None
    
    @lru_cache(maxsize=1000)
    def _get_economic_data_cache(self, state: str, lga: str, econ_data_hash: int) -> Optional[Dict[str, float]]:
        """Cache economic data lookups"""
        # This is a placeholder for caching logic
        # In practice, we'd cache the economic data lookup
        return None
    
    def find_economic_data(self, event: Dict[str, Any], econ_data: pd.DataFrame) -> Optional[Dict[str, float]]:
        """Find matching economic data for an event"""
        try:
            state = event.get('state', '').strip()
            lga = event.get('lga', '').strip()
            
            # Try exact match first
            econ_row = econ_data[
                (econ_data['State'].str.lower() == state.lower()) &
                (econ_data['LGA'].str.lower() == lga.lower())
            ]
            
            if econ_row.empty:
                # Try state-level match if LGA not found
                econ_row = econ_data[econ_data['State'].str.lower() == state.lower()]
            
            if econ_row.empty:
                logger.warning("No economic data found", state=state, lga=lga)
                return None
            
            econ_data_row = econ_row.iloc[0]
            return {
                'fuel_price': float(econ_data_row['Fuel_Price']),
                'inflation': float(econ_data_row['Inflation'])
            }
            
        except Exception as e:
            logger.error("Error finding economic data", error=str(e))
            return None
    
    def calculate_risk_score(self, event: Dict[str, Any], econ_data: pd.DataFrame) -> Optional[RiskSignal]:
        """
        Calculate risk score based on event type, economic indicators, and multidimensional factors
        Risk scoring algorithm:
        - Base score depends on event type and severity
        - Economic modifiers: inflation > 20% increases risk
        - Climate multiplier: flooding > 20% increases communal clash risk by 1.5x
        - Mining multiplier: proximity < 10km flags high funding potential
        - Sahelian multiplier: High border activity in Sokoto/Kebbi flags Lakurawa presence
        """
        try:
            event_type = event.get('event_type', '').lower()
            state = event.get('state', '').strip()
            lga = event.get('lga', '').strip()
            severity = event.get('severity', '').lower()
            
            # Find matching economic data
            economic_data = self.find_economic_data(event, econ_data)
            
            if not economic_data:
                logger.warning("No economic data available for risk calculation", 
                             state=state, lga=lga)
                return None
            
            fuel_price = economic_data['fuel_price']
            inflation = economic_data['inflation']
            
            # Initialize trigger reasons list
            trigger_reasons = []
            
            # Base risk score calculation
            base_score = Config.BASE_RISK_SCORE
            
            # Event type modifiers
            base_score += self.event_type_scores.get(event_type, 15)
            
            # Severity modifiers
            base_score += self.severity_modifiers.get(severity, 5)
            
            # Economic modifiers
            if inflation > Config.INFLATION_THRESHOLD:
                inflation_bonus = min((inflation - Config.INFLATION_THRESHOLD) * 2, 20)
                base_score += inflation_bonus
                trigger_reasons.append(f"High inflation ({inflation}%)")
            
            if fuel_price > Config.FUEL_PRICE_THRESHOLD:
                fuel_bonus = min((fuel_price - Config.FUEL_PRICE_THRESHOLD) * 0.1, 10)
                base_score += fuel_bonus
                trigger_reasons.append(f"Elevated fuel prices (₦{fuel_price})")
            
            # Special rule: clash events with inflation > threshold get > 80 risk score
            if event_type == 'clash' and inflation > Config.INFLATION_THRESHOLD:
                base_score = max(base_score, 81)
            
            # === MULTIDIMENSIONAL INDICATORS ===
            
            # 1. CLIMATE MULTIPLIER: Flooding-induced displacement
            climate_data = self.find_climate_data(state, lga)
            flood_inundation = None
            precipitation_anomaly = None
            vegetation_health = None
            
            if climate_data:
                flood_inundation = climate_data.get('flood_inundation_index', 0)
                precipitation_anomaly = climate_data.get('precipitation_anomaly', 0)
                vegetation_health = climate_data.get('vegetation_health_index', 0)
                
                # Flooding Multiplier: If flood_inundation > 20%, increase communal clash risk by 1.5x
                if flood_inundation > 20 and event_type in ['clash', 'conflict', 'violence']:
                    original_score = base_score
                    base_score = base_score * 1.5
                    trigger_reasons.append(
                        f"Flooding-induced displacement ({flood_inundation:.1f}% farmland inundated) - "
                        f"increased resource competition"
                    )
                    logger.info(f"Climate multiplier applied: {original_score} -> {base_score}")
            
            # 2. MINING MULTIPLIER: Illicit economic activity
            mining_site = self.find_nearest_mining_site(event)
            mining_proximity = None
            mining_site_name = None
            high_funding_potential = False
            informal_taxation = None
            
            if mining_site:
                mining_proximity = mining_site.get('distance_km')
                mining_site_name = mining_site.get('site_name')
                informal_taxation = mining_site.get('informal_taxation_rate')
                
                # Mining Multiplier: If event within 10km of mining site, flag high funding potential
                if mining_proximity and mining_proximity < 10:
                    high_funding_potential = True
                    base_score += 15
                    trigger_reasons.append(
                        f"High Funding Potential - Event within {mining_proximity:.1f}km of "
                        f"{mining_site_name} (informal taxation: {informal_taxation*100:.0f}%)"
                    )
                    logger.info(f"Mining multiplier applied: proximity {mining_proximity}km")
            
            # 3. SAHELIAN MULTIPLIER: Transnational jihadist expansion
            border_data = self.find_border_data(state, lga)
            border_activity = None
            lakurawa_presence = False
            border_permeability = None
            group_affiliation = None
            sophisticated_ied = False
            
            if border_data:
                border_activity = border_data.get('border_activity')
                lakurawa_presence = border_data.get('lakurawa_presence_confirmed', False)
                border_permeability = border_data.get('border_permeability_score')
                group_affiliation = border_data.get('group_affiliation')
                sophisticated_ied = border_data.get('sophisticated_ied_usage', False)
                
                # Sahelian Multiplier: High border activity in Sokoto/Kebbi flags Lakurawa presence
                if border_activity == 'High' and state.lower() in ['sokoto', 'kebbi']:
                    base_score += 20
                    trigger_reasons.append(
                        f"Lakurawa Presence Detected - Sahelian jihadist expansion from Niger border "
                        f"(border permeability: {border_permeability*100:.0f}%)"
                    )
                    logger.info(f"Sahelian multiplier applied: {state} border activity")
                elif border_activity == 'Critical':
                    base_score += 15
                    trigger_reasons.append(
                        f"Critical border activity - {group_affiliation} "
                        f"(permeability: {border_permeability*100:.0f}%)"
                    )
                elif border_activity == 'High':
                    base_score += 10
                    trigger_reasons.append(f"High border activity - {group_affiliation}")
            
            # Ensure score is within bounds
            risk_score = max(0, min(100, base_score))
            
            # Determine risk level
            if risk_score >= 80:
                risk_level = "Critical"
            elif risk_score >= 60:
                risk_level = "High"
            elif risk_score >= 40:
                risk_level = "Medium"
            elif risk_score >= 20:
                risk_level = "Low"
            else:
                risk_level = "Minimal"
            
            # Build comprehensive trigger reason
            if trigger_reasons:
                trigger_reason = f"{risk_level} Risk: " + "; ".join(trigger_reasons)
            else:
                trigger_reason = f"{risk_level} Risk: Standard risk calculation based on {event_type} event"
            
            return RiskSignal(
                event_type=event.get('event_type', 'unknown'),
                state=state,
                lga=lga,
                severity=event.get('severity', 'unknown'),
                fuel_price=fuel_price,
                inflation=inflation,
                risk_score=round(risk_score, 1),
                risk_level=risk_level,
                source_title=event.get('source_title', ''),
                source_url=event.get('source_url', ''),
                trigger_reason=trigger_reason,
                # Climate indicators
                flood_inundation_index=flood_inundation,
                precipitation_anomaly=precipitation_anomaly,
                vegetation_health_index=vegetation_health,
                # Mining indicators
                mining_proximity_km=mining_proximity,
                mining_site_name=mining_site_name,
                high_funding_potential=high_funding_potential,
                informal_taxation_rate=informal_taxation,
                # Border indicators
                border_activity=border_activity,
                lakurawa_presence=lakurawa_presence,
                border_permeability_score=border_permeability,
                group_affiliation=group_affiliation,
                sophisticated_ied_usage=sophisticated_ied
            )
            
        except Exception as e:
            logger.error("Error calculating risk score", error=str(e))
            return None
    
    def calculate_risk_scores_batch(self, events: List[Dict[str, Any]], econ_data: pd.DataFrame) -> List[RiskSignal]:
        """Calculate risk scores for multiple events"""
        try:
            risk_signals = []
            
            for event in events:
                try:
                    signal = self.calculate_risk_score(event, econ_data)
                    if signal:
                        risk_signals.append(signal)
                        logger.info("Calculated risk score", 
                                  score=signal.risk_score,
                                  event_type=signal.event_type,
                                  state=signal.state)
                    else:
                        logger.warning("Failed to calculate risk score", 
                                     title=event.get('source_title', 'Unknown'))
                        
                except Exception as e:
                    logger.error("Error processing event", 
                               url=event.get('source_url', 'unknown'), 
                               error=str(e))
                    continue
            
            logger.info("Completed risk calculation batch", 
                       total_events=len(events), 
                       successful=len(risk_signals))
            
            return risk_signals
            
        except Exception as e:
            logger.error("Error in risk calculation batch", error=str(e))
            return []
