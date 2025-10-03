# -*- coding: utf-8 -*-
class BaseRepo:
    def __init__(self, conn): self.conn = conn
    def _like(self, s):
        return f"%{(s or '').lower().replace(' ','').replace('-','').replace('_','')}%"
