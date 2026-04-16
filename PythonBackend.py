# Python Backend
import pandas as pd 
from fastapi import FastAPI
import pydantic as pyd 
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI() 

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://webincidents.parkerpeterman.com/"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

df = pd.read_csv("network_incidents.csv")

df['created_at'] = pd.to_datetime(df['created_at'])
df['resolved_at'] = pd.to_datetime(df['resolved_at'])

def calculate_mttr(df):
    #MTTR DF that only brings rows where status = resolved
    resolved_df = df[df['status'] == 'Resolved'].copy()
    #initialize array of resolution time values
    durations = resolved_df['resolved_at'] - resolved_df['created_at']

    if not durations.empty:
        mttr_delta = durations.mean()
        avg_Hours = mttr_delta.total_seconds() / 3600

    return round(avg_Hours, 2)



@app.get("/")
def read_root():
    return {"message": "Sentinel Service Advisory API is Online"}

@app.get("/metrics/summary")
def get_summary():
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


import os

if __name__ == "__main__":
    import uvicorn
    # This looks for the "PORT" environment variable provided by the cloud host
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)