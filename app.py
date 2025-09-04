from flask import Flask, request, jsonify, render_template_string
import re
from collections import Counter
import time

app = Flask(__name__)

# Personality analysis functions
def analyze_writing_style(text):
    """Analyze text for personality traits based on writing patterns"""
    
    # Basic text metrics
    word_count = len(text.split())
    sentence_count = len([s for s in re.split(r'[.!?]+', text) if s.strip()])
    avg_word_length = sum(len(word.strip('.,!?;:')) for word in text.split()) / max(word_count, 1)
    avg_sentence_length = word_count / max(sentence_count, 1)
    
    # Punctuation analysis
    exclamation_count = text.count('!')
    question_count = text.count('?')
    ellipses_count = text.count('...')
    caps_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
    
    # Word pattern analysis
    words = text.lower().split()
    
    # Personality indicators
    enthusiasm_words = ['amazing', 'awesome', 'incredible', 'fantastic', 'wonderful', 'great', 'love', 'excited']
    uncertainty_words = ['maybe', 'perhaps', 'might', 'possibly', 'probably', 'think', 'guess', 'suppose']
    analytical_words = ['because', 'therefore', 'however', 'although', 'whereas', 'consequently', 'furthermore']
    emotional_words = ['feel', 'heart', 'soul', 'emotion', 'passion', 'dream', 'hope', 'fear']
    
    # Calculate personality scores (0-100)
    extroversion = min(100, int(
        (exclamation_count * 20) + 
        (caps_ratio * 100) + 
        (sum(1 for word in words if word in enthusiasm_words) * 15) +
        (max(0, avg_sentence_length - 10) * 2)
    ))
    
    conscientiousness = min(100, int(
        (max(0, avg_word_length - 4) * 20) +
        (sum(1 for word in words if word in analytical_words) * 25) +
        (max(0, 15 - avg_sentence_length) * 3) +
        (50 if avg_sentence_length > 8 else 20)
    ))
    
    neuroticism = min(100, int(
        (ellipses_count * 25) +
        (sum(1 for word in words if word in uncertainty_words) * 20) +
        (question_count * 15) +
        (sum(1 for word in words if word in emotional_words) * 10)
    ))
    
    openness = min(100, int(
        (len(set(words)) / max(len(words), 1) * 100) +
        (sum(1 for word in words if len(word) > 7) * 10) +
        (avg_word_length * 10)
    ))
    
    agreeableness = min(100, int(
        (text.lower().count('please') * 30) +
        (text.lower().count('thank') * 25) +
        (100 - neuroticism * 0.3) +
        (50 - exclamation_count * 5)
    ))
    
    return {
        'extroversion': max(10, extroversion),
        'conscientiousness': max(10, conscientiousness),
        'neuroticism': max(10, neuroticism),
        'openness': max(10, openness),
        'agreeableness': max(10, agreeableness),
        'metrics': {
            'word_count': word_count,
            'avg_word_length': round(avg_word_length, 2),
            'avg_sentence_length': round(avg_sentence_length, 2),
            'exclamation_ratio': round(exclamation_count / max(sentence_count, 1), 2),
            'caps_ratio': round(caps_ratio * 100, 2)
        }
    }

def get_personality_description(scores):
    """Generate personality description from Big Five scores"""
    descriptions = []
    
    # Extroversion
    if scores['extroversion'] > 70:
        descriptions.append("🎉 Highly extroverted - energetic, outgoing, seeks social stimulation")
    elif scores['extroversion'] > 40:
        descriptions.append("🤝 Moderately extroverted - balanced social energy")
    else:
        descriptions.append("🤔 Introverted - thoughtful, reserved, introspective")
    
    # Conscientiousness
    if scores['conscientiousness'] > 70:
        descriptions.append("📋 Highly organized - detail-oriented, disciplined, methodical")
    elif scores['conscientiousness'] > 40:
        descriptions.append("⚖️ Moderately organized - balanced approach to structure")
    else:
        descriptions.append("🎨 Spontaneous - flexible, adaptable, creative")
    
    # Neuroticism
    if scores['neuroticism'] > 70:
        descriptions.append("😰 High sensitivity - emotionally reactive, stress-prone")
    elif scores['neuroticism'] > 40:
        descriptions.append("🌊 Moderate sensitivity - normal emotional responses")
    else:
        descriptions.append("😌 Emotionally stable - calm, resilient, steady")
    
    # Openness
    if scores['openness'] > 70:
        descriptions.append("🌟 Highly creative - imaginative, curious, open to new ideas")
    elif scores['openness'] > 40:
        descriptions.append("🎭 Moderately creative - balanced openness to experience")
    else:
        descriptions.append("🏛️ Traditional - practical, conventional, focused")
    
    # Agreeableness
    if scores['agreeableness'] > 70:
        descriptions.append("💖 Highly cooperative - trusting, helpful, empathetic")
    elif scores['agreeableness'] > 40:
        descriptions.append("🤷 Moderately cooperative - balanced social approach")
    else:
        descriptions.append("🎯 Competitive - direct, challenging, independent")
    
    return descriptions

# Routes
@app.route('/')
def index():
    """Main page with typing interface"""
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Typing Personality Analyzer</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
            .container { max-width: 800px; margin: 0 auto; background: rgba(255,255,255,0.1); padding: 30px; border-radius: 15px; backdrop-filter: blur(10px); }
            h1 { text-align: center; margin-bottom: 30px; }
            textarea { width: 100%; height: 200px; padding: 15px; border: none; border-radius: 10px; font-size: 16px; resize: vertical; }
            button { background: #ff6b6b; color: white; border: none; padding: 15px 30px; border-radius: 10px; font-size: 16px; cursor: pointer; margin-top: 15px; }
            button:hover { background: #ff5252; }
            .result { margin-top: 30px; padding: 20px; background: rgba(255,255,255,0.15); border-radius: 10px; }
            .score { display: inline-block; margin: 10px; padding: 10px; background: rgba(255,255,255,0.2); border-radius: 8px; }
            .description { margin-top: 15px; line-height: 1.6; }
            .example-buttons { margin: 15px 0; }
            .example-btn { background: rgba(255,255,255,0.2); margin: 5px; padding: 8px 15px; border-radius: 20px; font-size: 14px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🧠 Typing Personality Analyzer</h1>
            <p style="text-align: center; margin-bottom: 30px;">Write something (anything!) and discover your personality traits through your typing patterns.</p>
            
            <div class="example-buttons">
                <strong>Try examples:</strong><br>
                <button class="example-btn" onclick="setExample('excited')">Excited Person</button>
                <button class="example-btn" onclick="setExample('analytical')">Analytical Mind</button>
                <button class="example-btn" onclick="setExample('uncertain')">Uncertain Thinker</button>
            </div>
            
            <textarea id="textInput" placeholder="Start typing here... Share your thoughts, describe your day, or write about anything that comes to mind. The more you write, the more accurate the analysis!"></textarea>
            <br>
            <button onclick="analyzeText()">🔍 Analyze My Personality</button>
            
            <div id="result" class="result" style="display: none;">
                <h3>Your Personality Profile:</h3>
                <div id="scores"></div>
                <div id="description" class="description"></div>
                <div id="metrics" style="margin-top: 20px; font-size: 14px; opacity: 0.8;"></div>
            </div>
        </div>

        <script>
            function setExample(type) {
                const examples = {
                    'excited': "OMG this is SO amazing!! I absolutely LOVE this idea and I can't wait to see what happens next! This is going to be incredible and I'm super excited about all the possibilities!!!",
                    'analytical': "I think this approach has merit, however we should consider the various implications. The methodology appears sound, but perhaps we need to examine the underlying assumptions more carefully. What are the potential consequences?",
                    'uncertain': "Well... I'm not really sure about this. Maybe it could work? I guess we could try it, but I don't know... what do you think? It might be okay, but there could be issues..."
                };
                document.getElementById('textInput').value = examples[type];
            }

            function analyzeText() {
                const text = document.getElementById('textInput').value;
                if (!text.trim()) {
                    alert('Please write something first!');
                    return;
                }

                fetch('/analyze', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({text: text})
                })
                .then(response => response.json())
                .then(data => {
                    document.getElementById('result').style.display = 'block';
                    
                    // Display scores
                    const scores = data.personality;
                    document.getElementById('scores').innerHTML = `
                        <div class="score">Extroversion: <strong>${scores.extroversion}%</strong></div>
                        <div class="score">Conscientiousness: <strong>${scores.conscientiousness}%</strong></div>
                        <div class="score">Neuroticism: <strong>${scores.neuroticism}%</strong></div>
                        <div class="score">Openness: <strong>${scores.openness}%</strong></div>
                        <div class="score">Agreeableness: <strong>${scores.agreeableness}%</strong></div>
                    `;
                    
                    // Display description
                    document.getElementById('description').innerHTML = 
                        '<strong>Your Personality Traits:</strong><br>' + 
                        data.description.join('<br>');
                    
                    // Display metrics
                    const metrics = scores.metrics;
                    document.getElementById('metrics').innerHTML = `
                        <strong>Writing Metrics:</strong> ${metrics.word_count} words, 
                        avg word length: ${metrics.avg_word_length}, 
                        avg sentence length: ${metrics.avg_sentence_length}, 
                        caps usage: ${metrics.caps_ratio}%
                    `;
                });
            }
        </script>
    </body>
    </html>
    """
    return render_template_string(html_template)

@app.route('/analyze', methods=['POST'])
def analyze():
    """Analyze text and return personality assessment"""
    data = request.get_json()
    text = data.get('text', '')
    
    if not text.strip():
        return jsonify({'error': 'No text provided'}), 400
    
    # Analyze personality
    scores = analyze_writing_style(text)
    description = get_personality_description(scores)
    
    return jsonify({
        'personality': scores,
        'description': description,
        'word_count': len(text.split()),
        'timestamp': time.time()
    })

@app.route('/compare', methods=['POST'])
def compare():
    """Compare two people's typing personalities"""
    data = request.get_json()
    text1 = data.get('text1', '')
    text2 = data.get('text2', '')
    
    if not text1.strip() or not text2.strip():
        return jsonify({'error': 'Both texts required for comparison'}), 400
    
    # Analyze both texts
    scores1 = analyze_writing_style(text1)
    scores2 = analyze_writing_style(text2)
    
    # Calculate compatibility
    differences = {}
    total_diff = 0
    for trait in ['extroversion', 'conscientiousness', 'neuroticism', 'openness', 'agreeableness']:
        diff = abs(scores1[trait] - scores2[trait])
        differences[trait] = diff
        total_diff += diff
    
    compatibility = max(0, 100 - (total_diff / 5))
    
    return jsonify({
        'person1': {
            'personality': scores1,
            'description': get_personality_description(scores1)
        },
        'person2': {
            'personality': scores2,
            'description': get_personality_description(scores2)
        },
        'differences': differences,
        'compatibility': round(compatibility, 1),
        'analysis': f"Compatibility score: {round(compatibility, 1)}% - " + 
                   ("High compatibility! Very similar personalities." if compatibility > 80 
                    else "Good compatibility with some differences." if compatibility > 60
                    else "Moderate compatibility - complementary differences." if compatibility > 40
                    else "Low compatibility - very different personalities.")
    })

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=3000)