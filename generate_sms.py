#!/usr/bin/env python3
"""
SMS Data Generator for Forensic Analysis
Generates realistic SMS messages with patterns for forensic investigation
"""

import csv
import random
import json
from datetime import datetime, timedelta
import os
import hashlib

# Configuration
TOTAL_SMS = 185000  # ~100,000 SMS messages
OUTPUT_FILE = 'SMS-Data.csv'

# Phone number pools
USER_PHONE = "8318426949"  # The "user's" phone number

# Generate realistic phone numbers
def generate_phone_number(area_code=None):
    if area_code:
        return f"+91{area_code}{random.randint(1000000, 9999999)}"
    area_codes = ['812', '910', '715', '647', '982', '815', '612', '943', '732', '803']
    return f"+91{random.choice(area_codes)}{random.randint(1000000, 9999999)}"

# Contact list (people the user communicates with)
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
        {'name': 'Burner1', 'phone': generate_phone_number('305'), 'relationship': 'suspicious'},
        {'name': 'Contact_X', 'phone': generate_phone_number('646'), 'relationship': 'suspicious'},
    ]
}

# Message templates by category
MESSAGE_TEMPLATES = {
    'normal': [
        "Hey, how are you?",
        "See you tomorrow",
        "Thanks for the help",
        "What time are we meeting?",
        "I'm running late",
        "Can you call me?",
        "Happy Birthday!",
        "See you soon",
        "OK, sounds good",
        "On my way",
        "Got it, thanks",
        "Call me when you can",
        "Where are you?",
        "I'm at the office",
        "What's for dinner?",
    ],
    'work': [
        "Meeting at 2pm",
        "Please review the document",
        "Can you send the report?",
        "Client wants a call",
        "Deadline is tomorrow",
        "Updated the project plan",
        "Need your input",
        "Presentation at 3",
        "Conference call in 10",
        "Email me the details",
    ],
    'family': [
        "Don't forget milk",
        "What time is dinner?",
        "Pick up kids at 5",
        "Love you",
        "See you at home",
        "Happy anniversary",
        "Doctor appointment at 10",
        "How was school?",
        "Coming home late",
    ],
    'financial': [
        "Payment received",
        "Please send $500",
        "Bank transfer confirmed",
        "Your invoice #INV-{ref}",
        "Payment due tomorrow",
        "Check your account",
        "Money sent",
        "Transaction ID: {txn}",
        "Bitcoin address: {btc}",
        "Transfer complete",
    ],
    'suspicious': [
        "Delete the messages",
        "Use encrypted app",
        "Meet at {location} at {time}",
        "Burner phone only",
        "Don't call, text only",
        "Code word: {codeword}",
        "They're watching",
        "Switch to Signal",
        "Meeting moved to {location}",
        "Bring cash only",
        "Confirm when done",
        "Use the back entrance",
        "Park at {location}",
        "Wait for my signal",
    ],
    'urgent': [
        "URGENT: Call me now",
        "Emergency!",
        "ASAP - respond",
        "911 situation",
        "Immediate attention",
        "Urgent meeting",
        "Call immediately",
        "Time sensitive",
    ],
    'spam': [
        "You won $1,000,000!",
        "Click here: {link}",
        "Limited time offer",
        "Your account suspended",
        "Verify your password",
        "Free gift card",
        "Congratulations!",
        "Urgent action required",
        "Your package delayed",
    ]
}

# Generate realistic location names
LOCATIONS = ['park', 'mall', 'cafe', 'station', 'garage', 'plaza', 'hotel', 'restaurant']
CODES = ['alpha', 'bravo', 'charlie', 'delta', 'echo', 'foxtrot']
TIMES = ['noon', 'midnight', 'dawn', 'dusk', '10pm', '6am']

def generate_btc_address():
    return f"1{''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ234567', k=33))}"

def generate_message(category, contact_type):
    """Generate realistic message based on category"""
    if category == 'financial':
        template = random.choice(MESSAGE_TEMPLATES['financial'])
        if '{ref}' in template:
            template = template.replace('{ref}', str(random.randint(1000, 9999)))
        if '{txn}' in template:
            template = template.replace('{txn}', ''.join(random.choices('0123456789ABCDEF', k=16)))
        if '{btc}' in template:
            template = template.replace('{btc}', generate_btc_address())
        return template
    
    elif category == 'suspicious':
        template = random.choice(MESSAGE_TEMPLATES['suspicious'])
        if '{location}' in template:
            template = template.replace('{location}', random.choice(LOCATIONS))
        if '{time}' in template:
            template = template.replace('{time}', random.choice(TIMES))
        if '{codeword}' in template:
            template = template.replace('{codeword}', random.choice(CODES))
        return template
    
    elif category == 'urgent':
        return random.choice(MESSAGE_TEMPLATES['urgent'])
    
    elif category == 'spam':
        template = random.choice(MESSAGE_TEMPLATES['spam'])
        if '{link}' in template:
            template = template.replace('{link}', f"http://bit.ly/{random.randint(10000, 99999)}")
        return template
    
    else:
        # Normal messages based on contact type
        if contact_type == 'work':
            return random.choice(MESSAGE_TEMPLATES['work'])
        elif contact_type == 'family':
            return random.choice(MESSAGE_TEMPLATES['family'])
        else:
            return random.choice(MESSAGE_TEMPLATES['normal'])

def generate_sms_data():
    """Generate SMS dataset"""
    print(f"\n📱 Generating {TOTAL_SMS:,} SMS messages...")
    
    sms_records = []
    
    # Flatten contacts list
    all_contacts = []
    for category, contacts in CONTACTS.items():
        for contact in contacts:
            contact['category'] = category
            all_contacts.append(contact)
    
    # Generate date range (last 180 days)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)
    
    # Create patterns:
    # - Regular contacts have normal patterns
    # - Suspicious contacts have night/weekend patterns
    # - Financial contacts have transaction patterns
    
    for i in range(TOTAL_SMS):
        # Determine contact based on desired distribution
        if random.random() < 0.05:  # 5% suspicious
            contact = random.choice([c for c in all_contacts if c['category'] == 'suspicious'])
            category = 'suspicious' if random.random() < 0.3 else random.choice(['normal', 'urgent'])
        elif random.random() < 0.10:  # 10% financial
            contact = random.choice(all_contacts)
            category = 'financial'
        elif random.random() < 0.10:  # 10% work
            contact = random.choice([c for c in all_contacts if c['category'] == 'work'])
            category = 'work'
        else:  # 75% normal
            contact = random.choice([c for c in all_contacts if c['category'] in ['family', 'friends']])
            category = random.choice(['normal', 'family'])
        
        # Determine direction
        direction = 'OUTGOING' if random.random() < 0.55 else 'INCOMING'
        
        # Generate timestamp with patterns
        days_offset = random.randint(0, 180)
        
        # Pattern for suspicious contacts (late night)
        if contact['category'] == 'suspicious':
            # Bias towards late night/early morning
            hour = random.choices(
                population=list(range(24)),
                weights=[3 if h in [0,1,2,3,4,5] else 0.5 for h in range(24)]
            )[0]
        else:
            # Normal distribution with peak during day
            hour = random.choices(
                population=list(range(24)),
                weights=[0.2,0.2,0.1,0.1,0.1,0.5,  # 0-5
                        1,2,3,4,5,5,5,5,5,4,3,2,  # 6-17
                        2,1.5,1,0.5,0.5,0.5]      # 18-23
            )[0]
        
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        
        timestamp = start_date + timedelta(days=days_offset, hours=hour, minutes=minute, seconds=second)
        
        # Generate message
        message = generate_message(category, contact['category'])
        
        # Add some variation
        if random.random() < 0.3:
            message = message.lower()
        elif random.random() < 0.1:
            message = message.upper()
        
        sms_records.append({
            'Phone Number': contact['phone'],
            'Contact Name': contact['name'],
            'Direction': direction,
            'Message': message,
            'Date/Time': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'Category': category,
            'Relationship': contact['category'],
            'Read': random.choice(['YES', 'NO']),
            'Message_ID': f"SMS_{i+1:06d}"
        })
        
        if (i + 1) % 10000 == 0:
            print(f"  Generated {i+1:,} SMS records...")
    
    return sms_records

def save_sms_data(records):
    """Save SMS data to CSV"""
    print(f"\n💾 Saving to {OUTPUT_FILE}...")
    
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['Phone Number', 'Contact Name', 'Direction', 'Message', 'Date/Time', 'Category', 'Relationship', 'Read', 'Message_ID']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)
    
    print(f"✅ Successfully saved {len(records):,} SMS messages to {OUTPUT_FILE}")

def create_sms_metadata(records):
    """Create metadata file with statistics"""
    metadata = {
        'total_records': len(records),
        'date_generated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'statistics': {
            'by_direction': {},
            'by_category': {},
            'by_relationship': {}
        }
    }
    
    # Calculate statistics
    for record in records:
        metadata['statistics']['by_direction'][record['Direction']] = metadata['statistics']['by_direction'].get(record['Direction'], 0) + 1
        metadata['statistics']['by_category'][record['Category']] = metadata['statistics']['by_category'].get(record['Category'], 0) + 1
        metadata['statistics']['by_relationship'][record['Relationship']] = metadata['statistics']['by_relationship'].get(record['Relationship'], 0) + 1
    
    # Save metadata
    with open('SMS-Data-metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"📊 Metadata saved to SMS-Data-metadata.json")

if __name__ == "__main__":
    print("="*70)
    print(" SMS DATA GENERATOR FOR FORENSIC ANALYSIS")
    print("="*70)
    
    sms_records = generate_sms_data()
    save_sms_data(sms_records)
    create_sms_metadata(sms_records)
    
    print("\n✅ SMS Data generation complete!")