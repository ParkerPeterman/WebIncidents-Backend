## KFN Practice Project

import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

def generate_mock_data(num_records=100):

    #Provides options for possible services, issues,, and statuses
    services = ['Fiber-Backbone-East', 'Router-Group-A', 'Switch-Maize-04', 'Cloud-Gateway-Primary', 'VoIP-Server-Hutch']
    issue_types = ['Hardware Failure', 'Latency Spike', 'Packet Loss', 'Power Outage', 'Configuration Error']
    statuses = ['Resolved', 'In-Progress', 'Open'] 

    data = []

    base_date = datetime.now() - timedelta(days=30)

    for i in range(num_records):
        
        #Creating Ticket ID and status of Ticket
        ticket_id = f"TICK-{1000+i}"
        service = random.choice(services)
        issue = random.choice(issue_types)
        status_weights = weights = [90,5,5]
        status = random.choices(statuses, weights = status_weights, k=1) [0]

        #Creates Ticket Initialization Date and Time
        created_at = base_date + timedelta(
            days = random.randint(0,29), hours = random.randint(0,23), minutes=random.randint(0,59)
        )

        resolved_at = None
        #Generates stats for resolved tickets to calculate MTTR
        if status == 'Resolved':
            repair_time_hours = random.choices([random.uniform(0.5, 4), random.uniform(4, 24), random.uniform(24, 72)], weights=[70,20,10]) [0]
            resolved_at = created_at + timedelta(hours = repair_time_hours)

        data.append({
            "ticket_id": ticket_id,
            "service_name": service,
            "issue_type": issue,
            "status": status,
            "created_at": created_at.strftime('%Y-%m-%d %H:%M:%S'),
            "resolved_at": resolved_at.strftime('%Y-%m-%d %H:%M:%S') if resolved_at else None
        })

    df = pd.DataFrame(data)
    df.to_csv("network_incidents.csv", index=False)
    print(f"Successfully generated {num_records} incidents in 'network_incidents.csv'")

if __name__ == "__main__":
    generate_mock_data(500)