# src/detection/__init__.py
from flask import Blueprint

detection_bp = Blueprint('detection_bp', __name__)

from src.detection import controllers