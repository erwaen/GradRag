from pydantic import BaseModel, HttpUrl

class Papers(BaseModel):
    ai: int = 0
    vision: int = 0
    mlmining: int = 0
    nlp: int = 0
    inforet: int = 0
    arch: int = 0
    comm: int = 0
    sec: int = 0
    mod: int = 0
    da: int = 0
    bed: int = 0
    hpc: int = 0
    mobile: int = 0
    metrics: int = 0
    ops: int = 0
    plan: int = 0
    soft: int = 0
    act: int = 0
    crypt: int = 0
    log: int = 0
    graph: int = 0
    bio: int = 0
    csed: int = 0
    ecom: int = 0
    chi: int = 0
    robotics: int = 0
    visualization: int = 0

class Advisor(BaseModel):
    name: str
    # href: HttpUrl
    href: str
    papers: Papers

class Rankings(BaseModel):
    ai: int = 0
    vision: int = 0
    mlmining: int = 0
    nlp: int = 0
    inforet: int = 0
    arch: int = 0
    comm: int = 0
    sec: int = 0
    mod: int = 0
    da: int = 0
    bed: int = 0
    hpc: int = 0
    mobile: int = 0
    metrics: int = 0
    ops: int = 0
    plan: int = 0
    soft: int = 0
    act: int = 0
    crypt: int = 0
    log: int = 0
    graph: int = 0
    bio: int = 0
    csed: int = 0
    ecom: int = 0
    chi: int = 0
    robotics: int = 0
    visualization: int = 0

class University(BaseModel):
    name: str
    rankings: Rankings
    advisors: list[Advisor] = []

class DataModel(BaseModel):
    universities: list[University] = []
    
