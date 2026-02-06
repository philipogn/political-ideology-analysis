from sqlalchemy import select, and_, not_
from services.ingestion.db import session_local
from services.ingestion.models import Article, InferenceResult

def query_database(model_version, limit):
    session = session_local()
    # sub query to select existing rows with article id and model version 
    sub_query = (
        select(InferenceResult.article_id)
        .where(and_(
            InferenceResult.article_id == Article.article_id, 
            InferenceResult.model_version == model_version
        ))
        .exists()
    )

    # select rows of negated sub query
    stmt = (
        select(Article)
        .where(not_(sub_query))
        .order_by(Article.published_at.desc())
        .limit(limit)
    )

    result = session.execute(stmt).scalars().all()
    return result