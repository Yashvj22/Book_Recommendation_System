from flask import Flask, render_template, request
import pickle
import numpy as np
import sqlite3
import csv

popular_df = pickle.load(open('popular.pkl','rb'))
pt = pickle.load(open('pt.pkl','rb'))
books = pickle.load(open('books.pkl','rb'))
similarity_scores = pickle.load(open('similarity_scores.pkl','rb'))



app = Flask(__name__)

@app.route('/')
def index():
    conn = sqlite3.connect('feedback.sqlite')
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS feedback (name varchar(20), email varchar(50), message varchar(50));")
    cursor.close()
    conn.close()
    
    return render_template('index.html',
                           book_name=list(popular_df['Book-Title'].values),
                           author=list(popular_df['Book-Author'].values),
                           image=list(popular_df['Image-URL-M'].values),
                           votes=list(popular_df['num_ratings'].values),
                           rating=list(popular_df['avg_rating'].values)
                           )
    

@app.route('/recommend')
def recommend_ui():
    return render_template('recommend.html')

@app.route('/recommend_books',methods=['post'])
def recommend():
    user_input = request.form.get('user_input')
    index = np.where(pt.index == user_input)[0][0]
    similar_items = sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[1:5]

    data = []
    for i in similar_items:
        item = []
        temp_df = books[books['Book-Title'] == pt.index[i[0]]]
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values))

        data.append(item)

    print(data)

    return render_template('recommend.html',data=data)

@app.route('/contact', methods=['GET', 'POST'])
def contact_form():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        msg = request.form['message']

        conn = sqlite3.connect('feedback.sqlite')
        cur = conn.cursor()
        cur.execute('''INSERT INTO feedback values(?, ?, ?)''',(name, email, msg))
        conn.commit()
        cur.close()
        conn.close()


        return render_template('contact.html', confirmation=f"Thank you, {name}, for your message. We'll get back to you at {email} as soon as possible")

    
    return render_template('contact.html', confirmation="")


@app.route('/submit_contact_form', methods=['POST'])
def submit_contact_form():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        msg = request.form['message']

        conn = sqlite3.connect('feedback.sqlite')
        cur = conn.cursor()
        cur.execute('''INSERT INTO feedback values(?, ?, ?)''',(name, email, msg))
        conn.commit()
        cur.close()
        conn.close()

        context = dict()
        context['result'] =  f"Thank you, {name}, for your message. We'll get back to you at {email} as soon as possible"
        return render_template('contact.html', context=context)
    
def read_csv():
    with open('books.csv', mode='r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        books = [row for row in csv_reader]
    return books

# Search for a book by its title
def search_book_by_title(title: str, books):
    print(title)
    for book in books:
        if book['Book-Title'].lower() == title.lower():
            return book
    return None

# Define a route to handle book search by title
@app.route('/search', methods=['GET', 'POST'])
def search():
    title = request.form.get('title')
    # if not title:
    #     return render_template('index.html')

    books = read_csv()
    book = search_book_by_title(title, books)
    # print(book['Book-Title'])
    return render_template('result.html', book=book)    
    
if __name__ == '__main__':
    app.run(debug=True)

