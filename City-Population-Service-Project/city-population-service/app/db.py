import os
import logging
from sqlalchemy import create_engine, Column, Integer, String, MetaData, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Base class for SQLAlchemy models
Base = declarative_base()

class City(Base):
    """City model for storing city name and population"""
    __tablename__ = 'cities'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    population = Column(Integer, nullable=False)

class MySQLClient:
    def __init__(self):
        # Get MySQL connection details from environment variables with defaults
        mysql_host = os.environ.get('MYSQL_HOST', 'localhost')
        mysql_port = os.environ.get('MYSQL_PORT', '3306')
        mysql_user = os.environ.get('MYSQL_USER', 'root')
        mysql_password = os.environ.get('MYSQL_PASSWORD', 'password')
        mysql_database = os.environ.get('MYSQL_DATABASE', 'citydb')
        
        # Build connection URL
        self.db_url = f"mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_database}"
        self.engine = None
        self.Session = None
        
    def connect(self):
        """Establish connection to MySQL database"""
        try:
            self.engine = create_engine(self.db_url)
            
            # Create tables if they don't exist
            Base.metadata.create_all(self.engine)
            
            # Create session factory
            self.Session = sessionmaker(bind=self.engine)
            
            logger.info("Connected to MySQL database")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to MySQL database: {str(e)}")
            return False
    
    def upsert_city(self, city_name, population):
        """Insert or update a city's population"""
        try:
            # Normalize city name to lowercase for consistency
            city_name = city_name.lower()
            
            session = self.Session()
            
            # Check if city exists
            city = session.query(City).filter(City.name == city_name).first()
            
            if city:
                # Update existing city
                city.population = population
                logger.info(f"Updated city: {city_name} with population: {population}")
            else:
                # Create new city
                city = City(name=city_name, population=population)
                session.add(city)
                logger.info(f"Created city: {city_name} with population: {population}")
            
            session.commit()
            session.close()
            return True
        except Exception as e:
            logger.error(f"Failed to upsert city: {str(e)}")
            session.rollback()
            session.close()
            return False
    
    def get_city_population(self, city_name):
        """Get a city's population"""
        try:
            # Normalize city name to lowercase for consistency
            city_name = city_name.lower()
            
            session = self.Session()
            
            # Get city by name
            city = session.query(City).filter(City.name == city_name).first()
            
            session.close()
            
            if city:
                return city.population
            return None
        except Exception as e:
            logger.error(f"Failed to get city population: {str(e)}")
            session.close()
            return None

# Create a singleton instance
db_client = MySQLClient()