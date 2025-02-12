from app.db.database import Base
from app.models.user import User
from app.models.petition import Petition
from sqlalchemy.orm import relationship

User.petitions = relationship("Petition", back_populates="user")
