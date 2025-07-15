from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from . import crud, schemas
from .database import get_db

app = FastAPI(
    title="Kara Solutions - Medical Insights API",
    description="Provides analytical insights from Telegram channel data."
)

@app.get("/api/reports/top-products", response_model=List[schemas.ProductMention])
def read_top_products(limit: int = 10, db: Session = Depends(get_db)):
    """
    Returns the top N most frequently mentioned product keywords across all channels.
    This is a simple word count and serves as a proxy for product popularity.
    """
    return crud.get_top_products(db=db, limit=limit)

@app.get("/api/channels/{channel_name}/activity", response_model=schemas.ChannelActivity)
def read_channel_activity(channel_name: str, db: Session = Depends(get_db)):
    """
    Returns the total posting activity for a specific channel.
    """
    activity = crud.get_channel_activity(db=db, channel_name=channel_name)
    if not activity:
        raise HTTPException(status_code=404, detail="Channel not found or no activity.")
    return activity

@app.get("/api/search/messages", response_model=List[schemas.Message])
def read_search_results(query: str, db: Session = Depends(get_db)):
    """
    Searches for messages containing a specific keyword (case-insensitive).
    Useful for finding mentions of a specific drug like 'Paracetamol'.
    """
    return crud.search_messages(db=db, keyword=query)