from flask import Flask, render_template, request, redirect, url_for, session, flash
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.corpus import stopwords, wordnet
from nltk.stem import WordNetLemmatizer
import string
from transformers import AutoTokenizer, AutoModel
import torch
from flask_mysqldb import MySQL
import bcrypt
import os

app = Flask(__name__)

app.secret_key=os.urandom(24)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'user_auth'

mysql = MySQL(app)


users = {}

df = pd.read_csv('legal_cases_updated.csv')

# Download required nltk data
nltk.download('stopwords')
nltk.download('wordnet')
stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

# Load the BERT model for sentence embeddings
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
model = AutoModel.from_pretrained("bert-base-uncased")

# Function to get synonyms
def get_synonyms(word):
    synonyms = set()
    for syn in wordnet.synsets(word):
        for lemma in syn.lemmas():
            synonyms.add(lemma.name())
    return synonyms

# Preprocess text data
def preprocess_text(text):
    if isinstance(text, float):  # Handle NaN values
        text = ""
    text = text.lower()  # Convert to lowercase
    text = text.translate(str.maketrans('', '', string.punctuation))  # Remove punctuation
    words = text.split()
    lemmatized_words = []
    for word in words:
        if word not in stop_words:
            synonyms = get_synonyms(word)
            lemma = lemmatizer.lemmatize(word)
            lemmatized_words.append(lemma)
            lemmatized_words.extend(synonyms)  # Add synonyms to the list
    return ' '.join(lemmatized_words)

# Combine relevant fields into a single text field for vectorization
df['Case_Title'] = df['Case_Title'].astype(str)
df['Facts'] = df['Facts'].astype(str)
df['Issues'] = df['Issues'].astype(str)
df['Analysis'] = df['Analysis'].astype(str)
df['Conclusion'] = df['Conclusion'].astype(str)

df.fillna('', inplace=True)  # Replace NaN with empty strings

df['combined_text'] = df['Case_Title'] + ' ' + df['Facts'] + ' ' + df['Issues'] + ' ' + df['Analysis'] + ' ' + df['Conclusion']
df['combined_text'] = df['combined_text'].apply(preprocess_text)

# Create a TF-IDF vectorizer
vectorizer = TfidfVectorizer(stop_words=list(stop_words), ngram_range=(1, 3))

# Create a TF-IDF matrix for the combined text
X = vectorizer.fit_transform(df['combined_text'])

# Function to get BERT embeddings
def get_embeddings(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.last_hidden_state.mean(dim=1)

@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'].encode('utf-8')
        
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        user = cursor.fetchone()
        cursor.close()
        
        if user and bcrypt.checkpw(password, user[2].encode('utf-8')):
            session['username'] = username  # Set session variable upon successful login
            session['user_id'] = user[0]  # Assuming the user ID is in the first column
            flash('Login successful!', 'success')
            next_route = request.args.get('next', url_for('index'))
            return redirect(next_route)
        else:
            flash('Invalid username or password', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'].encode('utf-8')
        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())
        
        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO users (username, password) VALUES (%s, %s)', (username, hashed_password))
        mysql.connection.commit()
        cursor.close()
        
        flash('You are now registered and can log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('user_id', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

@app.route('/search', methods=['POST'])
def search():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    query = request.form['query']
    user_id = session.get('user_id')

    # Store the search query in the database
    if user_id:
        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO search (query, user_id) VALUES (%s, %s)', (query, user_id))
        mysql.connection.commit()
        cursor.close()
    
    # Preprocess the query
    preprocessed_query = preprocess_text(query)
    
    # Get the BERT embeddings for the query
    query_embeddings = get_embeddings(preprocessed_query).numpy()
    
    # Get the TF-IDF vector for the query
    query_vec = vectorizer.transform([preprocessed_query])
    
    # Calculate cosine similarity between the query and the document vectors
    cosine_similarities = cosine_similarity(query_vec, X).flatten()

    # Rank documents based on cosine similarity scores
    ranked_indices = cosine_similarities.argsort()[::-1]

    results = []
    for i in ranked_indices[:5]:  # Adjust to get top 5 relevant results
        if cosine_similarities[i] > 0.1:  # Adjust threshold as needed
            case = {
                'title': df.iloc[i]['Case_Title'],
                'id': df.iloc[i]['Case_Id'],
                'type': df.iloc[i]['Case_Type'],
                'facts': df.iloc[i]['Facts'],
                'court': df.iloc[i]['Court']
            }
            results.append(case)

    if not results:
        return render_template('index.html', query=query, cases=[], not_found=True)

    return render_template('index.html', query=query, cases=results)

@app.route('/case/<case_id>', methods=['GET', 'POST'])
def case_detail(case_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    case = df[df['Case_Id'] == float(case_id)].iloc[0]

    percentages = {}
    if request.method == 'POST':
        case_type = request.form['case_type'].lower()

        # Filter cases by court
        supreme_court_cases = df[df['Court'].str.lower() == 'supreme court of pakistan']
        lahore_high_court_cases = df[df['Court'].str.lower() == 'lahore high court']

        # Calculate percentages
        for court_name, cases in [('Supreme Court of Pakistan', supreme_court_cases), ('Lahore High Court', lahore_high_court_cases)]:
            total_cases = len(cases)
            if total_cases > 0:
                case_type_count = cases['Case_Type'].str.lower().str.contains(case_type).sum()
                percentage = (case_type_count / total_cases) * 100
                percentages[court_name] = percentage
            else:
                percentages[court_name] = 0.0

    return render_template('case_detail.html', case=case, percentages=percentages)

@app.route('/search_history')
def search_history():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    user_id = session.get('user_id')
    
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT query FROM search WHERE user_id = %s', (user_id,))
    search_history = cursor.fetchall()
    cursor.close()
    
    return render_template('search_history.html', search_history=search_history)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
