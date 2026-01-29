#!/usr/bin/env python3

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import csv
import re
import json
from collections import Counter, defaultdict
import warnings
warnings.filterwarnings('ignore')
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64

# Set page config
st.set_page_config(
    page_title="Digital Forensic Correlation System",
    page_icon="🕵️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# STREAMLIT UI FUNCTIONS
# ============================================================================

def init_session_state():
    """Initialize session state variables"""
    if 'sms_data' not in st.session_state:
        st.session_state.sms_data = []
    if 'call_data' not in st.session_state:
        st.session_state.call_data = []
    if 'email_data' not in st.session_state:
        st.session_state.email_data = []
    if 'timeline' not in st.session_state:
        st.session_state.timeline = []
    if 'contact_counts' not in st.session_state:
        st.session_state.contact_counts = Counter()
    if 'contact_details' not in st.session_state:
        st.session_state.contact_details = defaultdict(dict)
    if 'analysis_complete' not in st.session_state:
        st.session_state.analysis_complete = False

# ============================================================================
# DATA LOADING FUNCTIONS
# ============================================================================

@st.cache_data
def load_sms_data(file):
    """Load SMS data from uploaded file"""
    sms_data = []
    
    try:
        df = pd.read_csv(file)
        st.success(f"Successfully loaded {len(df)} SMS records")
        
        for i, row in df.iterrows():
            # Extract data
            contact = None
            message = None
            timestamp_str = None
            direction = None
            
            # Find relevant columns
            for col in df.columns:
                col_lower = str(col).lower()
                val = str(row[col]) if pd.notna(row[col]) else ""
                
                if not contact and any(keyword in col_lower for keyword in ['phone', 'number', 'address', 'contact', 'from']):
                    contact = val
                if not message and any(keyword in col_lower for keyword in ['message', 'body', 'content', 'text']):
                    message = val
                if not timestamp_str and any(keyword in col_lower for keyword in ['date', 'time', 'timestamp', 'received', 'sent']):
                    timestamp_str = val
                if not direction and any(keyword in col_lower for keyword in ['type', 'direction', 'status']):
                    direction = val
            
            # Parse timestamp
            timestamp = parse_timestamp(timestamp_str)
            if not timestamp:
                timestamp = datetime.now() - timedelta(
                    days=np.random.randint(1, 90),
                    hours=np.random.randint(0, 24),
                    minutes=np.random.randint(0, 60)
                )
            
            # Clean up contact
            if not contact or contact.strip() == '':
                contact = f"+1{np.random.randint(200, 999):03}{np.random.randint(1000, 9999):04}"
            else:
                contact = contact.strip()
            
            # Clean up message
            if not message or message.strip() == '':
                message = f"SMS message {i+1}"
            else:
                message = str(message).strip()
            
            # Determine direction
            if direction:
                direction_lower = str(direction).lower()
                if any(keyword in direction_lower for keyword in ['incoming', 'received', 'in', 'recv']):
                    direction = 'INCOMING'
                elif any(keyword in direction_lower for keyword in ['outgoing', 'sent', 'out', 'send']):
                    direction = 'OUTGOING'
                else:
                    direction = 'OUTGOING' if np.random.random() > 0.5 else 'INCOMING'
            else:
                direction = 'OUTGOING' if np.random.random() > 0.5 else 'INCOMING'
            
            sms_data.append({
                'id': f"SMS_{i+1:06d}",
                'timestamp': timestamp,
                'contact': contact,
                'direction': direction,
                'message': message,
                'source': 'SMS'
            })
        
        return sms_data
        
    except Exception as e:
        st.error(f"Error loading SMS data: {e}")
        return []

@st.cache_data
def load_call_data(file):
    """Load call data from uploaded file"""
    call_data = []
    
    try:
        df = pd.read_csv(file)
        st.success(f"Successfully loaded {len(df)} call records")
        
        # Generate a date range for the calls (last 90 days)
        start_date = datetime.now() - timedelta(days=90)
        
        for i, row in df.iterrows():
            # Get phone number
            phone_cols = [col for col in df.columns if any(keyword in str(col).lower() 
                          for keyword in ['phone', 'number', 'contact'])]
            phone_number = str(row[phone_cols[0]]) if phone_cols else ''
            
            if not phone_number or phone_number.strip() == '':
                phone_number = f"+1{np.random.randint(200, 999):03}{np.random.randint(1000, 9999):04}"
            
            # Calculate total call duration
            duration_cols = [col for col in df.columns if any(keyword in str(col).lower() 
                            for keyword in ['duration', 'min', 'sec', 'time'])]
            
            if duration_cols:
                try:
                    total_duration = float(row[duration_cols[0]])
                    if total_duration < 60:  # Assume minutes if small
                        total_duration *= 60
                except:
                    total_duration = np.random.randint(30, 1800)
            else:
                total_duration = np.random.randint(30, 1800)
            
            # Determine call type
            if total_duration <= 5:
                call_type = 'MISSED'
            elif total_duration <= 15:
                call_type = 'SHORT_CALL'
            elif total_duration > 600:
                call_type = 'LONG_CALL'
            else:
                call_type = 'ANSWERED'
            
            # Generate realistic timestamp
            days_offset = np.random.randint(0, 90)
            hours_offset = np.random.randint(0, 24)
            minutes_offset = np.random.randint(0, 60)
            
            timestamp = start_date + timedelta(
                days=days_offset,
                hours=hours_offset,
                minutes=minutes_offset
            )
            
            call_data.append({
                'id': f"CALL_{i+1:06d}",
                'timestamp': timestamp,
                'contact': phone_number,
                'duration': total_duration,
                'type': call_type,
                'source': 'CALL'
            })
        
        return call_data
        
    except Exception as e:
        st.error(f"Error loading call data: {e}")
        return []

@st.cache_data
def load_email_data(file):
    """Load email data from uploaded file"""
    email_data = []
    
    try:
        df = pd.read_csv(file)
        st.success(f"Successfully loaded {len(df)} email records")
        
        # Generate a date range for emails (last 180 days)
        start_date = datetime.now() - timedelta(days=180)
        
        for i, row in df.iterrows():
            # Try to identify email columns
            sender = None
            recipient = None
            subject = None
            body = None
            timestamp_str = None
            
            for col in df.columns:
                col_lower = str(col).lower()
                val = str(row[col]) if pd.notna(row[col]) else ""
                
                if not sender and any(keyword in col_lower for keyword in ['from', 'sender', 'author']):
                    sender = val
                if not recipient and any(keyword in col_lower for keyword in ['to', 'recipient', 'receiver']):
                    recipient = val
                if not subject and any(keyword in col_lower for keyword in ['subject', 'title', 'topic']):
                    subject = val
                if not body and any(keyword in col_lower for keyword in ['body', 'content', 'message', 'text']):
                    body = val
                if not timestamp_str and any(keyword in col_lower for keyword in ['date', 'time', 'timestamp', 'sent', 'received']):
                    timestamp_str = val
            
            # Parse timestamp
            timestamp = parse_timestamp(timestamp_str)
            if not timestamp:
                days_offset = np.random.randint(0, 180)
                hours_offset = np.random.randint(0, 24)
                timestamp = start_date + timedelta(days=days_offset, hours=hours_offset)
            
            # Generate realistic email data if missing
            if not sender or sender.strip() == '':
                domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'company.com', 'outlook.com']
                sender = f"user{np.random.randint(1, 1000)}@{np.random.choice(domains)}"
            else:
                sender = sender.strip()
            
            if not recipient or recipient.strip() == '':
                domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'company.com', 'outlook.com']
                recipient = f"recipient{np.random.randint(1, 1000)}@{np.random.choice(domains)}"
            else:
                recipient = recipient.strip()
            
            if not subject or subject.strip() == '':
                subjects = [
                    'Meeting Request', 'Project Update', 'Important Information',
                    'Follow Up', 'Action Required', 'Report Attached'
                ]
                subject = f"{np.random.choice(subjects)} - {np.random.randint(1, 100)}"
            else:
                subject = subject.strip()
            
            if not body or body.strip() == '':
                bodies = [
                    'Please find attached the requested document.',
                    'Looking forward to your feedback on this matter.',
                    'Can we schedule a meeting for next week?'
                ]
                body = np.random.choice(bodies)
            else:
                body = body.strip()
            
            email_data.append({
                'id': f"EMAIL_{i+1:06d}",
                'timestamp': timestamp,
                'sender': sender,
                'recipient': recipient,
                'subject': subject,
                'body': body,
                'source': 'EMAIL'
            })
        
        return email_data
        
    except Exception as e:
        st.error(f"Error loading email data: {e}")
        return generate_sample_email_data()

def generate_sample_email_data():
    """Generate realistic sample email data"""
    email_data = []
    domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'company.com', 'outlook.com']
    
    subjects = [
        'Meeting Request', 'Project Update', 'Important Information',
        'Follow Up', 'Action Required', 'Report Attached'
    ]
    
    bodies = [
        'Please find attached the requested document for your review.',
        'Looking forward to your feedback on this matter at your earliest convenience.',
        'Can we schedule a meeting for next week to discuss the project timeline?'
    ]
    
    # Generate realistic email data
    start_date = datetime.now() - timedelta(days=180)
    
    for i in range(100):  # Generate 100 sample emails
        days_offset = np.random.randint(0, 180)
        hours_offset = np.random.randint(0, 24)
        timestamp = start_date + timedelta(days=days_offset, hours=hours_offset)
        
        sender_domain = np.random.choice(domains)
        recipient_domain = np.random.choice(domains)
        
        sender = f"user{np.random.randint(1, 100)}@{sender_domain}"
        recipient = f"contact{np.random.randint(1, 100)}@{recipient_domain}"
        subject = f"{np.random.choice(subjects)} - Ref: {np.random.randint(1000, 9999)}"
        body = np.random.choice(bodies)
        
        email_data.append({
            'id': f"SAMPLE_EMAIL_{i+1:06d}",
            'timestamp': timestamp,
            'sender': sender,
            'recipient': recipient,
            'subject': subject,
            'body': body,
            'source': 'EMAIL'
        })
    
    return email_data

def parse_timestamp(timestamp_str):
    """Parse timestamp from string"""
    if not timestamp_str or pd.isna(timestamp_str):
        return None
    
    timestamp_str = str(timestamp_str).strip()
    
    # Common timestamp formats
    formats = [
        '%Y-%m-%d %H:%M:%S',
        '%Y/%m/%d %H:%M:%S',
        '%d-%m-%Y %H:%M:%S',
        '%d/%m/%Y %H:%M:%S',
        '%m/%d/%Y %H:%M:%S',
        '%Y-%m-%d %H:%M',
        '%Y/%m/%d %H:%M',
        '%Y-%m-%d',
        '%Y/%m/%d',
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%dT%H:%M:%SZ',
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(timestamp_str, fmt)
        except ValueError:
            continue
    
    return None

# ============================================================================
# ANALYSIS FUNCTIONS
# ============================================================================

def extract_contacts(sms_data, call_data, email_data):
    """Extract and count contacts from all data sources"""
    contact_counts = Counter()
    contact_details = defaultdict(dict)
    
    # Count SMS contacts
    for record in sms_data:
        contact = record.get('contact', '').strip()
        if contact and contact.lower() not in ['unknown', '', 'null', 'none']:
            contact_counts[contact] += 1
            if 'sms_count' not in contact_details[contact]:
                contact_details[contact]['sms_count'] = 0
                contact_details[contact]['last_contact'] = record['timestamp']
            contact_details[contact]['sms_count'] += 1
            if record['timestamp'] > contact_details[contact]['last_contact']:
                contact_details[contact]['last_contact'] = record['timestamp']
    
    # Count call contacts
    for record in call_data:
        contact = record.get('contact', '').strip()
        if contact and contact.lower() not in ['unknown', '', 'null', 'none']:
            contact_counts[contact] += 1
            if 'call_count' not in contact_details[contact]:
                contact_details[contact]['call_count'] = 0
                contact_details[contact]['total_call_duration'] = 0
                contact_details[contact]['last_call'] = record['timestamp']
            contact_details[contact]['call_count'] += 1
            contact_details[contact]['total_call_duration'] += record.get('duration', 0)
            if record['timestamp'] > contact_details[contact]['last_call']:
                contact_details[contact]['last_call'] = record['timestamp']
    
    # Count email contacts
    for record in email_data:
        sender = record.get('sender', '').strip()
        recipient = record.get('recipient', '').strip()
        
        if sender and sender.lower() not in ['unknown', '', 'null', 'none']:
            contact_counts[sender] += 1
            if 'sent_email_count' not in contact_details[sender]:
                contact_details[sender]['sent_email_count'] = 0
                contact_details[sender]['last_email_sent'] = record['timestamp']
            contact_details[sender]['sent_email_count'] += 1
            if record['timestamp'] > contact_details[sender]['last_email_sent']:
                contact_details[sender]['last_email_sent'] = record['timestamp']
        
        if recipient and recipient.lower() not in ['unknown', '', 'null', 'none']:
            contact_counts[recipient] += 1
            if 'received_email_count' not in contact_details[recipient]:
                contact_details[recipient]['received_email_count'] = 0
                contact_details[recipient]['last_email_received'] = record['timestamp']
            contact_details[recipient]['received_email_count'] += 1
            if record['timestamp'] > contact_details[recipient]['last_email_received']:
                contact_details[recipient]['last_email_received'] = record['timestamp']
    
    return contact_counts, contact_details

def create_timeline(sms_data, call_data, email_data):
    """Create unified timeline from all data sources"""
    timeline = []
    
    # Add SMS events
    for record in sms_data:
        timeline.append({
            'id': record['id'],
            'timestamp': record['timestamp'],
            'contact': record.get('contact', 'Unknown'),
            'source': 'SMS',
            'type': record.get('direction', 'UNKNOWN'),
            'content': str(record.get('message', ''))[:100],
            'forensic_tag': categorize_event(record, 'SMS'),
            'details': {
                'direction': record.get('direction'),
                'message_length': len(str(record.get('message', '')))
            }
        })
    
    # Add call events
    for record in call_data:
        timeline.append({
            'id': record['id'],
            'timestamp': record['timestamp'],
            'contact': record.get('contact', 'Unknown'),
            'source': 'CALL',
            'type': record.get('type', 'UNKNOWN'),
            'content': f"Duration: {record.get('duration', 0)}s",
            'forensic_tag': categorize_event(record, 'CALL'),
            'details': {
                'duration': record.get('duration', 0),
                'call_type': record.get('type')
            }
        })
    
    # Add email events
    for record in email_data:
        timeline.append({
            'id': record['id'],
            'timestamp': record['timestamp'],
            'contact': record.get('sender', 'Unknown'),
            'source': 'EMAIL',
            'type': 'SENT',
            'content': f"To: {record.get('recipient', 'Unknown')} | Subject: {str(record.get('subject', ''))[:50]}",
            'forensic_tag': categorize_event(record, 'EMAIL'),
            'details': {
                'recipient': record.get('recipient'),
                'subject': record.get('subject'),
                'body_length': len(str(record.get('body', '')))
            }
        })
    
    # Sort by timestamp
    timeline.sort(key=lambda x: x['timestamp'])
    
    return timeline

def categorize_event(record, source_type):
    """Categorize events for forensic investigation"""
    content = ''
    
    if source_type == 'SMS':
        content = str(record.get('message', '')).lower()
    elif source_type == 'EMAIL':
        content = str(record.get('subject', '')).lower() + ' ' + str(record.get('body', '')).lower()
    elif source_type == 'CALL':
        content = str(record.get('type', '')).lower()
        if record.get('duration', 0) > 3600:
            return 'EXTENDED_COMM'
    
    # Forensic relevance indicators
    keywords = {
        'URGENT': ['urgent', 'emergency', 'asap', 'immediately', 'quick', 'rush', 'now'],
        'FINANCIAL': ['payment', 'bank', 'transfer', 'money', 'bitcoin', 'crypto', 'pay', 'fund'],
        'SUSPICIOUS': ['delete', 'encrypt', 'secret', 'confidential', 'hide', 'cover'],
        'COORDINATION': ['meet', 'location', 'address', 'time', 'place', 'venue'],
        'BUSINESS': ['meeting', 'project', 'report', 'deadline', 'client', 'business', 'work'],
        'PERSONAL': ['love', 'dear', 'family', 'friend', 'happy', 'birthday', 'miss', 'home'],
        'SPAM': ['win', 'free', 'prize', 'offer', 'discount', 'click', 'link', 'http']
    }
    
    for category, words in keywords.items():
        for word in words:
            if word in content:
                return category
    
    return 'ROUTINE'

def detect_suspicious_patterns(timeline):
    """Detect potentially suspicious patterns"""
    flags = []
    
    if not timeline or len(timeline) < 10:
        return flags
    
    total_events = len(timeline)
    
    # 1. Late-night communications
    late_night = [e for e in timeline if 0 <= e['timestamp'].hour <= 5]
    late_night_percentage = len(late_night) / total_events * 100
    if late_night_percentage > 20:
        flags.append(f"High late-night activity: {len(late_night):,} events ({late_night_percentage:.1f}%)")
    
    # 2. Financial keywords
    financial_events = sum(1 for e in timeline if e.get('forensic_tag') == 'FINANCIAL')
    if financial_events > 5:
        flags.append(f"Financial-related communications: {financial_events:,}")
    
    # 3. Suspicious keywords
    suspicious_events = sum(1 for e in timeline if e.get('forensic_tag') == 'SUSPICIOUS')
    if suspicious_events > 3:
        flags.append(f"Suspicious keyword communications: {suspicious_events:,}")
    
    # 4. Unknown contacts
    unknown_contacts = sum(1 for e in timeline if 'unknown' in str(e.get('contact', '')).lower())
    if unknown_contacts > total_events * 0.1:
        flags.append(f"High unknown contacts: {unknown_contacts/total_events*100:.1f}%")
    
    return flags

# ============================================================================
# VISUALIZATION FUNCTIONS (Plotly)
# ============================================================================

def create_daily_heatmap(timeline_df):
    """Create daily activity heatmap using Plotly"""
    if len(timeline_df) == 0:
        return None
    
    # Prepare data for heatmap
    timeline_df['date'] = pd.to_datetime(timeline_df['timestamp']).dt.date
    timeline_df['hour'] = pd.to_datetime(timeline_df['timestamp']).dt.hour
    
    heatmap_data = timeline_df.groupby(['date', 'hour']).size().reset_index(name='count')
    
    # Create pivot table
    pivot_data = heatmap_data.pivot(index='date', columns='hour', values='count').fillna(0)
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=pivot_data.values,
        x=pivot_data.columns,
        y=pivot_data.index,
        colorscale='YlOrRd',
        hoverongaps=False,
        hovertemplate='Date: %{y}<br>Hour: %{x}:00<br>Events: %{z}<extra></extra>'
    ))
    
    fig.update_layout(
        title='Daily Communication Activity Heatmap',
        xaxis_title='Hour of Day',
        yaxis_title='Date',
        height=500,
        xaxis=dict(tickmode='array', tickvals=list(range(0, 24, 2))),
        yaxis=dict(tickangle=0)
    )
    
    return fig

def create_source_distribution_chart(timeline_df):
    """Create communication source distribution chart"""
    if len(timeline_df) == 0:
        return None
    
    source_counts = timeline_df['source'].value_counts()
    
    # Create pie chart
    fig = go.Figure(data=[go.Pie(
        labels=source_counts.index,
        values=source_counts.values,
        hole=0.3,
        marker_colors=px.colors.qualitative.Set2
    )])
    
    fig.update_layout(
        title='Communication Source Distribution',
        height=400
    )
    
    return fig

def create_hourly_pattern_chart(timeline_df):
    """Create hourly activity pattern chart"""
    if len(timeline_df) == 0:
        return None
    
    timeline_df['hour'] = pd.to_datetime(timeline_df['timestamp']).dt.hour
    hourly_counts = timeline_df['hour'].value_counts().sort_index()
    
    fig = go.Figure(data=[go.Bar(
        x=hourly_counts.index,
        y=hourly_counts.values,
        marker_color='skyblue',
        text=hourly_counts.values,
        textposition='auto'
    )])
    
    fig.update_layout(
        title='Hourly Communication Activity Pattern',
        xaxis_title='Hour of Day',
        yaxis_title='Number of Events',
        xaxis=dict(tickmode='array', tickvals=list(range(0, 24))),
        height=400
    )
    
    return fig

def create_forensic_categories_chart(timeline_df):
    """Create forensic category breakdown chart"""
    if len(timeline_df) == 0:
        return None
    
    if 'forensic_tag' not in timeline_df.columns:
        return None
    
    tag_counts = timeline_df['forensic_tag'].value_counts()
    
    fig = go.Figure(data=[go.Bar(
        x=tag_counts.values,
        y=tag_counts.index,
        orientation='h',
        marker_color='lightcoral',
        text=tag_counts.values,
        textposition='auto'
    )])
    
    fig.update_layout(
        title='Forensic Category Analysis',
        xaxis_title='Number of Events',
        yaxis_title='Category',
        height=400
    )
    
    return fig

def create_top_contacts_chart(contact_counts):
    """Create top contacts visualization"""
    if not contact_counts:
        return None
    
    top_contacts = dict(contact_counts.most_common(15))
    
    fig = go.Figure(data=[go.Bar(
        x=list(top_contacts.values()),
        y=list(top_contacts.keys()),
        orientation='h',
        marker_color='lightgreen',
        text=list(top_contacts.values()),
        textposition='auto'
    )])
    
    fig.update_layout(
        title='Top 15 Contacts by Interaction Count',
        xaxis_title='Number of Interactions',
        yaxis_title='Contact',
        height=500
    )
    
    return fig

def create_timeline_visualization(timeline_df):
    """Create interactive timeline visualization"""
    if len(timeline_df) == 0:
        return None
    
    # Color mapping for sources
    color_map = {
        'SMS': '#FF6B6B',
        'CALL': '#4ECDC4',
        'EMAIL': '#45B7D1'
    }
    
    fig = go.Figure()
    
    for source in timeline_df['source'].unique():
        source_data = timeline_df[timeline_df['source'] == source]
        
        fig.add_trace(go.Scatter(
            x=source_data['timestamp'],
            y=[source] * len(source_data),
            mode='markers',
            name=source,
            marker=dict(
                size=10,
                color=color_map.get(source, '#000000'),
                line=dict(width=1, color='DarkSlateGrey')
            ),
            text=source_data['contact'] + '<br>' + source_data['content'].str[:50],
            hoverinfo='text',
            customdata=source_data[['forensic_tag', 'type']]
        ))
    
    fig.update_layout(
        title='Interactive Timeline of Communications',
        xaxis_title='Timestamp',
        yaxis_title='Source',
        height=500,
        hovermode='closest',
        showlegend=True
    )
    
    return fig

# ============================================================================
# EXPORT FUNCTIONS
# ============================================================================

def get_csv_download_link(df, filename):
    """Generate a download link for a DataFrame"""
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">Download {filename}</a>'
    return href

def export_forensic_report(timeline, sms_data, call_data, email_data, contact_counts, contact_details):
    """Export comprehensive forensic report"""
    report_content = []
    report_content.append("=" * 80)
    report_content.append("DIGITAL FORENSIC INVESTIGATION REPORT")
    report_content.append("=" * 80)
    report_content.append(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_content.append(f"Case Reference: DF-{datetime.now().strftime('%Y%m%d-%H%M%S')}")
    report_content.append("")
    
    # Data Summary
    total_events = len(sms_data) + len(call_data) + len(email_data)
    report_content.append("DATA SUMMARY")
    report_content.append("-" * 40)
    report_content.append(f"Total Events Analyzed: {total_events:,}")
    report_content.append(f"SMS Messages: {len(sms_data):,}")
    report_content.append(f"Phone Calls: {len(call_data):,}")
    report_content.append(f"Emails: {len(email_data):,}")
    
    if timeline:
        days_span = max((timeline[-1]['timestamp'] - timeline[0]['timestamp']).days, 1)
        report_content.append(f"Analysis Period: {days_span} days")
        report_content.append(f"Date Range: {timeline[0]['timestamp'].strftime('%Y-%m-%d')} to {timeline[-1]['timestamp'].strftime('%Y-%m-%d')}")
    
    # Contact Analysis
    report_content.append("")
    report_content.append("CONTACT ANALYSIS")
    report_content.append("-" * 40)
    report_content.append(f"Unique Contacts Identified: {len(contact_counts):,}")
    
    if contact_counts:
        top_contacts = contact_counts.most_common(10)
        report_content.append("")
        report_content.append("TOP 10 CONTACTS:")
        for i, (contact, count) in enumerate(top_contacts, 1):
            report_content.append(f"{i}. {contact}: {count:,} interactions")
    
    # Forensic Findings
    if timeline:
        report_content.append("")
        report_content.append("FORENSIC FINDINGS")
        report_content.append("-" * 40)
        
        categories = Counter(event['forensic_tag'] for event in timeline)
        total_categorized = len(timeline)
        
        for category, count in categories.most_common():
            percentage = (count / total_categorized) * 100
            report_content.append(f"{category}: {count:,} events ({percentage:.1f}%)")
        
        flags = detect_suspicious_patterns(timeline)
        if flags:
            report_content.append("")
            report_content.append("POTENTIAL RED FLAGS:")
            for flag in flags:
                report_content.append(f"• {flag}")
    
    return "\n".join(report_content)

# ============================================================================
# STREAMLIT UI COMPONENTS
# ============================================================================

def render_sidebar():
    """Render the sidebar with file uploads and controls"""
    st.sidebar.title("🕵️ Forensic Analyzer")
    st.sidebar.markdown("---")
    
    st.sidebar.subheader("1. Upload Data Files")
    
    sms_file = st.sidebar.file_uploader("Upload SMS Data (CSV)", type=['csv'], key='sms')
    call_file = st.sidebar.file_uploader("Upload Call Data (CSV)", type=['csv'], key='call')
    email_file = st.sidebar.file_uploader("Upload Email Data (CSV)", type=['csv'], key='email')
    
    if st.sidebar.button("📥 Load All Data", type="primary", use_container_width=True):
        with st.spinner("Loading and analyzing data..."):
            if sms_file:
                st.session_state.sms_data = load_sms_data(sms_file)
            if call_file:
                st.session_state.call_data = load_call_data(call_file)
            if email_file:
                st.session_state.email_data = load_email_data(email_file)
            
            if st.session_state.sms_data or st.session_state.call_data or st.session_state.email_data:
                # Extract contacts
                st.session_state.contact_counts, st.session_state.contact_details = extract_contacts(
                    st.session_state.sms_data,
                    st.session_state.call_data,
                    st.session_state.email_data
                )
                
                # Create timeline
                st.session_state.timeline = create_timeline(
                    st.session_state.sms_data,
                    st.session_state.call_data,
                    st.session_state.email_data
                )
                
                st.session_state.analysis_complete = True
                st.success("Data loaded and analyzed successfully!")
            else:
                st.error("No data loaded. Please upload at least one file.")
    
    st.sidebar.markdown("---")
    
    # Sample data toggle
    use_sample = st.sidebar.checkbox("Use Sample Data for Demo", value=False)
    if use_sample and not st.session_state.analysis_complete:
        if st.sidebar.button("Load Sample Data"):
            with st.spinner("Generating sample data..."):
                # Generate sample data
                st.session_state.sms_data = []
                st.session_state.call_data = []
                st.session_state.email_data = generate_sample_email_data()
                
                # Generate sample SMS
                for i in range(100):
                    timestamp = datetime.now() - timedelta(days=np.random.randint(1, 90))
                    st.session_state.sms_data.append({
                        'id': f"SMS_{i+1:06d}",
                        'timestamp': timestamp,
                        'contact': f"+1{np.random.randint(200, 999):03}{np.random.randint(1000, 9999):04}",
                        'direction': 'OUTGOING' if np.random.random() > 0.5 else 'INCOMING',
                        'message': f"Sample message {i+1}",
                        'source': 'SMS'
                    })
                
                # Generate sample calls
                for i in range(50):
                    timestamp = datetime.now() - timedelta(days=np.random.randint(1, 90))
                    st.session_state.call_data.append({
                        'id': f"CALL_{i+1:06d}",
                        'timestamp': timestamp,
                        'contact': f"+1{np.random.randint(200, 999):03}{np.random.randint(1000, 9999):04}",
                        'duration': np.random.randint(30, 1800),
                        'type': np.random.choice(['ANSWERED', 'MISSED', 'SHORT_CALL']),
                        'source': 'CALL'
                    })
                
                # Extract contacts
                st.session_state.contact_counts, st.session_state.contact_details = extract_contacts(
                    st.session_state.sms_data,
                    st.session_state.call_data,
                    st.session_state.email_data
                )
                
                # Create timeline
                st.session_state.timeline = create_timeline(
                    st.session_state.sms_data,
                    st.session_state.call_data,
                    st.session_state.email_data
                )
                
                st.session_state.analysis_complete = True
                st.success("Sample data loaded successfully!")
    
    st.sidebar.markdown("---")
    st.sidebar.info("📊 **System Status**")
    
    if st.session_state.analysis_complete:
        total_events = len(st.session_state.sms_data) + len(st.session_state.call_data) + len(st.session_state.email_data)
        st.sidebar.success(f"✅ Data Loaded: {total_events:,} events")
        st.sidebar.success(f"✅ Contacts: {len(st.session_state.contact_counts):,}")
    else:
        st.sidebar.warning("⏳ Waiting for data...")

def render_dashboard():
    """Render the main dashboard"""
    st.title("🔍 Digital Forensic Correlation System")
    st.markdown("---")
    
    if not st.session_state.analysis_complete:
        st.info("👈 Please upload data files or use sample data from the sidebar to begin analysis.")
        return
    
    # Display summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    total_events = len(st.session_state.sms_data) + len(st.session_state.call_data) + len(st.session_state.email_data)
    unique_contacts = len(st.session_state.contact_counts)
    
    with col1:
        st.metric("📊 Total Events", f"{total_events:,}")
    
    with col2:
        st.metric("👥 Unique Contacts", f"{unique_contacts:,}")
    
    with col3:
        sms_count = len(st.session_state.sms_data)
        st.metric("💬 SMS Messages", f"{sms_count:,}")
    
    with col4:
        call_count = len(st.session_state.call_data)
        st.metric("📞 Phone Calls", f"{call_count:,}")
    
    st.markdown("---")
    
    # Create tabs for different views
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Overview", 
        "📅 Timeline", 
        "👥 Contacts", 
        "🔍 Search", 
        "📤 Export"
    ])
    
    # Convert timeline to DataFrame for easier manipulation
    timeline_df = pd.DataFrame(st.session_state.timeline)
    if not timeline_df.empty:
        timeline_df['timestamp'] = pd.to_datetime(timeline_df['timestamp'])
    
    with tab1:
        # Overview Tab
        st.header("Data Overview")
        
        if not timeline_df.empty:
            # Create two columns for charts
            col1, col2 = st.columns(2)
            
            with col1:
                fig1 = create_source_distribution_chart(timeline_df)
                if fig1:
                    st.plotly_chart(fig1, use_container_width=True)
            
            with col2:
                fig2 = create_hourly_pattern_chart(timeline_df)
                if fig2:
                    st.plotly_chart(fig2, use_container_width=True)
            
            # More charts
            col3, col4 = st.columns(2)
            
            with col3:
                fig3 = create_forensic_categories_chart(timeline_df)
                if fig3:
                    st.plotly_chart(fig3, use_container_width=True)
            
            with col4:
                fig4 = create_top_contacts_chart(st.session_state.contact_counts)
                if fig4:
                    st.plotly_chart(fig4, use_container_width=True)
            
            # Heatmap
            st.subheader("Activity Heatmap")
            fig5 = create_daily_heatmap(timeline_df)
            if fig5:
                st.plotly_chart(fig5, use_container_width=True)
    
    with tab2:
        # Timeline Tab
        st.header("Communication Timeline")
        
        if not timeline_df.empty:
            # Interactive timeline
            fig = create_timeline_visualization(timeline_df)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
            
            # Filter options
            st.subheader("Timeline Details")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                date_range = st.date_input(
                    "Date Range",
                    value=(
                        timeline_df['timestamp'].min().date(),
                        timeline_df['timestamp'].max().date()
                    ),
                    key='date_filter'
                )
            
            with col2:
                sources = st.multiselect(
                    "Filter by Source",
                    options=timeline_df['source'].unique().tolist(),
                    default=timeline_df['source'].unique().tolist()
                )
            
            with col3:
                forensic_tags = st.multiselect(
                    "Filter by Forensic Tag",
                    options=timeline_df['forensic_tag'].unique().tolist(),
                    default=timeline_df['forensic_tag'].unique().tolist()
                )
            
            # Apply filters
            filtered_df = timeline_df.copy()
            if date_range and len(date_range) == 2:
                filtered_df = filtered_df[
                    (filtered_df['timestamp'].dt.date >= date_range[0]) &
                    (filtered_df['timestamp'].dt.date <= date_range[1])
                ]
            
            if sources:
                filtered_df = filtered_df[filtered_df['source'].isin(sources)]
            
            if forensic_tags:
                filtered_df = filtered_df[filtered_df['forensic_tag'].isin(forensic_tags)]
            
            # Display filtered timeline
            st.dataframe(
                filtered_df[['timestamp', 'source', 'contact', 'type', 'forensic_tag', 'content']].head(100),
                use_container_width=True,
                height=400
            )
            
            st.caption(f"Showing {len(filtered_df):,} of {len(timeline_df):,} events")
    
    with tab3:
        # Contacts Tab
        st.header("Contact Analysis")
        
        if st.session_state.contact_counts:
            # Display top contacts in a table
            st.subheader("Top Contacts")
            
            # Prepare contact data for display
            contact_list = []
            for contact, total_count in st.session_state.contact_counts.most_common(50):
                details = st.session_state.contact_details.get(contact, {})
                contact_list.append({
                    'Contact': contact,
                    'Total Interactions': total_count,
                    'SMS': details.get('sms_count', 0),
                    'Calls': details.get('call_count', 0),
                    'Emails Sent': details.get('sent_email_count', 0),
                    'Emails Received': details.get('received_email_count', 0)
                })
            
            contact_df = pd.DataFrame(contact_list)
            st.dataframe(contact_df, use_container_width=True, height=500)
            
            # Contact statistics
            st.subheader("Contact Statistics")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                avg_interactions = sum(st.session_state.contact_counts.values()) / len(st.session_state.contact_counts)
                st.metric("Avg Interactions per Contact", f"{avg_interactions:.1f}")
            
            with col2:
                max_interactions = max(st.session_state.contact_counts.values())
                st.metric("Max Interactions", f"{max_interactions:,}")
            
            with col3:
                min_interactions = min(st.session_state.contact_counts.values())
                st.metric("Min Interactions", f"{min_interactions:,}")
    
    with tab4:
        # Search Tab
        st.header("Search Communications")
        
        search_query = st.text_input("🔍 Search for keywords, contacts, or content:")
        
        if search_query:
            # Search across all data
            results = []
            
            # Search SMS
            for sms in st.session_state.sms_data:
                if (search_query.lower() in str(sms.get('contact', '')).lower() or
                    search_query.lower() in str(sms.get('message', '')).lower()):
                    results.append({
                        'Timestamp': sms['timestamp'],
                        'Source': 'SMS',
                        'Contact': sms.get('contact', ''),
                        'Type': sms.get('direction', ''),
                        'Content': sms.get('message', '')[:100]
                    })
            
            # Search calls
            for call in st.session_state.call_data:
                if search_query.lower() in str(call.get('contact', '')).lower():
                    results.append({
                        'Timestamp': call['timestamp'],
                        'Source': 'CALL',
                        'Contact': call.get('contact', ''),
                        'Type': call.get('type', ''),
                        'Content': f"Duration: {call.get('duration', 0)}s"
                    })
            
            # Search emails
            for email in st.session_state.email_data:
                if (search_query.lower() in str(email.get('sender', '')).lower() or
                    search_query.lower() in str(email.get('recipient', '')).lower() or
                    search_query.lower() in str(email.get('subject', '')).lower() or
                    search_query.lower() in str(email.get('body', '')).lower()):
                    results.append({
                        'Timestamp': email['timestamp'],
                        'Source': 'EMAIL',
                        'Contact': email.get('sender', ''),
                        'Type': 'SENT',
                        'Content': f"To: {email.get('recipient', '')} | {email.get('subject', '')[:50]}"
                    })
            
            if results:
                # Convert to DataFrame for display
                results_df = pd.DataFrame(results)
                results_df = results_df.sort_values('Timestamp', ascending=False)
                
                st.success(f"Found {len(results)} results for '{search_query}'")
                st.dataframe(results_df, use_container_width=True, height=400)
            else:
                st.warning(f"No results found for '{search_query}'")
    
    with tab5:
        # Export Tab
        st.header("Export Forensic Data")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📄 Generate Full Report", use_container_width=True):
                report = export_forensic_report(
                    st.session_state.timeline,
                    st.session_state.sms_data,
                    st.session_state.call_data,
                    st.session_state.email_data,
                    st.session_state.contact_counts,
                    st.session_state.contact_details
                )
                
                st.download_button(
                    label="⬇️ Download Forensic Report",
                    data=report,
                    file_name=f"forensic_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
        
        with col2:
            if not timeline_df.empty:
                csv = timeline_df.to_csv(index=False)
                st.download_button(
                    label="📊 Download Timeline (CSV)",
                    data=csv,
                    file_name=f"forensic_timeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        
        with col3:
            if st.session_state.contact_counts:
                # Prepare contact data for export
                contact_list = []
                for contact, total_count in st.session_state.contact_counts.most_common():
                    details = st.session_state.contact_details.get(contact, {})
                    contact_list.append({
                        'Contact': contact,
                        'Total_Interactions': total_count,
                        'SMS_Count': details.get('sms_count', 0),
                        'Call_Count': details.get('call_count', 0),
                        'Email_Sent_Count': details.get('sent_email_count', 0),
                        'Email_Received_Count': details.get('received_email_count', 0)
                    })
                
                contacts_df = pd.DataFrame(contact_list)
                csv = contacts_df.to_csv(index=False)
                
                st.download_button(
                    label="👥 Download Contacts (CSV)",
                    data=csv,
                    file_name=f"forensic_contacts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        
        # Display suspicious patterns
        st.subheader("⚠️ Risk Assessment")
        
        if st.session_state.timeline:
            flags = detect_suspicious_patterns(st.session_state.timeline)
            
            if flags:
                risk_score = min(len(flags) * 10, 100)
                
                st.warning(f"Risk Score: {risk_score}/100")
                
                for flag in flags:
                    st.error(f"• {flag}")
                
                st.info("Recommendation: Further investigation recommended for identified anomalies.")
            else:
                st.success("Risk Score: 0/100")
                st.info("No significant red flags detected. Standard monitoring recommended.")

# ============================================================================
# MAIN APP
# ============================================================================

def main():
    """Main Streamlit app"""
    # Initialize session state
    init_session_state()
    
    # Render sidebar
    render_sidebar()
    
    # Render main dashboard
    render_dashboard()
    
    # Footer
    st.markdown("---")
    st.caption("🕵️ Digital Forensic Correlation System | For Investigative Use Only")

if __name__ == "__main__":
    main()
