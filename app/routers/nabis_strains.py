from typing import Annotated, List, Optional
from fastapi import APIRouter, FastAPI, Depends, Query, HTTPException
from sqlmodel import Field, Session, SQLModel, create_engine, select
from contextlib import asynccontextmanager
from pydantic import BaseModel
from datetime import datetime

class Strain(SQLModel, table=True):
    __tablename__ = "nabis_strains"
    __table_args__ = {"schema": "public"}
    
    strain_id: str | None = Field(default=None, primary_key=True)
    strain_name: str = Field(index=True)
    type: str 
    description: str
    abbreviation: str
    indica_percentage: int
    sativa_percentage: int
    thc_level: int
    cbd_level: int
    veg_length_days: int
    flower_length_day: int
    active: bool
    
   
class Meta(BaseModel):
    total: int
    offset: int
    limit: int
    count: int
    next: str

class StrainResponse(BaseModel):
    message: str
    status: int
    meta: Meta
    data: List[Strain]

class SingleStrainResponse(BaseModel):
    message: str
    status: int
    data: List[Strain]

router = APIRouter()

# PostgreSQL connection settings
POSTGRES_USER = "postgres"
POSTGRES_PASSWORD = "Aawesome7"
POSTGRES_HOST = "localhost"
POSTGRES_PORT = "5432"
POSTGRES_DB = "inventory"

# PostgreSQL connection URL
DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

# Create engine
engine = create_engine(DATABASE_URL)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

router = APIRouter(lifespan=lifespan)

@router.get("/nabis/strains/", response_model=StrainResponse, tags=["nabis_strains"], operation_id="get_nabis_strains")
def get_strains(
    session: SessionDep,
    offset: int = 0,
    limit: int = 50
) -> StrainResponse:
    """
    Get a list of all Nabis strains with pagination support.
    
    Args:
        session: Database session
        offset: Number of records to skip (default: 0)
        limit: Maximum number of records to return (default: 50)
        
    Returns:
        StrainResponse: List of strains with pagination metadata
    """
    # Get total count
    total = session.exec(select(Strain)).all()
    total_count = len(total)
    
    # Get paginated results with ordering
    strains = session.exec(
        select(Strain)
        .order_by(Strain.strain_id.asc())
        .offset(offset)
        .limit(limit)
    ).all()
    
    return StrainResponse(
        message="Success",
        status=200,
        meta=Meta(
            total=total_count,
            offset=offset,
            limit=limit,
            count=len(strains),
            next=""
        ),
        data=strains
    )

@router.get("/nabis/strains/{strain_id}", response_model=SingleStrainResponse, tags=["nabis_strains"], operation_id="get_nabis_strain_by_id")
def get_strain_by_id(strain_id: str, session: SessionDep) -> SingleStrainResponse:
    """
    Get a single Nabis strain by its ID.
    
    Args:
        strain_id: The unique identifier of the strain
        session: Database session
        
    Returns:
        SingleStrainResponse: The requested strain
        
    Raises:
        HTTPException: If the strain is not found
    """
    strain = session.get(Strain, strain_id)
    if not strain:
        raise HTTPException(status_code=404, detail="Strain not found")
    
    return SingleStrainResponse(
        message="Success",
        status=200,
        data=[strain]
    )


@router.post("/nabis/strains/", response_model=SingleStrainResponse, tags=["nabis_strains"], operation_id="post_nabis_strain")
def post_strain(strain: Strain, session: SessionDep) -> SingleStrainResponse:
    """
    Create a new Nabis strain.
    
    Args:
        strain: The strain to create
        session: Database session
        
    Returns:
        SingleStrainResponse: The created strain
    """
    session.add(strain)
    session.commit()
    session.refresh(strain)
    return SingleStrainResponse(
        message="Success",
        status=200,
        data=[strain]
    )


