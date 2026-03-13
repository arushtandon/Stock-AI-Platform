"""
Repository: persist and query analyses and recommendations.
"""
from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from config import DATABASE_URL
from core.schemas import StockAnalysis, StockRecommendation, DataSource
from database.models import Base, StockAnalysisModel, RecommendationModel

# SQLite for dev (no psycopg2 needed); PostgreSQL for production
if DATABASE_URL.startswith("sqlite"):
    _engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
else:
    _engine = create_engine(DATABASE_URL)

Base.metadata.create_all(_engine)
Session = sessionmaker(bind=_engine, autoflush=True)


def save_analyses(analyses: List[StockAnalysis]) -> int:
    session = Session()
    try:
        for a in analyses:
            m = StockAnalysisModel(
                symbol=a.symbol,
                company_name=a.company_name,
                source=a.source.value,
                fundamental_score=a.fundamental_score,
                technical_score=a.technical_score,
                sentiment_score=a.sentiment_score,
                analyst_rating=a.analyst_rating,
                ai_rating=a.ai_rating,
                raw_data=a.raw_data,
                timestamp=a.timestamp,
            )
            session.add(m)
        session.commit()
        return len(analyses)
    finally:
        session.close()


def save_recommendations(recommendations: List[StockRecommendation]) -> int:
    session = Session()
    try:
        for r in recommendations:
            m = RecommendationModel(
                symbol=r.symbol,
                company_name=r.company_name,
                entry_price=r.entry_price,
                stop_loss=r.stop_loss,
                take_profit=r.take_profit,
                risk_reward_ratio=r.risk_reward_ratio,
                composite_score=r.composite_score,
                holding_period=r.holding_period.value,
                sources=r.sources,
                expected_return_pct=r.expected_return_pct,
                position_risk_pct=r.position_risk_pct,
                support_level=r.support_level,
                resistance_level=r.resistance_level,
                atr=r.atr,
                published_at=r.timestamp,
            )
            session.add(m)
        session.commit()
        return len(recommendations)
    finally:
        session.close()


def get_latest_recommendations(
    since: Optional[datetime] = None,
    limit: int = 20,
) -> List[dict]:
    session = Session()
    try:
        q = session.query(RecommendationModel).order_by(RecommendationModel.published_at.desc())
        if since:
            q = q.filter(RecommendationModel.published_at >= since)
        rows = q.limit(limit).all()
        return [
            {
                "symbol": r.symbol,
                "company_name": r.company_name,
                "entry_price": r.entry_price,
                "stop_loss": r.stop_loss,
                "take_profit": r.take_profit,
                "risk_reward_ratio": r.risk_reward_ratio,
                "composite_score": r.composite_score,
                "holding_period": r.holding_period,
                "sources": r.sources or [],
                "expected_return_pct": r.expected_return_pct,
                "position_risk_pct": r.position_risk_pct,
                "support_level": r.support_level,
                "resistance_level": r.resistance_level,
                "published_at": r.published_at.isoformat() if r.published_at else None,
            }
            for r in rows
        ]
    finally:
        session.close()
