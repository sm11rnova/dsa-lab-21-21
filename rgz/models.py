# импортирую необходимые компоненты из sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, BigInteger, Date, Numeric, ForeignKey

# создаю базовый класс для моделей
Base = declarative_base()

# определяю модель пользователя
class User(Base):
    # указываю имя таблицы в бд
    __tablename__ = "users"
    
    # создаю поле id как первичный ключ
    id = Column(Integer, primary_key=True)
    
    # создаю поле для имени пользователя (обязательное)
    name = Column(String, nullable=False)
    
    # создаю поле для chat_id (уникальное и обязательное)
    chat_id = Column(BigInteger, unique=True, nullable=False)

# определяю модель операции
class Operation(Base):
    # указываю имя таблицы в бд
    __tablename__ = "operations"
    
    # создаю поле id как первичный ключ
    id = Column(Integer, primary_key=True)
    
    # создаю поле для даты операции (обязательное)
    date = Column(Date, nullable=False)
    
    # создаю поле для суммы операции (обязательное)
    sum = Column(Numeric, nullable=False)
    
    # создаю поле для связи с пользователем (внешний ключ)
    chat_id = Column(BigInteger, ForeignKey("users.chat_id"), nullable=False)
    
    # создаю поле для типа операции (обязательное)
    type_operation = Column(String, nullable=False)