from typing import Dict

def analyze_news_simple(symbol: str) -> Dict:
    """Simplified news analysis - less restrictive"""
    return {
        'impact': 'NEUTRAL',
        'sentiment_score': 0,
        'headlines': []
    }

def get_economic_calendar_light(config: dict) -> Dict:
    """Lighter economic calendar - don't block trading"""
    if config.get('current', {}).get('ignore_economic_calendar', False):
        return {
            'impact': 'LOW',
            'events': [],
            'should_reduce_confidence': False
        }
    
    return {
        'impact': 'MEDIUM',
        'events': ['Economic events not blocking trades'],
        'should_reduce_confidence': False
    }
