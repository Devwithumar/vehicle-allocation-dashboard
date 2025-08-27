# utils.py - helper functions for Vehicle Allocation Dashboard
from typing import Dict
import pandas as pd
import numpy as np
import io

COMMON_KEYS = {
    'day': ['day', 'weekday', 'day_of_week'],
    'vehicle': ['vehicle id', 'vehicle', 'vehicle_id', 'vehicleid', 'vehicle name'],
    'start': ['departure time', 'start time', 'start', 'departure'],
    'end': ['arrival time', 'end time', 'arrival', 'end'],
    'purpose': ['journey purpose', 'purpose', 'type', 'journey_type', 'journey purpose/type'],
    'route': ['route', 'destination', 'to', 'route/destination'],
    'passengers': ['passengers', 'pax', 'no_passengers', 'num_passengers']
}

def detect_header_and_read(file_obj) -> pd.DataFrame:
    best = None
    best_score = -1
    # if file_obj is BytesIO, ensure pointer at 0
    try:
        file_obj.seek(0)
    except Exception:
        pass
    for header in range(0, 5):
        try:
            df = pd.read_excel(file_obj, header=header)
        except Exception:
            try:
                file_obj.seek(0)
            except Exception:
                pass
            continue
        cols = [str(c).strip().lower() for c in df.columns]
        score = 0
        for key, variants in COMMON_KEYS.items():
            for v in variants:
                if any(v == c or v in c for c in cols):
                    score += 1
                    break
        if score > best_score and not df.empty:
            best_score = score
            best = (header, df)
        try:
            file_obj.seek(0)
        except Exception:
            pass
    if best:
        _, df = best
        df.columns = [str(c).strip() for c in df.columns]
        return df
    else:
        try:
            file_obj.seek(0)
        except Exception:
            pass
        return pd.read_excel(file_obj)

def auto_map_columns(df: pd.DataFrame) -> Dict[str, str]:
    cols = {c.lower(): c for c in df.columns}
    mapped = {}
    for logical, variants in COMMON_KEYS.items():
        for v in variants:
            for c_lower, orig in cols.items():
                if v == c_lower or v in c_lower or c_lower in v:
                    mapped[logical] = orig
                    break
            if logical in mapped:
                break
    return mapped

def parse_times(df: pd.DataFrame, mapping: Dict[str, str]) -> pd.DataFrame:
    df = df.copy()
    def parse_time_col(col):
        if not col or col not in df.columns:
            return pd.to_datetime(pd.Series([pd.NaT]*len(df)))
        try:
            parsed = pd.to_datetime(df[col], errors='coerce')
            return parsed
        except Exception:
            return pd.to_datetime(df[col].astype(str), errors='coerce')

    start_col = mapping.get('start') if mapping else None
    end_col = mapping.get('end') if mapping else None
    df['_start_raw'] = parse_time_col(start_col)
    df['_end_raw'] = parse_time_col(end_col)

    day_col = mapping.get('day') if mapping else None
    if day_col and day_col in df.columns:
        day_map = {d.lower(): i for i, d in enumerate(['monday','tuesday','wednesday','thursday','friday','saturday','sunday'])}
        df['_day_index'] = df[day_col].astype(str).str.lower().map(day_map).fillna(0).astype(int)
    else:
        df['_day_index'] = 0

    base_date = pd.to_datetime('2025-01-06')

    def make_dt(row, raw_col):
        raw = row[raw_col]
        if pd.isna(raw):
            return pd.NaT
        try:
            if raw.date() == pd.to_datetime('1970-01-01').date() or raw.year < 1900:
                return pd.Timestamp.combine(base_date + pd.Timedelta(days=int(row['_day_index'])), pd.Timestamp(raw).time())
            else:
                return raw
        except Exception:
            # fallback: interpret as time-only string
            try:
                t = pd.to_datetime(str(raw)).time()
                return pd.Timestamp.combine(base_date + pd.Timedelta(days=int(row['_day_index'])), t)
            except Exception:
                return pd.NaT

    df['start_dt'] = df.apply(lambda r: make_dt(r, '_start_raw'), axis=1)
    df['end_dt'] = df.apply(lambda r: make_dt(r, '_end_raw'), axis=1)
    df.loc[(~df['start_dt'].isna()) & (~df['end_dt'].isna()) & (df['end_dt'] <= df['start_dt']), 'end_dt'] += pd.Timedelta(days=1)
    df['duration_hours'] = (df['end_dt'] - df['start_dt']).dt.total_seconds() / 3600.0
    return df

def detect_conflicts(df: pd.DataFrame, vehicle_col: str = 'Vehicle ID') -> pd.DataFrame:
    conflicts = []
    for vehicle, group in df.groupby(vehicle_col):
        g = group.sort_values('start_dt')
        prev_end = None
        prev_idx = None
        for idx, row in g.iterrows():
            if prev_end is not None and not pd.isna(row['start_dt']):
                if row['start_dt'] < prev_end:
                    conflicts.append({
                        'vehicle': vehicle,
                        'idx1': prev_idx,
                        'idx2': idx,
                        'overlap_minutes': (prev_end - row['start_dt']).total_seconds()/60.0
                    })
            prev_end = row['end_dt'] if not pd.isna(row['end_dt']) else prev_end
            prev_idx = idx
    return pd.DataFrame(conflicts)

def compute_utilization(df: pd.DataFrame, vehicle_col: str) -> pd.DataFrame:
    out = df.groupby(vehicle_col)['duration_hours'].sum().reset_index().rename(columns={'duration_hours': 'total_hours'})
    out = out.sort_values('total_hours', ascending=False)
    return out

def generate_sample_excel(path_or_buf):
    demo = pd.DataFrame([
        ['Monday', 'Van 001', '08:00', '15:30', 'School Run', 'Route A', 10],
        ['Tuesday', 'Car 002', '09:30', '11:00', 'Hospital Visit', 'Route B', 2],
        ['Wednesday', 'Van 001', '10:15', '12:30', 'Shopping Trip', 'Route C', 5],
        ['Friday', 'Bus 010', '07:00', '17:30', 'Long Haul', 'Route D', 20],
        ['Monday', 'Van 002', '07:30', '09:30', 'School Run', 'Route B', 8],
        ['Tuesday', 'Van 003', '08:00', '12:00', 'Delivery', 'Route E', 1],
        ['Wednesday', 'Car 005', '13:00', '16:00', 'Service', 'Route F', 1],
        ['Thursday', 'Minibus 007', '06:00', '10:00', 'Airport Run', 'Route G', 12],
        ['Friday', 'Van 001', '18:00', '22:00', 'Night Shift', 'Route H', 3],
        ['Saturday', 'Bus 011', '09:00', '17:00', 'Charter', 'Route I', 40],
        ['Sunday', 'Van 004', '10:00', '14:00', 'Community', 'Route J', 6],
        ['Monday', 'Van 005', '08:30', '11:00', 'Routine', 'Route K', 4],
    ], columns=['Day','Vehicle ID','Departure Time','Arrival Time','Journey Purpose','Route/Destination','Passengers'])
    if hasattr(path_or_buf, 'write'):
        demo.to_excel(path_or_buf, index=False)
    else:
        demo.to_excel(path_or_buf, index=False)
