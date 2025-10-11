from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List, Any
from sqlmodel import SQLModel, Session, select
from datetime import datetime

T = TypeVar('T', bound=SQLModel)


class BaseRepository(ABC, Generic[T]):
    """Base repository class with common CRUD operations"""
    
    def __init__(self, session: Session, model_class: type[T]):
        self.session = session
        self.model_class = model_class
    
    def create(self, obj_in: T) -> T:
        """Create a new object"""
        self.session.add(obj_in)
        self.session.commit()
        self.session.refresh(obj_in)
        return obj_in
    
    def get_by_id(self, id: int) -> Optional[T]:
        """Get object by ID"""
        return self.session.get(self.model_class, id)
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Get all objects with pagination"""
        statement = select(self.model_class).offset(skip).limit(limit)
        return list(self.session.exec(statement).all())
    
    def update(self, obj_in: T) -> T:
        """Update an existing object"""
        self.session.add(obj_in)
        self.session.commit()
        self.session.refresh(obj_in)
        return obj_in
    
    def delete(self, id: int) -> bool:
        """Delete object by ID"""
        obj = self.get_by_id(id)
        if obj:
            self.session.delete(obj)
            self.session.commit()
            return True
        return False
    
    def delete_object(self, obj: T) -> bool:
        """Delete an object instance"""
        if obj:
            self.session.delete(obj)
            self.session.commit()
            return True
        return False
    
    def count(self) -> int:
        """Count total number of objects"""
        statement = select(self.model_class)
        return len(list(self.session.exec(statement).all()))
    
    def exists(self, **filters) -> bool:
        """Check if object exists with given filters"""
        statement = select(self.model_class)
        for key, value in filters.items():
            statement = statement.where(getattr(self.model_class, key) == value)
        return self.session.exec(statement).first() is not None
