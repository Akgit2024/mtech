#!/usr/bin/env python3
"""
CDR (Call Detail Record) Data Generator for Forensic Analysis
Generates realistic call data with patterns for forensic investigation
"""

import csv
import random
import json
from datetime import datetime, timedelta
import numpy as np

# Configuration
TOTAL_CALLS = 185000  
OUTPUT_FILE = 'CDR-Call-Details.csv'

# Phone number pools (same as SMS for consistency)
USER_PHONE = "8318426949"  # The "user's" phone number

def generate_phone_number(area_code=None):
    if area_code:
        return f"+91{area_code}{random.randint(1000000, 9999999)}"
    area_codes = ['812', '910', '715', '647', '982', '815', '612', '943', '732', '803']
    return f"+91{random.choice(area_codes)}{random.randint(1000000, 9999999)}"

# Contact list (same as SMS for consistency)
CONTACTS = {
    'family': [
        {'name': 'Arati', 'phone': generate_phone_number('212'), 'relationship': 'family'},
        {'name': 'David', 'phone': generate_phone_number('212'), 'relationship': 'family'},
        {'name': 'Sarah', 'phone': generate_phone_number('310'), 'relationship': 'family'},
        {'name': 'Bhagya', 'phone': generate_phone_number('415'), 'relationship': 'family'},
        {'name': 'Varun', 'phone': generate_phone_number('617'), 'relationship': 'family'},
        {'name': 'Hasini', 'phone': generate_phone_number('202'), 'relationship': 'family'},
    ],
    'work': [
        {'name': 'Boss', 'phone': generate_phone_number('305'), 'relationship': 'work'},
        {'name': 'Colleague1', 'phone': generate_phone_number('312'), 'relationship': 'work'},
        {'name': 'Colleague2', 'phone': generate_phone_number('713'), 'relationship': 'work'},
        {'name': 'Client_A', 'phone': generate_phone_number('602'), 'relationship': 'work'},
        {'name': 'Client_B', 'phone': generate_phone_number('303'), 'relationship': 'work'},
        {'name': 'HR_Dept', 'phone': generate_phone_number('212'), 'relationship': 'work'},
    ],
    'friends': [
        {'name': 'BestFriend', 'phone': generate_phone_number('310'), 'relationship': 'friend'},
        {'name': 'Friend', 'phone': generate_phone_number('415'), 'relationship': 'friend'},
        {'name': 'Neighbor', 'phone': generate_phone_number('617'), 'relationship': 'friend'},
        {'name': 'OldColleague', 'phone': generate_phone_number('202'), 'relationship': 'friend'},
    ],
    'suspicious': [
        {'name': 'Unknown1', 'phone': generate_phone_number('786'), 'relationship': 'suspicious'},
        {'name': 'Unknown2', 'phone': generate_phone_number('954'), 'relationship': 'suspicious'},
    ]
}

# Call types
CALL_TYPES = ['ANSWERED', 'MISSED', 'VOICEMAIL', 'REJECTED', 'BLOCKED']
CALL_TYPE_WEIGHTS = [0.7, 0.15, 0.1, 0.03, 0.02]  # 70% answered

# International call distribution
INTERNATIONAL_COUNTRIES = [
    {'code': '44', 'country': 'UK', 'weight': 0.4},
    {'code': '91', 'country': 'India', 'weight': 0.3},
    {'code': '86', 'country': 'China', 'weight': 0.2},
    {'code': '52', 'country': 'Mexico', 'weight': 0.1},
]

def generate_duration(call_type, relationship):
    """Generate realistic call duration in seconds"""
    if call_type == 'MISSED':
        return random.randint(0, 5)
    elif call_type == 'VOICEMAIL':
        return random.randint(10, 60)
    elif call_type == 'REJECTED':
        return random.randint(0, 3)
    elif call_type == 'BLOCKED':
        return 0
    
    # Normal answered calls
    if relationship == 'family':
        # Family calls tend to be longer
        return random.choices(
            population=[30, 60, 120, 300, 600, 1800, 3600],
            weights=[0.1, 0.2, 0.3, 0.2, 0.1, 0.05, 0.05]
        )[0]
    elif relationship == 'work':
        # Work calls: moderate length
        return random.choices(
            population=[15, 30, 60, 120, 300, 600, 1800],
            weights=[0.05, 0.1, 0.2, 0.3, 0.2, 0.1, 0.05]
        )[0]
    elif relationship == 'suspicious':
        # Suspicious calls: short and varied
        return random.choices(
            population=[5, 10, 30, 60, 120, 300, 30],
            weights=[0.1, 0.2, 0.3, 0.2, 0.1, 0.05, 0.05]
        )[0]
    else:
        # Friends: moderate
        return random.randint(30, 900)

def generate_cdr_data():
    """Generate CDR dataset"""
    print(f"\n📞 Generating {TOTAL_CALLS:,} call records...")
    
    call_records = []
    
    # Flatten contacts list
    all_contacts = []
    for category, contacts in CONTACTS.items():
        for contact in contacts:
            contact['category'] = category
            all_contacts.append(contact)
    
    # Generate date range (last 180 days)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)
    
    # Create call records
    for i in range(TOTAL_CALLS):
        # Select contact based on patterns
        if random.random() < 0.08:  # 8% suspicious
            contact = random.choice([c for c in all_contacts if c['category'] == 'suspicious'])
        elif random.random() < 0.3:  # 30% work
            contact = random.choice([c for c in all_contacts if c['category'] == 'work'])
        else:  # 62% personal
            contact = random.choice([c for c in all_contacts if c['category'] in ['family', 'friends']])
        
        # Determine if international
        is_international = random.random() < 0.05  # 5% international calls
        
        if is_international:
            country = random.choices(INTERNATIONAL_COUNTRIES, weights=[c['weight'] for c in INTERNATIONAL_COUNTRIES])[0]
            phone_number = f"+{country['code']}{random.randint(100000000, 999999999)}"
        else:
            phone_number = contact['phone']
        
        # Call type
        call_type = random.choices(CALL_TYPES, weights=CALL_TYPE_WEIGHTS)[0]
        
        # Generate duration
        duration_seconds = generate_duration(call_type, contact['category'])
        
        # Convert to minutes for CDR format
        duration_minutes = duration_seconds / 60
        
        # Distribute across day/evening/night
        hour = random.randint(0, 23)
        if 6 <= hour < 12:  # Morning
            day_mins = duration_minutes
            eve_mins = 0
            night_mins = 0
        elif 12 <= hour < 18:  # Afternoon
            day_mins = duration_minutes
            eve_mins = 0
            night_mins = 0
        elif 18 <= hour < 22:  # Evening
            day_mins = 0
            eve_mins = duration_minutes
            night_mins = 0
        else:  # Night
            day_mins = 0
            eve_mins = 0
            night_mins = duration_minutes
        
        # Generate charges (simplified pricing model)
        day_charge = day_mins * 0.05  # $0.05 per minute
        eve_charge = eve_mins * 0.03  # $0.03 per minute
        night_charge = night_mins * 0.01  # $0.01 per minute
        intl_charge = (duration_minutes * 0.20) if is_international else 0
        
        # Call counts
        if duration_minutes > 0:
            if 6 <= hour < 12:
                day_calls = 1
                eve_calls = 0
                night_calls = 0
            elif 12 <= hour < 18:
                day_calls = 1
                eve_calls = 0
                night_calls = 0
            elif 18 <= hour < 22:
                day_calls = 0
                eve_calls = 1
                night_calls = 0
            else:
                day_calls = 0
                eve_calls = 0
                night_calls = 1
        else:
            day_calls = eve_calls = night_calls = 0
        
        intl_calls = 1 if is_international else 0
        
        # Voicemail messages
        vmail_messages = 1 if call_type == 'VOICEMAIL' else 0
        
        # Account length (days since account created)
        account_length = random.randint(30, 3650)  # 1 month to 10 years
        
        # Customer service calls (correlated with account age and issues)
        if account_length < 180:  # New accounts call more
            custserv_calls = random.choices([0, 1, 2, 3], weights=[0.5, 0.3, 0.15, 0.05])[0]
        else:
            custserv_calls = random.choices([0, 1, 2], weights=[0.8, 0.15, 0.05])[0]
        
        # Churn probability (based on customer service calls and account length)
        churn_prob = (custserv_calls * 0.1) + (1 if account_length < 90 else 0) * 0.2
        churn = 'TRUE' if random.random() < churn_prob else 'FALSE'
        
        # Generate timestamp
        days_offset = random.randint(0, 180)
        timestamp = start_date + timedelta(days=days_offset, hours=hour, 
                                           minutes=random.randint(0, 59),
                                           seconds=random.randint(0, 59))
        
        call_records.append({
            'Phone Number': phone_number,
            'Contact Name': contact['name'] if not is_international else f"Intl_{country['country']}",
            'Call Type': call_type,
            'Duration (sec)': duration_seconds,
            'Day Mins': round(day_mins, 2),
            'Eve Mins': round(eve_mins, 2),
            'Night Mins': round(night_mins, 2),
            'Intl Mins': round(duration_minutes if is_international else 0, 2),
            'Day Calls': day_calls,
            'Eve Calls': eve_calls,
            'Night Calls': night_calls,
            'Intl Calls': intl_calls,
            'Day Charge': round(day_charge, 2),
            'Eve Charge': round(eve_charge, 2),
            'Night Charge': round(night_charge, 2),
            'Intl Charge': round(intl_charge, 2),
            'VMail Message': vmail_messages,
            'Account Length': account_length,
            'CustServ Calls': custserv_calls,
            'Churn': churn,
            'Date/Time': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'Call_ID': f"CALL_{i+1:06d}",
            'Relationship': contact['category'],
            'International': 'YES' if is_international else 'NO'
        })
        
        if (i + 1) % 10000 == 0:
            print(f"  Generated {i+1:,} call records...")
    
    return call_records

def save_cdr_data(records):
    """Save CDR data to CSV"""
    print(f"\n💾 Saving to {OUTPUT_FILE}...")
    
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['Phone Number', 'Contact Name', 'Call Type', 'Duration (sec)', 
                     'Day Mins', 'Eve Mins', 'Night Mins', 'Intl Mins',
                     'Day Calls', 'Eve Calls', 'Night Calls', 'Intl Calls',
                     'Day Charge', 'Eve Charge', 'Night Charge', 'Intl Charge',
                     'VMail Message', 'Account Length', 'CustServ Calls', 'Churn',
                     'Date/Time', 'Call_ID', 'Relationship', 'International']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)
    
    print(f"✅ Successfully saved {len(records):,} call records to {OUTPUT_FILE}")

def create_cdr_metadata(records):
    """Create metadata file with statistics"""
    metadata = {
        'total_records': len(records),
        'date_generated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'statistics': {
            'by_call_type': {},
            'by_relationship': {},
            'international_calls': 0,
            'total_duration_minutes': 0,
            'average_duration_seconds': 0,
            'churn_rate': 0
        }
    }
    
    total_duration = 0
    churn_count = 0
    
    for record in records:
        metadata['statistics']['by_call_type'][record['Call Type']] = metadata['statistics']['by_call_type'].get(record['Call Type'], 0) + 1
        metadata['statistics']['by_relationship'][record['Relationship']] = metadata['statistics']['by_relationship'].get(record['Relationship'], 0) + 1
        
        if record['International'] == 'YES':
            metadata['statistics']['international_calls'] += 1
        
        total_duration += int(record['Duration (sec)'])
        
        if record['Churn'] == 'TRUE':
            churn_count += 1
    
    metadata['statistics']['total_duration_minutes'] = round(total_duration / 60, 2)
    metadata['statistics']['average_duration_seconds'] = round(total_duration / len(records), 2)
    metadata['statistics']['churn_rate'] = round((churn_count / len(records)) * 100, 2)
    
    # Save metadata
    with open('CDR-Call-Details-metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"📊 Metadata saved to CDR-Call-Details-metadata.json")

if __name__ == "__main__":
    print("="*70)
    print(" CDR DATA GENERATOR FOR FORENSIC ANALYSIS")
    print("="*70)
    
    call_records = generate_cdr_data()
    save_cdr_data(call_records)
    create_cdr_metadata(call_records)
    
    print("\n✅ CDR Data generation complete!")