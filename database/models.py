"""
SQLAlchemy models for central storage of analyses and recommendations.
"""
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, Integer, JSON, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class StockAnalysisModel(Base):
    __tablename__ = "stock_analyses"
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), index=True, nullable=False)
    company_name = Column(String(255))
    source = Column(String(50), index=True, nullable=False)
    fundamental_score = Column(Float)
    technical_score = Column(Float)
    sentiment_score = Column(Float)
    analyst_rating = Column(String(50))
    ai_rating = Column(Float)
    raw_data = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow)


class RecommendationModel(Base):
    __tablename__ = "recommendations"
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), index=True, nullable=False)
    company_name = Column(String(255))
    entry_price = Column(Float, nullable=False)
    stop_loss = Column(Float, nullable=False)
    take_profit = Column(Float, nullable=False)
    risk_reward_ratio = Column(String(20))
    composite_score = Column(Float)
    holding_period = Column(String(30))
    sources = Column(JSON)  # list of source names
    expected_return_pct = Column(Float)
    position_risk_pct = Column(Float)
    support_level = Column(Float)
    resistance_level = Column(Float)
    atr = Column(Float)
    published_at = Column(DateTime, default=datetime.utcnow, index=True)


class RecommendationPerformanceModel(Base):
    __tablename__ = "recommendation_performance"
    id = Column(Integer, primary_key=True, autoincrement=True)
    recommendation_id = Column(Integer, index=True)
    symbol = Column(String(20), index=True)
    return_pct = Column(Float)
    hit = Column(Integer)  # 1 if return > 0
    tracked_at = Column(DateTime, default=datetime.utcnow)
