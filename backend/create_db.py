
from app.database import engine, Base
import app.models as models

Base.metadata.create_all(bind=engine)
print("DB initialized (dev.db)")

