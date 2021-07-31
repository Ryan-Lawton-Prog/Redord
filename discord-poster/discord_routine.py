from flask import Flask, request, Response, Blueprint
from flask_accept import accept

from config import MongoDataBase
import os

DB = MongoDataBase()
datasets = DB.get_collection("datasets")
models = DB.get_collection("models")

