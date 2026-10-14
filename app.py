"""Jalankan dengan: python app.py"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from frontend.ui import main

if __name__ == "__main__":
    main()
