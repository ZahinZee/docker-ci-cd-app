import pytest
import json
from app import app

@pytest.fixture   #reusable helper\client you can “inject” into tests
def client():
    """
    Create a test client for the Flask app
    """
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_homepage(client):
    """
    Tests Main Page loads correctly
    """
    response = client.get('/')
    assert response.status_code == 200
    assert b'Typing Personality Analyzer' in response.data
    assert b'textarea' in response.data 


def test_analyze_valid_text(client):

    test_text = " IT'S A SILLY APP"
    response = client.post('/analyze', 
                          data=json.dumps({"text": test_text}),
                          content_type='application/json')
    
    assert response.status_code == 200
    
    data = json.loads(response.data)
    
    # Check required keys exist
    assert 'personality' in data
    assert 'description' in data
    assert 'word_count' in data
    
    # Check personality traits exist
    personality = data['personality']
    required_traits = ['extroversion', 'conscientiousness', 'neuroticism', 'openness', 'agreeableness']
    for trait in required_traits:
        assert trait in personality
    
    # Check data types
    assert isinstance(data['description'], list)
    assert isinstance(data['word_count'], int)
    assert data['word_count'] > 0

def test_analyze_empty_text(client):
    """Test error handling for empty text"""
    response = client.post('/analyze', 
                          data=json.dumps({"text": ""}),
                          content_type='application/json')
    
    assert response.status_code == 400
    
    data = json.loads(response.data)
    assert 'error' in data
    assert 'No text provided' in data['error']

def test_analyze_whitespace_only(client):
    """Test error handling for whitespace-only text"""
    response = client.post('/analyze', 
                          data=json.dumps({"text": "   \n\t  "}),
                          content_type='application/json')
    
    assert response.status_code == 400

def test_personality_scores_range(client):
    """Test that personality scores are within valid range (0-100)"""
    response = client.post('/analyze', 
                          data=json.dumps({"text": "This is a comprehensive test message for detailed personality analysis!"}),
                          content_type='application/json')
    
    data = json.loads(response.data)
    personality = data['personality']
    
    # Check that all personality scores are in valid range
    for trait in ['extroversion', 'conscientiousness', 'neuroticism', 'openness', 'agreeableness']:
        score = personality[trait]
        assert 0 <= score <= 100, f"{trait} score {score} is not between 0-100"

def test_compare_endpoint(client):
    """Test the compare functionality"""
    text1 = "I'm super excited about everything! This is amazing!!!"
    text2 = "I think this might work. Perhaps we should consider the options carefully."
    
    response = client.post('/compare', 
                          data=json.dumps({"text1": text1, "text2": text2}),
                          content_type='application/json')
    
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert 'person1' in data
    assert 'person2' in data
    assert 'compatibility' in data
    assert 'analysis' in data
    
    # Check score is valid
    compatibility = data['compatibility']
    assert 0 <= compatibility <= 100

def test_compare_missing_text(client):
    """Test compare endpoint with missing text"""
    response = client.post('/compare', 
                          data=json.dumps({"text1": "Hello world"}),
                          content_type='application/json')
    
    assert response.status_code == 400
    
    data = json.loads(response.data)
    assert 'error' in data

def test_invalid_json(client):
    """Test handling of invalid JSON"""
    response = client.post('/analyze', 
                          data="not valid json",
                          content_type='application/json')
    
    assert response.status_code in [400, 500]

