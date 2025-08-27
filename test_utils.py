# tests/test_utils.py - basic tests for utils functions
import io
import pandas as pd
from utils import detect_header_and_read, auto_map_columns, parse_times, detect_conflicts

def test_sample_read():
    from utils import generate_sample_excel
    buf = io.BytesIO()
    generate_sample_excel(buf)
    buf.seek(0)
    df = detect_header_and_read(buf)
    assert not df.empty
    mapping = auto_map_columns(df)
    assert 'vehicle' in mapping
