from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class BusinessType(db.Model):
    """Тип бизнеса"""
    __tablename__ = 'business_types'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    base_price = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

class BusinessSize(db.Model):
    """Размер бизнеса"""
    __tablename__ = 'business_sizes'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    multiplier = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

class Feature(db.Model):
    """Дополнительные функции/услуги"""
    __tablename__ = 'features'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

class Article(db.Model):
    """Статья базы знаний"""
    __tablename__ = 'articles'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(255), nullable=True)
    date = db.Column(db.String(50), nullable=True)  # Форматированная дата для отображения
    featured = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

class Example(db.Model):
    """Пример успешного бизнес-проекта"""
    __tablename__ = 'examples'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    business_type = db.Column(db.String(100), nullable=False)
    investment = db.Column(db.Integer, nullable=False)
    profit = db.Column(db.Integer, nullable=False)
    period = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

class Message(db.Model):
    """Сообщение от пользователя"""
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    response = db.Column(db.Text, nullable=True)  # Текст ответа
    response_sent_at = db.Column(db.DateTime, nullable=True)  # Дата отправки ответа
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

class User(db.Model):
    """Пользователь системы"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

class BusinessPlan(db.Model):
    """Созданный бизнес-план"""
    __tablename__ = 'business_plans'
    
    id = db.Column(db.Integer, primary_key=True)
    business_type_id = db.Column(db.Integer, db.ForeignKey('business_types.id'), nullable=False)
    business_size_id = db.Column(db.Integer, db.ForeignKey('business_sizes.id'), nullable=False)
    total_price = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # Отношения
    business_type = db.relationship('BusinessType', backref=db.backref('plans', lazy=True))
    business_size = db.relationship('BusinessSize', backref=db.backref('plans', lazy=True))
    user = db.relationship('User', backref=db.backref('plans', lazy=True))
    features = db.relationship('Feature', secondary='plan_features', lazy='subquery',
                               backref=db.backref('plans', lazy=True))

# Промежуточная таблица для связи многие-ко-многим между бизнес-планами и функциями
plan_features = db.Table('plan_features',
    db.Column('plan_id', db.Integer, db.ForeignKey('business_plans.id'), primary_key=True),
    db.Column('feature_id', db.Integer, db.ForeignKey('features.id'), primary_key=True)
) 