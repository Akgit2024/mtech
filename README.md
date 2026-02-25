# Multi-Source Event Reconstruction System 

A comprehensive digital forensics analysis tool that reconstructs and analyzes communication patterns across SMS, phone calls, and emails. This system provides automated detection of suspicious activities, multi-channel communication patterns, and generates detailed forensic reports.

## 🚀 Features

### Data Processing
- **Multi-Format Support**: Automatically loads and processes data from CSV and JSON files
- **Smart File Detection**: Automatically identifies and loads relevant data files from the current directory
- **Flexible Schema Handling**: Adapts to various data structures and column naming conventions

### Core Analysis Capabilities

#### 1. **Unified Timeline Reconstruction**
- Merges communications from all sources into a single chronological timeline
- Tracks source/destination relationships with clear direction indicators
- Identifies user's phone number through pattern analysis

#### 2. **Forensic Classification**
Automatically categorizes communications into:
- `SUSPICIOUS` - Contains suspicious keywords or patterns
- `FINANCIAL` - Payment, banking, or money-related communications
- `URGENT` - Time-sensitive or emergency communications
- `INTERNATIONAL` - Cross-border communications
- `EXTENDED_COMM` - Unusually long communications
- `SPAM` - Suspicious marketing or phishing attempts
- `ROUTINE` - Normal, non-suspicious communications

#### 3. **Multi-Channel Pattern Detection**
- Identifies coordinated communications across SMS, calls, and emails
- Detects sequential patterns (e.g., SMS → Call → Email)
- Risk assessment based on channel combinations and volume
- Timeline analysis of communication sequences

#### 4. **Risk Assessment Engine**
- Calculates risk scores based on multiple factors:
  - Volume of suspicious communications
  - Presence of high-risk categories
  - Late-night activity patterns
  - Contact concentration
  - Multi-channel patterns
- Provides detailed explanations for each risk factor

#### 5. **Comprehensive Reporting**
- **Text Reports**: Detailed forensic analysis with executive summaries
- **CSV Exports**: Timeline data and contact analysis
- **JSON Summary**: Machine-readable forensic summary
- **Visualizations**: Activity patterns and distribution charts

## 📊 Visualization Capabilities

- Communication source distribution (pie/bar charts)
- Hourly activity patterns
- Day-of-week analysis
- Forensic category distribution
- Interactive Jupyter dashboard (when available)

## 🛠️ Installation

```bash
# Clone the repository
git clone https://github.com/Akgit2024/Multi-Source.git
cd Multi-Source

# Install required packages
pip install pandas numpy matplotlib seaborn ipywidgets
```
### 📁 Required Data Files

The system automatically detects and loads data from:
SMS Data

   # - SMS-Data.csv, sms_data.csv

   # - sms.json, SMS.json, sms_messages.json

Call Data (CDR)

   # - CDR-Call-Details.csv, call_data.csv, CallDetails.csv

   # - calls.json, call_log.json, cdr.json

Email Data

   # - emails.csv, email_data.csv

   # - emails.json, email_data.json, mail.json

### 🚀 Usage
  Run the main analysis
  
  python forensic_analyzer.py

### Interactive Menu Options

   # - Timeline Events - View all communications with source/destination details

   # - Detailed Analysis - In-depth communication flow and pattern analysis

   # - Suspicious Communications - Focused analysis of flagged communications

   # - Multi-Channel Patterns - Detect coordinated communication sequences

   # - Visualizations - Generate activity charts and graphs

   # - Export Report - Save comprehensive forensic reports

   # - Exit - End the analysis session

### 📄 License

MIT License - Feel free to use and modify for your forensic needs.

### ⚠️ Disclaimer

This tool is designed for legitimate forensic and security analysis purposes. Users are responsible for complying with all applicable laws and regulations regarding data privacy and surveillance.
