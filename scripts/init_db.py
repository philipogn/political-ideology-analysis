from services.ingestion.db import engine
from services.ingestion.models import Base

Base.metadata.create_all(bind=engine)
print('Database initialised.')

