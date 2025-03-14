from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    google_id = db.Column(db.String(100), unique=True)
    email = db.Column(db.String(100))
    name = db.Column(db.String(100))
    picture = db.Column(db.String(500))  # URL to user's profile picture
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    bots = db.relationship("Bot", back_populates="user")
    chats = db.relationship("Chat", back_populates="user")

class Bot(db.Model):
    __tablename__ = 'bots'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    name = db.Column(db.String(100))
    model = db.Column(db.String(50))
    system_prompt = db.Column(db.Text)
    temperature = db.Column(db.String(10))
    top_p = db.Column(db.String(10))
    top_k = db.Column(db.String(10))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship("User", back_populates="bots")
    chats = db.relationship("Chat", back_populates="bot")

class Chat(db.Model):
    __tablename__ = 'chats'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    bot_id = db.Column(db.Integer, db.ForeignKey('bots.id'))
    title = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship("User", back_populates="chats")
    bot = db.relationship("Bot", back_populates="chats")
    messages = db.relationship("Message", back_populates="chat")

class Message(db.Model):
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, db.ForeignKey('chats.id'))
    role = db.Column(db.String(20))  # 'user' or 'assistant'
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    chat = db.relationship("Chat", back_populates="messages") 