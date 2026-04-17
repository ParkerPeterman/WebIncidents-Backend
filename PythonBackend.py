# Python Backend
import pandas as pd 
from fastapi import FastAPI
import pydantic as pyd 
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI() 

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

df = pd.read_csv("network_incidents.csv")

df['created_at'] = pd.to_datetime(df['created_at'])
df['resolved_at'] = pd.to_datetime(df['resolved_at'])

def calculate_mttr(df):
    resolved_df = df[df['status'] == 'Resolved'].copy()
    durations = resolved_df['resolved_at'] - resolved_df['created_at']

    avg_Hours = 0.0 

    if not durations.empty:
        mttr_delta = durations.mean()
        avg_Hours = mttr_delta.total_seconds() / 3600

    return round(avg_Hours, 2)



@app.get("/")
def read_root():
    return {"message": "Sentinel Service Advisory API is Online"}

@app.get("/metrics/summary")
def get_summary():
    try:
        """Returns high-level KPIs for the dashboard."""
        total_incidents = len(df)
        active_incidents = len(df[df['status'] != 'Resolved'])
        global_mttr = calculate_mttr(df)
    
        return {
            "total_tickets": total_incidents,
            "active_outages": active_incidents,
            "mttr_hours": global_mttr,
            "system_health": "Stable" if active_incidents < 50 else "Degraded"
        }
    except Exception as e:
        print(f"Error in summary endpoint: {e}")
        return {"error": str(e)}


@app.get("/incidents/active")
def get_active_incidents():
    """Returns a list of all current outages."""
    active_df = df[df['status'] != 'Resolved']
    # .to_dict('records') turns the DataFrame rows into a list of JSON objects
    return active_df.to_dict(orient='records')

@app.get("/metrics/chart")
def get_chart_data():
    total_counts = df['service_name'].value_counts()
    resolved_counts = df[df['status'] == 'Resolved']['service_name'].value_counts()
    
    combined_data = []
    for service in total_counts.index:
        combined_data.append({
            "name": service,
            "total": int(total_counts[service]),
            "resolved": int(resolved_counts.get(service, 0))
        })
        
    return combined_data

@app.get("/metrics/trends")
def get_trend_data():
    trend_df = df.copy()
    trend_df.set_index('created_at', inplace=True)

    daily_groups = trend_df.groupby([pd.Grouper(freq='D'), 'service_name']).size().unstack(fill_value=0)

    trend_data=[]
    for date, row in daily_groups.iterrows():
        data_point = {"date": date.strftime('%Y-%m-%d')}
        data_point.update(row.to_dict())
        trend_data.append(data_point)
    
    return {
        "data": trend_data,
        "categories": daily_groups.columns.tolist()
    }

@app.get("/metrics/heatmap")
def get_heatmap_data():
    try: 
        h_df = df.copy()
        h_df['hour'] = h_df['created_at'].dt.hour
        h_df['day_idx'] = h_df['created_at'].dt.dayofweek
        
        density = h_df.groupby(['day_idx', 'hour']).size().reset_index(name='value')
        
        return density.to_dict(orient='records') 
    except Exception as e:
        print(f"Heatmap Error: {e}")
        return {"error": str(e)}

import os

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)