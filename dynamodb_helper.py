import boto3
import json
import logging
import time
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from botocore.exceptions import ClientError, NoCredentialsError

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# DynamoDB Configuration
TABLE_NAME = "website-scrapes"
REGION = "us-east-1"

# Initialize DynamoDB client
try:
    dynamodb = boto3.resource('dynamodb', region_name=REGION)
    table = dynamodb.Table(TABLE_NAME)
    print(f"✅ DynamoDB client initialized for table: {TABLE_NAME}")
except Exception as e:
    print(f"❌ Failed to initialize DynamoDB client: {str(e)}")
    table = None

def generate_project_id():
    """Generate a unique project ID with timestamp"""
    timestamp = int(time.time())
    unique_id = str(uuid.uuid4())[:8]
    return f"proj_{timestamp}_{unique_id}"

def save_scrape_data(user_id, project_id, url, scrape_data):
    """
    Save website scrape data to DynamoDB
    
    Args:
        user_id (str): User identifier
        project_id (str): Unique project identifier
        url (str): The scraped URL
        scrape_data (dict): Complete scraping results
    
    Returns:
        bool: True if successful, False otherwise
    """
    if not table:
        logger.error("❌ DynamoDB table not available")
        return False
    
    try:
        # Convert float values to integers for DynamoDB compatibility
        def convert_floats_to_ints(obj):
            if isinstance(obj, dict):
                return {k: convert_floats_to_ints(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_floats_to_ints(item) for item in obj]
            elif isinstance(obj, float):
                return int(obj)
            else:
                return obj
        
        # Convert the scrape data to be DynamoDB compatible
        dynamodb_compatible_data = convert_floats_to_ints(scrape_data)
        
        # Prepare the item for DynamoDB
        item = {
            'user_id': user_id,
            'project_id': project_id,
            'url': url,
            'scraped_at': int(time.time()),
            'scrape_data': dynamodb_compatible_data,
            'status': 'success'
        }
        
        # Save to DynamoDB
        table.put_item(Item=item)
        
        logger.info(f"✅ Saved scrape data for user {user_id}, project {project_id}")
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        logger.error(f"❌ DynamoDB error saving data: {error_code} - {str(e)}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error saving data: {str(e)}")
        return False

def get_user_scrapes(user_id, limit=50):
    """
    Get all scrapes for a specific user
    
    Args:
        user_id (str): User identifier
        limit (int): Maximum number of items to return
    
    Returns:
        list: List of scrape data items, or empty list if error
    """
    if not table:
        logger.error("❌ DynamoDB table not available")
        return []
    
    try:
        response = table.query(
            KeyConditionExpression='user_id = :uid',
            ExpressionAttributeValues={':uid': user_id},
            ScanIndexForward=False,  # Most recent first
            Limit=limit
        )
        
        items = response.get('Items', [])
        logger.info(f"✅ Retrieved {len(items)} scrapes for user {user_id}")
        return items
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        logger.error(f"❌ DynamoDB error retrieving user scrapes: {error_code} - {str(e)}")
        return []
    except Exception as e:
        logger.error(f"❌ Unexpected error retrieving user scrapes: {str(e)}")
        return []

def get_project(user_id, project_id):
    """
    Get a specific project for a user
    
    Args:
        user_id (str): User identifier
        project_id (str): Project identifier
    
    Returns:
        dict: Project data, or None if not found or error
    """
    if not table:
        logger.error("❌ DynamoDB table not available")
        return None
    
    try:
        response = table.get_item(
            Key={
                'user_id': user_id,
                'project_id': project_id
            }
        )
        
        item = response.get('Item')
        if item:
            logger.info(f"✅ Retrieved project {project_id} for user {user_id}")
            return item
        else:
            logger.info(f"ℹ️ Project {project_id} not found for user {user_id}")
            return None
            
    except ClientError as e:
        error_code = e.response['Error']['Code']
        logger.error(f"❌ DynamoDB error retrieving project: {error_code} - {str(e)}")
        return None
    except Exception as e:
        logger.error(f"❌ Unexpected error retrieving project: {str(e)}")
        return None

def delete_project(user_id, project_id):
    """
    Delete a specific project for a user
    
    Args:
        user_id (str): User identifier
        project_id (str): Project identifier
    
    Returns:
        bool: True if successful, False otherwise
    """
    if not table:
        logger.error("❌ DynamoDB table not available")
        return False
    
    try:
        table.delete_item(
            Key={
                'user_id': user_id,
                'project_id': project_id
            }
        )
        
        logger.info(f"✅ Deleted project {project_id} for user {user_id}")
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        logger.error(f"❌ DynamoDB error deleting project: {error_code} - {str(e)}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error deleting project: {str(e)}")
        return False

def list_recent_user_scrapes(user_id, days=7):
    """
    Get recent scrapes for a user within specified days
    
    Args:
        user_id (str): User identifier
        days (int): Number of days to look back
    
    Returns:
        list: List of recent scrape data items
    """
    if not table:
        logger.error("❌ DynamoDB table not available")
        return []
    
    try:
        # Calculate cutoff timestamp
        cutoff_time = int((datetime.now() - timedelta(days=days)).timestamp())
        
        # Get all user scrapes and filter by date
        all_scrapes = get_user_scrapes(user_id, limit=1000)  # Get more items to filter
        
        # Filter by date
        recent_scrapes = [
            scrape for scrape in all_scrapes 
            if scrape.get('scraped_at', 0) >= cutoff_time
        ]
        
        logger.info(f"✅ Retrieved {len(recent_scrapes)} recent scrapes for user {user_id}")
        return recent_scrapes
        
    except Exception as e:
        logger.error(f"❌ Error retrieving recent scrapes: {str(e)}")
        return []

def save_failed_scrape(user_id, project_id, url, error_message):
    """
    Save information about a failed scrape
    
    Args:
        user_id (str): User identifier
        project_id (str): Project identifier
        url (str): The URL that failed
        error_message (str): Error description
    
    Returns:
        bool: True if successful, False otherwise
    """
    if not table:
        logger.error("❌ DynamoDB table not available")
        return False
    
    try:
        item = {
            'user_id': user_id,
            'project_id': project_id,
            'url': url,
            'scraped_at': int(time.time()),
            'scrape_data': {},
            'status': 'failed',
            'error_message': error_message
        }
        
        table.put_item(Item=item)
        
        logger.info(f"✅ Saved failed scrape data for user {user_id}, project {project_id}")
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        logger.error(f"❌ DynamoDB error saving failed scrape: {error_code} - {str(e)}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error saving failed scrape: {str(e)}")
        return False

def get_table_stats():
    """
    Get basic statistics about the DynamoDB table
    
    Returns:
        dict: Table statistics, or None if error
    """
    if not table:
        logger.error("❌ DynamoDB table not available")
        return None
    
    try:
        # Use the table meta attribute to get table description
        table.meta.client.describe_table(TableName=TABLE_NAME)
        table.reload()  # Refresh table metadata
        
        stats = {
            'table_name': table.name,
            'table_status': table.table_status,
            'item_count': table.item_count,
            'table_size_bytes': table.table_size_bytes,
            'creation_date': str(table.creation_date_time)
        }
        
        logger.info(f"✅ Retrieved table stats: {stats}")
        return stats
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        logger.error(f"❌ DynamoDB error getting table stats: {error_code} - {str(e)}")
        return None
    except Exception as e:
        logger.error(f"❌ Unexpected error getting table stats: {str(e)}")
        return None

# Test function for development
def test_dynamodb_connection():
    """
    Test DynamoDB connection and basic operations
    
    Returns:
        bool: True if all tests pass, False otherwise
    """
    print("🧪 Testing DynamoDB connection...")
    
    # Test 1: Check if table exists
    if not table:
        print("❌ Table not available")
        return False
    
    print("✅ DynamoDB table object created successfully")
    
    # Test 2: Get table stats
    stats = get_table_stats()
    if not stats:
        print("❌ Could not get table stats")
        return False
    
    print(f"✅ Table stats: {stats}")
    
    # Test 3: Try to save a test item
    test_user_id = "test_user"
    test_project_id = generate_project_id()
    test_url = "https://example.com"
    test_data = {"test": "data", "timestamp": int(time.time())}
    
    success = save_scrape_data(test_user_id, test_project_id, test_url, test_data)
    if not success:
        print("❌ Could not save test data")
        return False
    
    print("✅ Successfully saved test data")
    
    # Test 4: Try to retrieve the test item
    retrieved = get_project(test_user_id, test_project_id)
    if not retrieved:
        print("❌ Could not retrieve test data")
        return False
    
    print(f"✅ Successfully retrieved test data: {retrieved}")
    
    # Test 5: Try to query user scrapes
    user_scrapes = get_user_scrapes(test_user_id, limit=5)
    if user_scrapes is None:
        print("❌ Could not query user scrapes")
        return False
    
    print(f"✅ Successfully queried user scrapes: {len(user_scrapes)} items found")
    
    # Test 6: Clean up test data
    delete_success = delete_project(test_user_id, test_project_id)
    if not delete_success:
        print("⚠️ Could not delete test data")
        return False
    
    print("✅ Successfully deleted test data")
    
    print("🎉 All DynamoDB tests passed!")
    return True

if __name__ == "__main__":
    # Run tests if script is executed directly
    test_dynamodb_connection()
