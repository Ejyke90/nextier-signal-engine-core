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
        self.climate_indicators = self._load_climate_indicators_geojson()
        self.mining_data = self._load_mining_data()
        self.border_data = self._load_border_data()
        self.strategic_indicators = self._load_strategic_indicators()
        self.previous_risk_scores = {}  # For surge detection
        
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
    
    def _load_climate_indicators_geojson(self) -> Dict[str, Any]:
        """Load climate stress zones from GeoJSON file"""
        try:
            data_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'climate_indicators.geojson')
            with open(data_path, 'r') as f:
                geojson_data = json.load(f)
                logger.info(f"Loaded {len(geojson_data.get('features', []))} climate stress zones")
                return geojson_data
        except Exception as e:
            logger.warning(f"Could not load climate indicators GeoJSON: {e}")
            return {'type': 'FeatureCollection', 'features': []}
    
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
    
    def _load_strategic_indicators(self) -> pd.DataFrame:
        """Load strategic indicators CSV with normalized state-level data"""
        try:
            data_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'nigeria_econ_indicators.csv')
            df = pd.read_csv(data_path)
            logger.info(f"Loaded strategic indicators for {len(df)} states")
            return df
        except Exception as e:
            logger.warning(f"Could not load strategic indicators: {e}")
            return pd.DataFrame()
    
    def get_strategic_indicators(self, state: str) -> Optional[Dict[str, float]]:
        """Get strategic indicators for a given state"""
        try:
            if self.strategic_indicators.empty:
                return None
            
            state_data = self.strategic_indicators[
                self.strategic_indicators['state'].str.lower() == state.lower()
            ]
            
            if state_data.empty:
                logger.warning(f"No strategic indicators found for state: {state}")
                return None
            
            row = state_data.iloc[0]
            return {
                'poverty_rate': float(row['poverty_rate']),
                'inflation_rate': float(row['inflation_rate']),
                'unemployment': float(row['unemployment']),
                'mining_density': float(row['mining_density']),
                'climate_vulnerability': float(row['climate_vulnerability']),
                'migration_pressure': float(row['migration_pressure'])
            }
        except Exception as e:
            logger.error(f"Error getting strategic indicators: {e}")
            return None
    
    def _haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points in kilometers using Haversine formula"""
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        km = 6371 * c
        return km
    
    def _point_in_polygon(self, lat: float, lon: float, polygon_coords: List[List[float]]) -> bool:
        """Check if a point is inside a polygon using ray casting algorithm"""
        inside = False
        n = len(polygon_coords)
        
        for i in range(n):
            j = (i - 1) % n
            xi, yi = polygon_coords[i][0], polygon_coords[i][1]
            xj, yj = polygon_coords[j][0], polygon_coords[j][1]
            
            intersect = ((yi > lat) != (yj > lat)) and (lon < (xj - xi) * (lat - yi) / (yj - yi) + xi)
            if intersect:
                inside = not inside
        
        return inside
    
    def calculate_climate_risk(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Calculate climate risk for an event based on climate stress zones
        
        Returns:
            Dict with climate risk data if event is in a climate stress zone, None otherwise
        """
        try:
            latitude = event.get('latitude')
            longitude = event.get('longitude')
            
            if not latitude or not longitude:
                return None
            
            # Check each climate stress zone
            for feature in self.climate_indicators.get('features', []):
                geometry = feature.get('geometry', {})
                properties = feature.get('properties', {})
                
                if geometry.get('type') == 'Polygon':
                    # Get polygon coordinates (first ring for exterior)
                    polygon_coords = geometry.get('coordinates', [[]])[0]
                    
                    # Check if event is within this climate stress zone
                    if self._point_in_polygon(latitude, longitude, polygon_coords):
                        impact_zone = properties.get('impact_zone', 'Unknown')
                        recession_index = properties.get('recession_index', 0)
                        
                        return {
                            'in_climate_zone': True,
                            'region': properties.get('region', 'Unknown'),
                            'indicator': properties.get('indicator', 'Unknown'),
                            'recession_index': recession_index,
                            'impact_zone': impact_zone,
                            'conflict_correlation': properties.get('conflict_correlation', ''),
                            'is_high_impact': impact_zone == 'High'
                        }
            
            return None
            
        except Exception as e:
            logger.error(f"Error calculating climate risk: {e}")
            return None
    
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
    
    def detect_surge(self, state: str, lga: str, current_risk_score: float) -> Dict[str, Any]:
        """Detect if risk score has surged by >20% in current scrape window"""
        location_key = f"{state}:{lga}"
        surge_detected = False
        percentage_increase = 0.0
        previous_score = None
        
        if location_key in self.previous_risk_scores:
            previous_score = self.previous_risk_scores[location_key]
            percentage_increase = ((current_risk_score - previous_score) / previous_score) * 100
            
            if percentage_increase > 20:
                surge_detected = True
                logger.warning(
                    f"SURGE DETECTED: {state}/{lga} risk increased by {percentage_increase:.1f}% "
                    f"({previous_score:.1f} -> {current_risk_score:.1f})"
                )
        
        # Update tracking
        self.previous_risk_scores[location_key] = current_risk_score
        
        return {
            'surge_detected': surge_detected,
            'percentage_increase': round(percentage_increase, 1),
            'previous_score': previous_score,
            'current_score': current_risk_score
        }
    
    def is_farmer_herder_conflict(self, event: Dict[str, Any]) -> bool:
        """Determine if event is a Farmer-Herder conflict based on keywords"""
        text_to_check = (
            event.get('source_title', '') + ' ' + 
            event.get('content', '') + ' ' + 
            event.get('event_type', '')
        ).lower()
        
        farmer_herder_keywords = [
            'farmer', 'herder', 'herdsmen', 'fulani', 'pastoralist',
            'cattle', 'grazing', 'farmland', 'crop', 'livestock',
            'communal clash', 'land dispute'
        ]
        
        return any(keyword in text_to_check for keyword in farmer_herder_keywords)
    
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
    
    # Map event types to categories and confidence scores
    def get_category_confidence(self, event_type: str) -> tuple[str, int]:
        """Map event type to category and confidence score"""
        event_type_lower = event_type.lower()
        
        category_mapping = {
            'clash': ('Organized Banditry', 94),
            'attack': ('Organized Banditry', 91),
            'kidnapping': ('Kidnapping-for-Ransom', 87),
            'protest': ('Sectarian Insurgency', 78),
            'vandalism': ('Organized Banditry', 82),
            'robbery': ('Organized Banditry', 89),
            'bombing': ('Sectarian Insurgency', 93),
            'terrorism': ('Sectarian Insurgency', 95),
            'farmer_herder': ('Farmer-Herder Clashes', 92),
            'communal': ('Farmer-Herder Clashes', 88),
            'ethnic': ('Sectarian Insurgency', 85),
            'religious': ('Sectarian Insurgency', 86)
        }
        
        return category_mapping.get(event_type_lower, ('Unknown', 0))

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
            
            # === STRATEGIC DEEP INDICATORS ===
            
            # Get state-level strategic indicators
            strategic_data = self.get_strategic_indicators(state)
            climate_vulnerability = None
            mining_density = None
            migration_pressure = None
            poverty_rate = None
            
            if strategic_data:
                climate_vulnerability = strategic_data['climate_vulnerability']
                mining_density = strategic_data['mining_density']
                migration_pressure = strategic_data['migration_pressure']
                poverty_rate = strategic_data['poverty_rate']
            
            # === MULTIDIMENSIONAL INDICATORS ===
            
            # 1. CLIMATE STRESS MULTIPLIER: Using climate_vulnerability from strategic indicators
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
            
            # DEEP INDICATOR: Climate Stress Multiplier
            if climate_vulnerability and climate_vulnerability > 0.7:
                climate_stress_bonus = climate_vulnerability * 15  # Up to 15 points
                base_score += climate_stress_bonus
                trigger_reasons.append(
                    f"High Climate Vulnerability ({climate_vulnerability*100:.0f}%) - "
                    f"environmental stress amplifies conflict risk"
                )
                logger.info(f"Climate stress multiplier applied: +{climate_stress_bonus:.1f} points")
            
            # 2. FUNDING RISK MULTIPLIER: Illicit economic activity using mining_density
            mining_site = self.find_nearest_mining_site(event)
            mining_proximity = None
            mining_site_name = None
            high_funding_potential = False
            high_escalation_potential = False
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
            
            # DEEP INDICATOR: Funding Risk Multiplier using mining_density
            if mining_density and mining_density > 0.6:
                funding_risk_bonus = mining_density * 20  # Up to 20 points
                base_score += funding_risk_bonus
                high_escalation_potential = True
                trigger_reasons.append(
                    f"High Escalation Potential due to Illicit Funding - "
                    f"Mining density {mining_density*100:.0f}% enables armed group financing"
                )
                logger.info(f"Funding risk multiplier applied: +{funding_risk_bonus:.1f} points")
            
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
            
            # DEEP INDICATOR: Farmer-Herder Conflict Logic with Migration Pressure
            is_farmer_herder = self.is_farmer_herder_conflict(event)
            if is_farmer_herder and migration_pressure and migration_pressure > 0.5:
                migration_multiplier = 1 + migration_pressure  # 1.5x to 2.0x multiplier
                original_score = base_score
                base_score = base_score * migration_multiplier
                trigger_reasons.append(
                    f"Farmer-Herder Conflict amplified by Migration Pressure ({migration_pressure*100:.0f}%) - "
                    f"pastoralist displacement intensifies land competition"
                )
                logger.info(f"Farmer-Herder multiplier applied: {original_score:.1f} -> {base_score:.1f}")
            
            # === CLIMATE-CONFLICT CORRELATION ===
            # Calculate climate risk using GeoJSON climate stress zones
            climate_risk = self.calculate_climate_risk(event)
            climate_zone_region = None
            climate_recession_index = None
            climate_conflict_driver = None
            
            if climate_risk and climate_risk.get('in_climate_zone'):
                climate_zone_region = climate_risk.get('region')
                climate_recession_index = climate_risk.get('recession_index', 0)
                impact_zone = climate_risk.get('impact_zone')
                conflict_correlation = climate_risk.get('conflict_correlation', '')
                
                # If event occurs in High impact zone, increase risk score and tag as Environmental/Climate
                if climate_risk.get('is_high_impact'):
                    climate_bonus = 25  # Significant boost for High impact zones
                    base_score += climate_bonus
                    climate_conflict_driver = 'Environmental/Climate'
                    trigger_reasons.append(
                        f"Climate Stress Zone: {climate_zone_region} (Recession Index: {climate_recession_index:.2f}) - "
                        f"{conflict_correlation}"
                    )
                    logger.info(f"Climate-Conflict correlation applied: +{climate_bonus} points in {climate_zone_region}")
                elif impact_zone in ['Medium-High', 'Medium']:
                    climate_bonus = 15
                    base_score += climate_bonus
                    climate_conflict_driver = 'Environmental/Climate'
                    trigger_reasons.append(
                        f"Climate Stress Zone: {climate_zone_region} ({impact_zone} impact) - {conflict_correlation}"
                    )
            
            # Ensure score is within bounds
            risk_score = max(0, min(100, base_score))
            
            # DEEP INDICATOR: Surge Detection (>20% increase in 15-min window)
            surge_info = self.detect_surge(state, lga, risk_score)
            surge_detected = surge_info['surge_detected']
            percentage_increase = surge_info['percentage_increase']
            
            if surge_detected:
                trigger_reasons.append(
                    f"⚠️ SURGE ALERT: Risk increased by {percentage_increase:.1f}% in last 15 minutes - "
                    f"rapid escalation detected"
                )
            
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
            
            # Build comprehensive trigger reason with strategic tags
            if trigger_reasons:
                trigger_reason = f"{risk_level} Risk: " + "; ".join(trigger_reasons)
            else:
                trigger_reason = f"{risk_level} Risk: Standard risk calculation based on {event_type} event"
            
            # Add strategic tags
            if high_escalation_potential:
                trigger_reason = "[HIGH ESCALATION POTENTIAL] " + trigger_reason
            
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
                sophisticated_ied_usage=sophisticated_ied,
                # Strategic Deep Indicators
                climate_vulnerability=climate_vulnerability,
                mining_density=mining_density,
                migration_pressure=migration_pressure,
                poverty_rate=poverty_rate,
                high_escalation_potential=high_escalation_potential,
                is_farmer_herder_conflict=is_farmer_herder,
                surge_detected=surge_detected,
                surge_percentage_increase=percentage_increase if surge_detected else None,
                # Climate-Conflict Correlation Fields
                climate_zone_region=climate_zone_region,
                climate_recession_index=climate_recession_index,
                climate_impact_zone=impact_zone,
                climate_conflict_correlation=climate_risk.get('conflict_correlation') if climate_risk else None,
                conflict_driver=climate_conflict_driver
            )
            
        except Exception as e:
            logger.error("Error calculating risk score", error=str(e))
            return None
    
    def calculate_risk_score_dynamic(
        self, 
        event: Dict[str, Any], 
        econ_data: pd.DataFrame,
        fuel_price_index: float,
        inflation_rate: float,
        chatter_intensity: float
    ) -> Optional[Dict[str, Any]]:
        """
        Calculate dynamic risk score for simulation with slider parameters.
        
        Args:
            event: Event data dictionary
            econ_data: Economic data DataFrame
            fuel_price_index: Fuel price crisis index (0-100)
            inflation_rate: Inflation rate percentage (0-100)
            chatter_intensity: Social media chatter intensity (0-100)
        
        Returns:
            Dictionary with risk score, status, heatmap_weight, and all event data
        """
        try:
            event_type = event.get('event_type', '').lower()
            state = event.get('state', '').strip()
            lga = event.get('lga', '').strip()
            severity = event.get('severity', '').lower()
            latitude = event.get('latitude')
            longitude = event.get('longitude')
            
            if not latitude or not longitude:
                logger.warning("Event missing coordinates", state=state, lga=lga)
                return None
            
            trigger_reasons = []
            
            # Base risk score calculation
            base_score = Config.BASE_RISK_SCORE
            
            # Event type modifiers
            base_score += self.event_type_scores.get(event_type, 15)
            
            # Severity modifiers
            base_score += self.severity_modifiers.get(severity, 5)
            
            # DYNAMIC ECONOMIC MODIFIERS (from sliders)
            # Map inflation_rate slider (0-100) to actual inflation percentage
            actual_inflation = inflation_rate
            if actual_inflation > Config.INFLATION_THRESHOLD:
                inflation_bonus = min((actual_inflation - Config.INFLATION_THRESHOLD) * 2, 20)
                base_score += inflation_bonus
                trigger_reasons.append(f"High inflation ({actual_inflation:.1f}%)")
            
            # Map fuel_price_index slider (0-100) to fuel price impact
            # Scale: 0-100 index maps to 0-20 bonus points
            fuel_bonus = (fuel_price_index / 100) * 20
            base_score += fuel_bonus
            if fuel_price_index > 50:
                trigger_reasons.append(f"Elevated fuel prices (index: {fuel_price_index:.0f}/100)")
            
            # === MULTIDIMENSIONAL INDICATORS ===
            
            # 1. CLIMATE MULTIPLIER
            climate_data = self.find_climate_data(state, lga)
            flood_inundation = None
            
            if climate_data:
                flood_inundation = climate_data.get('flood_inundation_index', 0)
                
                if flood_inundation > 20 and event_type in ['clash', 'conflict', 'violence']:
                    base_score = base_score * 1.5
                    trigger_reasons.append(
                        f"Flooding-induced displacement ({flood_inundation:.1f}% inundated)"
                    )
            
            # 2. MINING MULTIPLIER
            mining_site = self.find_nearest_mining_site(event)
            mining_proximity = None
            
            if mining_site:
                mining_proximity = mining_site.get('distance_km')
                
                if mining_proximity and mining_proximity < 10:
                    base_score += 15
                    trigger_reasons.append(
                        f"High Funding Potential ({mining_proximity:.1f}km from mining)"
                    )
            
            # 3. SAHELIAN MULTIPLIER
            border_data = self.find_border_data(state, lga)
            
            if border_data:
                border_activity = border_data.get('border_activity')
                
                if border_activity == 'High' and state.lower() in ['sokoto', 'kebbi']:
                    base_score += 20
                    trigger_reasons.append("Lakurawa Presence Detected")
                elif border_activity == 'Critical':
                    base_score += 15
                    trigger_reasons.append("Critical border activity")
                elif border_activity == 'High':
                    base_score += 10
                    trigger_reasons.append("High border activity")
            
            # === ECONOMIC IGNITER: Urban LGA Multiplier ===
            # If fuel_price_index > 80, apply 1.5x multiplier to urban LGAs
            is_urban = Config.is_urban_lga(lga)
            if fuel_price_index > 80 and is_urban:
                original_score = base_score
                base_score = base_score * 1.5
                trigger_reasons.append(
                    f"Economic Crisis in Urban Center (fuel index: {fuel_price_index:.0f}) - "
                    f"1.5x multiplier applied"
                )
                logger.info(f"Economic Igniter activated: {original_score} -> {base_score} for {lga}")
            
            # Normalize to 0-100 range
            risk_score = max(0, min(100, base_score))
            
            # Determine risk level and status
            if risk_score >= 80:
                risk_level = "Critical"
                status = "CRITICAL"
            elif risk_score >= 60:
                risk_level = "High"
                status = "HIGH"
            elif risk_score >= 40:
                risk_level = "Medium"
                status = "MEDIUM"
            elif risk_score >= 20:
                risk_level = "Low"
                status = "LOW"
            else:
                risk_level = "Minimal"
                status = "MINIMAL"
            
            # === SOCIAL TRIGGER: Map chatter_intensity to heatmap weight ===
            # chatter_intensity (0-100) directly influences the heatmap radius/weight
            # Higher chatter = larger heat zone radius
            # Base radius: 5km, Max radius: 50km
            base_radius_km = 5
            max_radius_km = 50
            heatmap_radius_km = base_radius_km + (chatter_intensity / 100) * (max_radius_km - base_radius_km)
            
            # Weight for heatmap intensity (0-1 scale)
            heatmap_weight = min(1.0, (risk_score / 100) * (1 + chatter_intensity / 100))
            
            # Build trigger reason
            if trigger_reasons:
                trigger_reason = f"{risk_level} Risk: " + "; ".join(trigger_reasons)
            else:
                trigger_reason = f"{risk_level} Risk: Standard calculation"
            
            # Get category and confidence based on event type
            category, confidence = self.get_category_confidence(event.get('event_type', 'unknown'))
            
            return {
                'event_type': event.get('event_type', 'unknown'),
                'state': state,
                'lga': lga,
                'severity': severity,
                'latitude': latitude,
                'longitude': longitude,
                'risk_score': round(risk_score, 1),
                'risk_level': risk_level,
                'status': status,
                'category': category,
                'confidence': confidence,
                'source_title': event.get('source_title', ''),
                'source_url': event.get('source_url', ''),
                'trigger_reason': trigger_reason,
                'heatmap_weight': round(heatmap_weight, 3),
                'heatmap_radius_km': round(heatmap_radius_km, 1),
                'is_urban': is_urban,
                'fuel_price_index': fuel_price_index,
                'inflation_rate': inflation_rate,
                'chatter_intensity': chatter_intensity,
                'calculated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error("Error in dynamic risk calculation", error=str(e))
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
