import os
# ============================================================
# 設定
# ============================================================

class Config(object):
    # デバッグモード
    DEBUG=True
    # 警告対策
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # DB設定
    SQLALCHEMY_DATABASE_URI = "sqlite:///mleague.sqlite"
    SECRET_KEY = os.urandom(24)