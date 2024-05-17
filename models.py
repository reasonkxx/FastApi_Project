from sqlalchemy import Column, Integer, String, Time, ForeignKey, create_engine
from sqlalchemy.orm import relationship, Session, declarative_base
from sqlalchemy.orm import sessionmaker


Base = declarative_base()

class Train(Base):
    __tablename__ = 'trains'
    TrainID = Column(Integer, primary_key=True)  # SQLAlchemy автоматически обрабатывает автоинкремент
    TrainName = Column(String(100), nullable=False)
    TrainType = Column(String(50), nullable=False)

    # Встановлення зв'язку з розкладами
    schedules = relationship('Schedule', back_populates='train')


class Station(Base):
    __tablename__ = 'stations'
    
    StationID = Column(Integer, primary_key=True, index=True)
    StationName = Column(String(100), nullable=False)
    Location = Column(String(255), nullable=False)

    # Встановлення зв'язків з маршрутами
    origin_routes = relationship('Route', foreign_keys='[Route.OriginStationID]', back_populates='origin_station')
    destination_routes = relationship('Route', foreign_keys='[Route.DestinationStationID]', back_populates='destination_station')


class Route(Base):
    __tablename__ = 'routes'
    
    RouteID = Column(Integer, primary_key=True, index=True)
    OriginStationID = Column(Integer, ForeignKey('stations.StationID'), nullable=False)
    DestinationStationID = Column(Integer, ForeignKey('stations.StationID'), nullable=False)

    # Встановлення зв'язку зі станціями
    origin_station = relationship('Station', foreign_keys=[OriginStationID], back_populates='origin_routes')
    destination_station = relationship('Station', foreign_keys=[DestinationStationID], back_populates='destination_routes')

    # Встановлення зв'язку з розкладами
    schedules = relationship('Schedule', back_populates='route')


class Schedule(Base):
    __tablename__ = 'schedules'
    
    ScheduleID = Column(Integer, primary_key=True, index=True)
    TrainID = Column(Integer, ForeignKey('trains.TrainID'), nullable=False)
    RouteID = Column(Integer, ForeignKey('routes.RouteID'), nullable=False)
    DepartureTime = Column(Time, nullable=False)
    ArrivalTime = Column(Time, nullable=False)

    # Встановлення зв'язків з потягами та маршрутами
    train = relationship('Train', back_populates='schedules')
    route = relationship('Route', back_populates='schedules')

# Створення двигуна та сесії
engine = create_engine("mssql+pyodbc://admin:123456789@MYCOMPUTER\\MSSQLSERVER1/TrainRoutes?driver=SQL+Server", echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# # Створення таблиць у базі даних
# Base.metadata.create_all(bind=engine)

# Функція для залежності отримання сесії БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()