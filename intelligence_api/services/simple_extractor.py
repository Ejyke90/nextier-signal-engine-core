"""
Simple rule-based event extractor for Nigerian conflict news
Fallback when LLM is unavailable or returns invalid data
"""
import re
from typing import Dict, Any, Optional
from datetime import datetime

# Nigerian states with coordinates (capital city coordinates)
STATE_COORDINATES = {
    'abia': {'lat': 5.4527, 'lng': 7.5248},
    'adamawa': {'lat': 9.3265, 'lng': 12.3984},
    'akwa ibom': {'lat': 5.0077, 'lng': 7.8536},
    'anambra': {'lat': 6.2209, 'lng': 6.9370},
    'bauchi': {'lat': 10.3158, 'lng': 9.8442},
    'bayelsa': {'lat': 4.7719, 'lng': 6.0699},
    'benue': {'lat': 7.7347, 'lng': 8.5378},
    'borno': {'lat': 11.8333, 'lng': 13.1500},
    'cross river': {'lat': 4.9609, 'lng': 8.3417},
    'delta': {'lat': 5.8904, 'lng': 5.6804},
    'ebonyi': {'lat': 6.2649, 'lng': 8.0137},
    'edo': {'lat': 6.3350, 'lng': 5.6037},
    'ekiti': {'lat': 7.7190, 'lng': 5.3110},
    'enugu': {'lat': 6.5244, 'lng': 7.5106},
    'gombe': {'lat': 10.2897, 'lng': 11.1689},
    'imo': {'lat': 5.4840, 'lng': 7.0351},
    'jigawa': {'lat': 12.2230, 'lng': 9.5619},
    'kaduna': {'lat': 10.5105, 'lng': 7.4165},
    'kano': {'lat': 12.0022, 'lng': 8.5920},
    'katsina': {'lat': 12.9908, 'lng': 7.6177},
    'kebbi': {'lat': 12.4539, 'lng': 4.1975},
    'kogi': {'lat': 7.7333, 'lng': 6.7333},
    'kwara': {'lat': 8.4966, 'lng': 4.5426},
    'lagos': {'lat': 6.5244, 'lng': 3.3792},
    'nasarawa': {'lat': 8.5400, 'lng': 8.3100},
    'niger': {'lat': 9.6139, 'lng': 6.5569},
    'ogun': {'lat': 6.9082, 'lng': 3.3470},
    'ondo': {'lat': 7.2571, 'lng': 5.2058},
    'osun': {'lat': 7.5629, 'lng': 4.5200},
    'oyo': {'lat': 7.8451, 'lng': 3.9318},
    'plateau': {'lat': 9.2182, 'lng': 9.5179},
    'rivers': {'lat': 4.8156, 'lng': 7.0498},
    'sokoto': {'lat': 13.0622, 'lng': 5.2339},
    'taraba': {'lat': 7.9897, 'lng': 10.7739},
    'yobe': {'lat': 12.2941, 'lng': 11.9661},
    'zamfara': {'lat': 12.1704, 'lng': 6.6594},
    'fct': {'lat': 9.0765, 'lng': 7.3986},
    'abuja': {'lat': 9.0765, 'lng': 7.3986}
}

NIGERIAN_STATES = set(STATE_COORDINATES.keys())

# Conflict-related keywords
CONFLICT_KEYWORDS = {
    'clash': ['clash', 'clashes', 'fighting', 'battle', 'combat'],
    'protest': ['protest', 'demonstration', 'rally', 'march'],
    'attack': ['attack', 'attacked', 'assault', 'raid', 'strike'],
    'kidnapping': ['kidnap', 'abduct', 'hostage'],
    'banditry': ['bandit', 'bandits', 'armed gang'],
    'terrorism': ['boko haram', 'iswap', 'terrorist', 'insurgent'],
    'communal': ['communal', 'ethnic', 'tribal'],
    'violence': ['violence', 'violent', 'killing', 'killed', 'death']
}

def extract_state(text: str) -> Optional[str]:
    """Extract Nigerian state from text"""
    text_lower = text.lower()
    for state in NIGERIAN_STATES:
        if state in text_lower:
            return state.title()
    return "Nigeria"  # Default if no state found

def extract_event_type(text: str) -> str:
    """Extract event type from text using keywords"""
    text_lower = text.lower()
    
    for event_type, keywords in CONFLICT_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text_lower:
                return event_type
    
    return "conflict"  # Default event type

def extract_severity(text: str) -> str:
    """Determine severity based on keywords"""
    text_lower = text.lower()
    
    # Critical indicators
    if any(word in text_lower for word in ['killed', 'death', 'massacre', 'slaughter', 'bomb']):
        return "critical"
    
    # High indicators
    if any(word in text_lower for word in ['injured', 'wounded', 'attack', 'assault', 'kidnap']):
        return "high"
    
    # Medium indicators
    if any(word in text_lower for word in ['protest', 'clash', 'tension']):
        return "medium"
    
    return "low"

def extract_lga(text: str, state: str) -> str:
    """Extract LGA (Local Government Area) from text"""
    # Common LGAs for major states
    lga_patterns = {
        'Lagos': ['ikeja', 'surulere', 'lagos island', 'eti-osa', 'alimosho'],
        'Borno': ['maiduguri', 'bama', 'gwoza', 'konduga'],
        'Kaduna': ['kaduna north', 'kaduna south', 'zaria', 'kafanchan'],
        'Kano': ['kano municipal', 'nassarawa', 'fagge'],
        'Rivers': ['port harcourt', 'obio-akpor', 'eleme'],
        'Plateau': ['jos north', 'jos south', 'barkin ladi'],
        'Abuja': ['abuja municipal', 'gwagwalada', 'bwari']
    }
    
    text_lower = text.lower()
    
    # Try to find LGA for the state
    if state in lga_patterns:
        for lga in lga_patterns[state]:
            if lga in text_lower:
                return lga.title()
    
    # Default to state capital or "Unknown"
    return f"{state} Central"

def simple_extract_event(article: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Extract event data from article using simple rules
    
    Args:
        article: Article dictionary with title and content
    
    Returns:
        Event dictionary or None if not conflict-related or invalid
    """
    try:
        # VALIDATE INPUT TYPE
        if not isinstance(article, dict):
            logger.warning("Invalid article type", type=type(article).__name__)
            return None
        
        # VALIDATE REQUIRED FIELDS
        title = article.get('title', '')
        content = article.get('content', '')
        url = article.get('url', '')
        
        if not title or not isinstance(title, str):
            logger.warning("Missing or invalid title", url=url)
            return None
            
        if not content or not isinstance(content, str):
            logger.warning("Missing or invalid content", url=url)
            return None
        
        # VALIDATE MINIMUM LENGTH
        if len(title) < 10:
            logger.debug("Title too short", title_length=len(title), url=url)
            return None
            
        if len(content) < 50:
            logger.debug("Content too short", content_length=len(content), url=url)
            return None
        
        combined_text = f"{title} {content}"
        
        # Check if article is conflict-related
        is_conflict = any(
            keyword in combined_text.lower()
            for keywords in CONFLICT_KEYWORDS.values()
            for keyword in keywords
        )
        
        if not is_conflict:
            return None
        
        # Extract event details
        state = extract_state(combined_text)
        event_type = extract_event_type(combined_text)
        severity = extract_severity(combined_text)
        lga = extract_lga(combined_text, state)
        
        # Get coordinates for the state
        coords = STATE_COORDINATES.get(state.lower(), STATE_COORDINATES.get('abuja'))
        
        event = {
            'event_type': event_type,
            'state': state,
            'lga': lga,
            'severity': severity,
            'source_title': title[:200],  # Limit length
            'source_url': article.get('url', ''),
            'parsed_at': datetime.now().isoformat(),
            'latitude': coords['lat'],
            'longitude': coords['lng']
        }
        
        return event
        
    except Exception as e:
        return None
