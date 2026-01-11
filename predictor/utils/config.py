import os
from typing import Optional


class Config:
    # Database configuration
    MONGODB_URL: str = os.getenv('MONGODB_URL', 'mongodb://admin:password@mongodb:27017/')
    MONGODB_DATABASE: str = os.getenv('MONGODB_DATABASE', 'nextier_signal')
    
    # RabbitMQ configuration
    RABBITMQ_URL: str = os.getenv('RABBITMQ_URL', 'amqp://admin:password@rabbitmq:5672/')
    RABBITMQ_QUEUE_EVENTS: str = os.getenv('RABBITMQ_QUEUE_EVENTS', 'parsed_events')
    RABBITMQ_QUEUE_SIGNALS: str = os.getenv('RABBITMQ_QUEUE_SIGNALS', 'risk_signals')
    
    # Processing configuration
    POLL_INTERVAL: int = int(os.getenv('POLL_INTERVAL', '30'))
    MAX_CONCURRENT_PROCESSING: int = int(os.getenv('MAX_CONCURRENT_PROCESSING', '5'))
    
    # Risk scoring configuration
    BASE_RISK_SCORE: int = int(os.getenv('BASE_RISK_SCORE', '30'))
    INFLATION_THRESHOLD: float = float(os.getenv('INFLATION_THRESHOLD', '20.0'))
    FUEL_PRICE_THRESHOLD: float = float(os.getenv('FUEL_PRICE_THRESHOLD', '650.0'))
    
    # CORS configuration
    ALLOWED_ORIGINS: list = os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000,http://localhost:8080,https://nextier.example.com').split(',')
    
    # Service configuration
    SERVICE_NAME: str = os.getenv('SERVICE_NAME', 'predictor')
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    
    # Urban LGA classification for Economic Igniter (major Nigerian cities)
    URBAN_LGAS: set = {
        # Lagos State
        'ikeja', 'lagos island', 'lagos mainland', 'surulere', 'eti-osa', 'apapa',
        'kosofe', 'oshodi-isolo', 'alimosho', 'ajeromi-ifelodun', 'mushin',
        # Abuja FCT
        'abuja municipal', 'gwagwalada', 'kuje', 'abaji', 'bwari', 'kwali',
        # Kano State
        'kano municipal', 'nassarawa', 'fagge', 'dala', 'gwale', 'tarauni',
        # Rivers State (Port Harcourt)
        'port harcourt', 'obio-akpor', 'eleme', 'okrika',
        # Kaduna State
        'kaduna north', 'kaduna south', 'chikun', 'igabi',
        # Oyo State (Ibadan)
        'ibadan north', 'ibadan south-west', 'ibadan north-east', 'ibadan south-east', 'ibadan north-west',
        # Enugu State
        'enugu north', 'enugu south', 'enugu east',
        # Anambra State (Onitsha, Awka)
        'onitsha north', 'onitsha south', 'awka north', 'awka south',
        # Delta State (Warri, Asaba)
        'warri south', 'warri north', 'warri south-west', 'oshimili south',
        # Edo State (Benin City)
        'oredo', 'egor', 'ikpoba-okha',
        # Abia State (Aba, Umuahia)
        'aba north', 'aba south', 'umuahia north', 'umuahia south',
        # Plateau State (Jos)
        'jos north', 'jos south', 'jos east',
        # Benue State (Makurdi)
        'makurdi',
        # Cross River State (Calabar)
        'calabar municipal', 'calabar south',
        # Akwa Ibom State (Uyo)
        'uyo',
        # Bauchi State
        'bauchi',
        # Borno State (Maiduguri)
        'maiduguri',
        # Gombe State
        'gombe',
        # Imo State (Owerri)
        'owerri municipal', 'owerri north', 'owerri west',
        # Kwara State (Ilorin)
        'ilorin west', 'ilorin east', 'ilorin south',
        # Niger State (Minna)
        'minna',
        # Ondo State (Akure)
        'akure south', 'akure north',
        # Osun State (Osogbo)
        'osogbo',
        # Ogun State (Abeokuta)
        'abeokuta south', 'abeokuta north',
        # Sokoto State
        'sokoto north', 'sokoto south',
        # Yobe State (Damaturu)
        'damaturu',
        # Zamfara State (Gusau)
        'gusau'
    }
    
    @classmethod
    def is_urban_lga(cls, lga: str) -> bool:
        """Check if an LGA is classified as urban"""
        return lga.lower().strip() in cls.URBAN_LGAS
    
    @classmethod
    def validate(cls) -> bool:
        """Validate configuration parameters"""
        required_vars = [
            'MONGODB_URL',
            'RABBITMQ_URL'
        ]
        
        for var in required_vars:
            if not getattr(cls, var):
                raise ValueError(f"Required environment variable {var} is not set")
        
        return True
