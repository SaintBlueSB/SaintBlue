# config.py
import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///:memory:")  # Usando SQLite em memória para simplicidade
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY", "uma_chave_secreta_muito_segura") # Mantenha sua chave secreta aqui