import json
import sys
import os
import atexit
import logging
from datetime import datetime, timedelta
import shutil
from anthropic import Anthropic
import time
from collections import deque
import threading
from typing import Dict, Deque
import math

# Set up logging
logging.basicConfig(
    filename='hadis_processor.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class RateLimiter:
    def __init__(self):
        self.requests_per_min = 1000
        self.tokens_per_min = 100000
        self.tokens_per_day = 25000000
        
        # Track requests
        self.request_times: Deque[float] = deque()
        self.token_usage_min: Deque[Dict] = deque()
        self.token_usage_day: Deque[Dict] = deque()
        
        # Lock for thread safety
        self.lock = threading.Lock()
        
        # Track total tokens used today
        self.total_tokens_today = 0
        self.day_start = datetime.now()
        
    def reset_daily_tokens(self):
        current_time = datetime.now()
        if (current_time - self.day_start).days >= 1:
            self.total_tokens_today = 0
            self.day_start = current_time
            self.token_usage_day.clear()
    
    def wait_if_needed(self, estimated_tokens: int):
        with self.lock:
            current_time = time.time()
            minute_ago = current_time - 60
            
            # Clean up old entries
            while self.request_times and self.request_times[0] < minute_ago:
                self.request_times.popleft()
            while self.token_usage_min and self.token_usage_min[0]['time'] < minute_ago:
                self.token_usage_min.popleft()
                
            # Check and reset daily tokens
            self.reset_daily_tokens()
            
            # Calculate current usage
            current_requests = len(self.request_times)
            current_tokens = sum(usage['tokens'] for usage in self.token_usage_min)
            
            # Calculate wait time needed
            wait_time = 0
            
            # Check request rate limit
            if current_requests >= self.requests_per_min:
                wait_time = max(wait_time, self.request_times[0] + 60 - current_time)
            
            # Check token rate limit
            if current_tokens + estimated_tokens > self.tokens_per_min:
                wait_time = max(wait_time, self.token_usage_min[0]['time'] + 60 - current_time)
            
            # Check daily token limit
            if self.total_tokens_today + estimated_tokens > self.tokens_per_day:
                logging.warning("Approaching daily token limit. Sleeping until next day.")
                tomorrow = self.day_start + timedelta(days=1)
                wait_time = max(wait_time, (tomorrow - datetime.now()).total_seconds())
            
            # If wait needed, sleep
            if wait_time > 0:
                logging.info(f"Rate limit approaching. Waiting {wait_time:.2f} seconds")
                time.sleep(wait_time)
            
            # Record this request
            self.request_times.append(current_time)
            self.token_usage_min.append({
                'time': current_time,
                'tokens': estimated_tokens
            })
            self.total_tokens_today += estimated_tokens

# Initialize rate limiter
rate_limiter = RateLimiter()

def get_api_key():
    """Read API key from haikukey.txt file"""
    try:
        with open('haikukey.txt', 'r') as f:
            return f.read().strip()
    except Exception as e:
        logging.error(f"Error reading API key: {str(e)}")
        print(f"Error reading API key: {str(e)}")
        return None

def backup_output_file(output_file):
    """Create a backup of the output file"""
    if os.path.exists(output_file):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"{output_file}.{timestamp}.backup"
        shutil.copy2(output_file, backup_file)
        logging.info(f"Created backup: {backup_file}")

def append_to_output(item, output_file):
    """Append a single processed item to the output file with backup"""
    try:
        # Create backup before modification
        backup_output_file(output_file)
        
        # Read existing data if file exists
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = []

        # Append new item
        data.append(item)

        # Write back to file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            
        logging.info(f"Successfully processed and saved hadis_id: {item.get('hadis_id')}")

    except Exception as e:
        logging.error(f"Error appending to output file: {str(e)}")
        raise

def get_last_processed_id(output_file):
    """Get the hadis_id of the last processed item"""
    try:
        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if data:
                last_id = data[-1].get('hadis_id')
                logging.info(f"Found last processed hadis_id: {last_id}")
                return last_id
    except (FileNotFoundError, json.JSONDecodeError):
        logging.info("No previous progress found")
        pass
    return None

def extract_details(client, hadis, terjemahan):
    logging.info("Starting extraction of details")
    
    # Estimate tokens for each request (adjust these based on actual usage patterns)
    estimated_tokens = {
        'perawi_ar': 500,
        'perawi_id': 500,
        'premis': 500,
        'topik': 500
    }
    
    try:
        # Extract Perawi_Ar
        rate_limiter.wait_if_needed(estimated_tokens['perawi_ar'])
        message = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1024,
            temperature=0,
            messages=[
                {"role": "user", "content": f"Ekstrak nama-nama tokoh yang menjadi jalur hadis secara urut dalam bahasa Arab dari teks berikut, pisahkan dengan koma tanpa nomor urut, tanpa menambahkan kalimat pengantar atau format apapun: {hadis}"}
            ]
        )
        perawi_ar = message.content[0].text.strip()

        # Extract Perawi_Id
        rate_limiter.wait_if_needed(estimated_tokens['perawi_id'])
        message = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1024,
            temperature=0,
            messages=[
                {"role": "user", "content": f"Ekstrak nama-nama tokoh yang menjadi jalur hadis secara urut dalam bahasa Indonesia dari teks berikut, pisahkan dengan koma tanpa nomor urut, tanpa menambahkan kalimat pengantar atau format apapun: {terjemahan}"}
            ]
        )
        perawi_id = message.content[0].text.strip()

        # Extract Premis
        rate_limiter.wait_if_needed(estimated_tokens['premis'])
        message = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1024,
            temperature=0,
            messages=[
                {"role": "user", "content": f"Ekstrak kalimat inti hadis dari teks berikut tanpa menambahkan kalimat pengantar atau format apapun: {terjemahan}"}
            ]
        )
        premis = message.content[0].text.strip()

        # Extract Topik
        rate_limiter.wait_if_needed(estimated_tokens['topik'])
        message = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1024,
            temperature=0,
            messages=[
                {"role": "user", "content": f"""Ekstrak 1-10 topik yang dibahas dalam hadis berikut dalam bentuk kata atau frasa (bukan kalimat), dipisahkan dengan koma. 
                Topik harus berupa konsep, nilai, prinsip, atau hal non-person (boleh lokasi atau waktu). 
                Jangan masukkan nama-nama orang berikut ini ke dalam topik: {perawi_id}. 
                Jangan tambahkan kalimat pengantar atau penjelasan apapun. 
                Teks hadis: {terjemahan}"""}
            ]
        )
        topik = message.content[0].text.strip()

        # Filter out any remaining topics that match perawi names
        perawi_list = [name.strip().lower() for name in perawi_id.split(',')]
        topik_list = [t.strip() for t in topik.split(',')]
        filtered_topik = [t for t in topik_list if t.lower() not in perawi_list]
        topik = ', '.join(filtered_topik)

        logging.info("Successfully extracted all details")
        return perawi_ar, perawi_id, premis, topik

    except Exception as e:
        if "rate limit" in str(e).lower():
            logging.warning(f"Rate limit hit: {str(e)}")
            # Add extra delay if rate limit is hit
            time.sleep(65)  # Wait slightly over a minute
            raise Exception("Rate limit hit, retrying after delay")
        else:
            raise

def process_json(input_file, output_file):
    try:
        logging.info("Starting hadis processing")
        
        # Read input file
        logging.info("Loading input file...")
        with open(input_file, 'r', encoding='utf-8') as f:
            input_data = json.load(f)

        # Get the last processed hadis_id
        last_processed_id = get_last_processed_id(output_file)
        start_processing = False if last_processed_id else True

        # Initialize Anthropic client
        api_key = get_api_key()
        if not api_key:
            raise Exception("Failed to read API key from haikukey.txt")
        client = Anthropic(api_key=api_key)

        # Define the stop_id
        stop_id = "ha62169"

        # Process each entry
        total_items = len(input_data)
        retry_count = 0
        max_retries = 3

        for i, item in enumerate(input_data):
            current_hadis_id = item.get('hadis_id')

            if not start_processing:
                if current_hadis_id == last_processed_id:
                    start_processing = True
                    logging.info(f"Resuming from hadis_id: {current_hadis_id}")
                    print(f"Resuming from hadis_id: {current_hadis_id}")
                continue

            print(f"\nProcessing item {i+1} of {total_items} (hadis_id: {current_hadis_id})...")
            logging.info(f"Processing hadis_id: {current_hadis_id} ({i+1}/{total_items})")

            # Extract details with retry logic
            while retry_count < max_retries:
                try:
                    hadis = item.get('Hadis', '')
                    terjemahan = item.get('Terjemahan', '')
                    perawi_ar, perawi_id, premis, topik = extract_details(client, hadis, terjemahan)
                    retry_count = 0  # Reset counter on success
                    break
                except Exception as e:
                    retry_count += 1
                    if retry_count >= max_retries:
                        logging.error(f"Failed after {max_retries} attempts for hadis_id {current_hadis_id}")
                        raise
                    logging.warning(f"Retry {retry_count} for hadis_id {current_hadis_id}")
                    time.sleep(5 * retry_count)  # Incremental backoff

            print(f"Extracted data for item {i+1}:")
            print(f"Perawi_Ar: {perawi_ar}")
            print(f"Perawi_Id: {perawi_id}")
            print(f"Premis: {premis}")
            print(f"Topik: {topik}")
            print("-" * 50)

            # Update item with extracted data
            item['Perawi_Ar'] = perawi_ar
            item['Perawi_Id'] = perawi_id
            item['Premis'] = premis
            item['Topik'] = topik

            # Append processed item to output file
            append_to_output(item, output_file)

            # Check if we need to stop processing
            if current_hadis_id == stop_id:
                logging.info(f"Reached stop_id: {stop_id}. Stopping processing.")
                print(f"Reached stop_id: {stop_id}. Stopping processing.")
                break

        logging.info("Processing complete!")
        print("\nProcessing complete!")

    except KeyboardInterrupt:
        logging.info("Process interrupted by user")
        print("\nProcess safely interrupted. Progress has been saved.")
        sys.exit(0)
        
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        print(f"\nUnexpected error occurred. Check hadis_processor.log for details")
        print(f"Error details: {str(e)}")
        sys.exit(1)

def cleanup():
    """Cleanup function that runs on exit"""
    logging.info("Cleaning up resources...")
    # Create final backup
    backup_output_file('anotasihadis.json')
    logging.info("Process completed")

atexit.register(cleanup)

if __name__ == "__main__":
    input_file = 'terjemahhadis.json'
    output_file = 'anotasihadis.json'
    process_json(input_file, output_file)