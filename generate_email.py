#!/usr/bin/env python3
"""
Email Data Generator for Forensic Analysis
Generates realistic email data with patterns for forensic investigation
"""

import csv
import random
import json
from datetime import datetime, timedelta
import hashlib

# Configuration
TOTAL_EMAILS = 168658 
OUTPUT_FILE = 'email_data.csv'

# Email domains
DOMAINS = [
    'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'company.com',
    'business.org', 'protonmail.com', 'mail.com', 'aol.com', 'icloud.com'
]

SUSPICIOUS_DOMAINS = ['protonmail.com', 'tutanota.com', 'guerrillamail.com']

# Contact list (expanded for emails)
CONTACTS = {
    'personal': [
        {'email': f"arati{random.randint(1,100)}@gmail.com", 'name': 'Friend1', 'type': 'friend'},
        {'email': f"david{random.randint(1,100)}@yahoo.com", 'name': 'Friend2', 'type': 'friend'},
        {'email': f"sarah{random.randint(1,100)}@hotmail.com", 'name': 'Cousin', 'type': 'family'},
    ],
    'work': [
        {'email': 'boss@company.com', 'name': 'Boss', 'type': 'work'},
        {'email': 'hr@company.com', 'name': 'HR Dept', 'type': 'work'},
        {'email': 'colleague1@company.com', 'name': 'Colleague A', 'type': 'work'},
        {'email': 'colleague2@company.com', 'name': 'Colleague B', 'type': 'work'},
        {'email': 'client@business.org', 'name': 'Client X', 'type': 'work'},
    ],
    'suspicious': [
        {'email': f"xxuc{random.randint(1,100)}@protonmail.com", 'name': 'Unknown Contact', 'type': 'suspicious'},
        {'email': f"note{random.randint(1,100)}@tutanota.com", 'name': 'Signal User', 'type': 'suspicious'},
        {'email': f"spam{random.randint(1,100)}@guerrillamail.com", 'name': 'Temp User', 'type': 'suspicious'},
    ]
}

# Email templates by category
EMAIL_TEMPLATES = {
    'work': {
        'subjects': [
            "Meeting: Project {project} - {date}",
            "Q{quarter} Report - Action Required",
            "Please review: {doc_type} for client {client}",
            "Team Meeting Minutes - {date}",
            "URGENT: Response needed by {time}",
            "Project Update: {project} - Phase {phase}",
            "Budget Approval Request - {amount}",
            "Weekly Status Report - Week {week}",
        ],
        'bodies': [
            "Please find attached the {doc_type} for {client}. Review by {date}.",
            "Meeting scheduled for {time} in Conference Room {room}. Agenda attached.",
            "The {project} deadline has been moved to {date}. Please adjust accordingly.",
            "Could you please provide feedback on the attached document?",
            "Client requested changes to the {project} deliverables.",
            "Urgent: Please call me regarding the {client} account.",
            "The {quarter} financials need to be submitted by {date}.",
            "Following up on our conversation about {topic}.",
        ]
    },
    'personal': {
        'subjects': [
            "Catching up this weekend?",
            "Photos from {event}",
            "Happy Birthday {name}!",
            "Dinner plans for {day}",
            "Checking in - how are you?",
            "Weekend getaway ideas?",
            "Family gathering on {date}",
            "Can you believe what happened?",
        ],
        'bodies': [
            "Hey, long time no see! Want to grab coffee this week?",
            "Attached are the photos from our {event} trip!",
            "Hope you have a fantastic birthday! Let's celebrate on {date}.",
            "Thinking of getting together for dinner on {day}. Free?",
            "Just checking in to see how you're doing. Let's catch up soon!",
            "Found this great place for a weekend trip. Interested?",
            "Family BBQ on {date} at {time}. Bring the kids!",
            "You won't believe what happened to me yesterday...",
        ]
    },
    'financial': {
        'subjects': [
            "Invoice #{invoice} - Payment Due",
            "Your {bank} statement is ready",
            "Payment Confirmation: ${amount}",
            "Transaction Alert: ${amount}",
            "Tax Documents Available",
            "Investment Portfolio Update - Q{quarter}",
            "Mortgage Statement - {date}",
            "Credit Card Payment Due",
        ],
        'bodies': [
            "Invoice #{invoice} for ${amount} is due on {date}. Payment link: {link}",
            "Your {bank} account statement for {month} is now available online.",
            "Payment of ${amount} to {payee} has been processed. Reference: {ref}",
            "New transaction: ${amount} at {merchant} on {date}.",
            "Your {year} tax documents are ready for download.",
            "Quarterly investment report attached. Total value: ${value}",
            "Mortgage payment of ${amount} due on {date}.",
            "Credit card bill of ${amount} due in {days} days.",
        ]
    },
    'suspicious': {
        'subjects': [
            "RE: Our meeting location",
            "Updated instructions",
            "Secure message",
            "Do not reply to this email",
            "FW: Document for review",
            "Signal: New message",
            "Encrypted: Read carefully",
            "Plan B details",
        ],
        'bodies': [
            "Meeting moved to {location} at {time}. Come alone.",
            "Delete this email after reading. Meet at {location} tomorrow.",
            "Use the secure channel for further communication.",
            "The package will be delivered on {date} at {time}.",
            "Check the {platform} app for encrypted message.",
            "Memorize these instructions then delete: {instructions}",
            "Confirmation code: {code}. Use this at the meeting.",
            "Switch to the backup communication method.",
        ]
    }
}

# Helper functions
def generate_project():
    projects = ['Alpha', 'Beta', 'Gamma', 'Delta', 'Omega', 'Phoenix', 'Nova', 'Eclipse']
    return random.choice(projects)

def generate_client():
    clients = ['Acme Corp', 'Globex', 'Initech', 'Umbrella Corp', 'Wayne Enterprises', 'Stark Industries']
    return random.choice(clients)

def generate_amount():
    return round(random.uniform(100, 10000), 2)

def generate_location():
    locations = ['Central Park', 'Union Station', 'Airport', 'Mall Food Court', 'Library', 'Parking Garage']
    return random.choice(locations)

def generate_instructions():
    instructions = ['Wait for signal', 'Use back entrance', 'Bring identification', 'Leave package', 'Call upon arrival']
    return random.choice(instructions)

def generate_code():
    return ''.join(random.choices('0123456789ABCDEF', k=6))

def generate_email_content(category, contact_type):
    """Generate realistic email content based on category"""
    templates = EMAIL_TEMPLATES.get(category, EMAIL_TEMPLATES['personal'])
    
    # Generate subject
    subject_template = random.choice(templates['subjects'])
    subject = subject_template.replace('{project}', generate_project())
    subject = subject.replace('{client}', generate_client())
    subject = subject.replace('{date}', (datetime.now() + timedelta(days=random.randint(1,30))).strftime('%m/%d'))
    subject = subject.replace('{time}', f"{random.randint(9,17)}:00")
    subject = subject.replace('{quarter}', str(random.randint(1,4)))
    subject = subject.replace('{week}', str(random.randint(1,52)))
    subject = subject.replace('{amount}', f"${random.randint(100,10000)}")
    subject = subject.replace('{event}', random.choice(['vacation', 'wedding', 'party', 'trip']))
    subject = subject.replace('{name}', random.choice(['John', 'Sarah', 'Mike', 'Lisa']))
    subject = subject.replace('{day}', random.choice(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']))
    subject = subject.replace('{invoice}', str(random.randint(10000, 99999)))
    subject = subject.replace('{bank}', random.choice(['Chase', 'Bank of America', 'Wells Fargo']))
    subject = subject.replace('{month}', (datetime.now() + timedelta(days=30)).strftime('%B'))
    subject = subject.replace('{year}', str(datetime.now().year))
    subject = subject.replace('{days}', str(random.randint(5, 30)))
    subject = subject.replace('{value}', f"${random.randint(10000, 100000)}")
    
    # Generate body
    body_template = random.choice(templates['bodies'])
    body = body_template.replace('{doc_type}', random.choice(['contract', 'proposal', 'report', 'presentation']))
    body = body.replace('{client}', generate_client())
    body = body.replace('{date}', (datetime.now() + timedelta(days=random.randint(1,30))).strftime('%m/%d/%Y'))
    body = body.replace('{time}', f"{random.randint(8,20)}:00")
    body = body.replace('{room}', random.choice(['A', 'B', 'C', 'Conference Room']))
    body = body.replace('{project}', generate_project())
    body = body.replace('{topic}', random.choice(['budget', 'timeline', 'resources', 'staffing']))
    body = body.replace('{event}', random.choice(['vacation', 'wedding', 'party', 'trip']))
    body = body.replace('{day}', random.choice(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']))
    body = body.replace('{invoice}', str(random.randint(10000, 99999)))
    body = body.replace('{amount}', f"${generate_amount()}")
    body = body.replace('{link}', f"http://secure-payment{random.randint(1,100)}.com")
    body = body.replace('{bank}', random.choice(['Chase', 'Bank of America', 'Wells Fargo']))
    body = body.replace('{payee}', random.choice(['Electric Company', 'Water Utility', 'Internet Provider']))
    body = body.replace('{ref}', ''.join(random.choices('0123456789', k=10)))
    body = body.replace('{merchant}', random.choice(['Amazon', 'Walmart', 'Target', 'Best Buy']))
    body = body.replace('{year}', str(datetime.now().year))
    body = body.replace('{quarter}', str(random.randint(1,4)))
    body = body.replace('{value}', f"${random.randint(10000, 100000)}")
    body = body.replace('{days}', str(random.randint(5, 30)))
    body = body.replace('{location}', generate_location())
    body = body.replace('{platform}', random.choice(['Signal', 'Telegram', 'WhatsApp', 'ProtonMail']))
    body = body.replace('{instructions}', generate_instructions())
    body = body.replace('{code}', generate_code())
    
    return subject, body

def generate_email_data():
    """Generate email dataset"""
    print(f"\n📧 Generating {TOTAL_EMAILS:,} email records...")
    
    email_records = []
    
    # Flatten contacts
    all_contacts = []
    for category, contacts in CONTACTS.items():
        for contact in contacts:
            contact['category'] = category
            all_contacts.append(contact)
    
    # Generate date range (last 365 days)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    # Create threads/conversations
    conversations = {}
    
    for i in range(TOTAL_EMAILS):
        # Determine email category distribution
        r = random.random()
        if r < 0.4:  # 40% work
            category = 'work'
            contact = random.choice([c for c in all_contacts if c['category'] == 'work'])
        elif r < 0.7:  # 30% personal
            category = 'personal'
            contact = random.choice([c for c in all_contacts if c['category'] == 'personal'])
        elif r < 0.9:  # 20% financial
            category = 'financial'
            contact = random.choice(all_contacts)  # Financial can be anyone
        else:  # 10% suspicious
            category = 'suspicious'
            contact = random.choice([c for c in all_contacts if c['category'] == 'suspicious'])
        
        # Generate subject and body
        subject, body = generate_email_content(category, contact['type'])
        
        # Determine direction
        direction = 'SENT' if random.random() < 0.55 else 'RECEIVED'
        
        # Set sender/recipient based on direction
        if direction == 'SENT':
            sender = 'arati@email.com'
            recipient = contact['email']
        else:
            sender = contact['email']
            recipient = 'david@email.com'
        
        # Generate timestamp with patterns
        days_offset = random.randint(0, 365)
        
        # Pattern for suspicious emails (odd hours)
        if category == 'suspicious':
            hour = random.choices(
                list(range(24)),
                weights=[3 if h in [0,1,2,3,4,22,23] else 0.5 for h in range(24)]
            )[0]
        else:
            # Normal distribution (9-5)
            hour = random.choices(
                list(range(24)),
                weights=[0.1,0.1,0.1,0.1,0.1,0.2,0.5,1,3,5,5,5,5,5,5,4,3,2,1,0.5,0.5,0.3,0.2,0.1]
            )[0]
        
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        
        timestamp = start_date + timedelta(days=days_offset, hours=hour, minutes=minute, seconds=second)
        
        # Thread ID (for conversation tracking)
        thread_key = f"{sender}|{recipient}"
        if thread_key in conversations:
            # This is a reply
            thread_id = conversations[thread_key]
            is_reply = True
            in_reply_to = random.choice([e['Message_ID'] for e in email_records if e['Thread_ID'] == thread_id]) if email_records else None
        else:
            # New thread
            thread_id = f"THREAD_{i+1:06d}"
            conversations[thread_key] = thread_id
            is_reply = False
            in_reply_to = None
        
        email_records.append({
            'From': sender,
            'To': recipient,
            'Date': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'Subject': subject,
            'Body': body,
            'Message_ID': f"MSG_{i+1:06d}",
            'Thread_ID': thread_id,
            'In_Reply_To': in_reply_to if in_reply_to else '',
            'Category': category,
            'Contact_Type': contact['type'],
            'Direction': direction,
            'Has_Attachment': random.choice(['TRUE', 'FALSE']),
            'Attachment_Type': random.choice(['PDF', 'DOC', 'XLS', 'ZIP', 'IMG']) if random.random() < 0.3 else '',
            'Size_KB': random.randint(10, 5000) if random.random() < 0.3 else 0,
            'Read_Status': random.choice(['READ', 'UNREAD']),
            'Labels': random.choice(['INBOX', 'SENT', 'ARCHIVE', 'SPAM', 'WORK', 'PERSONAL'])
        })
        
        if (i + 1) % 10000 == 0:
            print(f"  Generated {i+1:,} email records...")
    
    return email_records

def save_email_data(records):
    """Save email data to CSV"""
    print(f"\n💾 Saving to {OUTPUT_FILE}...")
    
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['From', 'To', 'Date', 'Subject', 'Body', 'Message_ID', 
                     'Thread_ID', 'In_Reply_To', 'Category', 'Contact_Type', 
                     'Direction', 'Has_Attachment', 'Attachment_Type', 
                     'Size_KB', 'Read_Status', 'Labels']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)
    
    print(f"✅ Successfully saved {len(records):,} email records to {OUTPUT_FILE}")

def create_email_metadata(records):
    """Create metadata file with statistics"""
    metadata = {
        'total_records': len(records),
        'date_generated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'statistics': {
            'by_category': {},
            'by_direction': {},
            'by_contact_type': {},
            'attachments': 0,
            'threads': 0,
            'avg_thread_length': 0
        }
    }
    
    threads = set()
    
    for record in records:
        metadata['statistics']['by_category'][record['Category']] = metadata['statistics']['by_category'].get(record['Category'], 0) + 1
        metadata['statistics']['by_direction'][record['Direction']] = metadata['statistics']['by_direction'].get(record['Direction'], 0) + 1
        metadata['statistics']['by_contact_type'][record['Contact_Type']] = metadata['statistics']['by_contact_type'].get(record['Contact_Type'], 0) + 1
        
        if record['Has_Attachment'] == 'TRUE':
            metadata['statistics']['attachments'] += 1
        
        threads.add(record['Thread_ID'])
    
    metadata['statistics']['threads'] = len(threads)
    metadata['statistics']['avg_thread_length'] = round(len(records) / len(threads), 2)
    
    # Save metadata
    with open('email_data-metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"📊 Metadata saved to email_data-metadata.json")

if __name__ == "__main__":
    print("="*70)
    print(" EMAIL DATA GENERATOR FOR FORENSIC ANALYSIS")
    print("="*70)
    
    email_records = generate_email_data()
    save_email_data(email_records)
    create_email_metadata(email_records)
    
    print("\n✅ Email Data generation complete!")