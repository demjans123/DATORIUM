from flask import Flask, render_template, request
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from peewee import SqliteDatabase, Model, CharField, IntegerField
import os

app = Flask(__name__)

# Datubāzes inicializācija
db = SqliteDatabase('data.db')

class DataEntry(Model):
    column1 = CharField()
    column2 = CharField()
    column3 = CharField()
    column4 = IntegerField()
    
    class Meta:
        database = db

db.connect()
db.create_tables([DataEntry], safe=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        if file and file.filename.endswith('.csv'):
            df = pd.read_csv(file)
            # Saglabā datus datubāzē
            for _, row in df.iterrows():
                DataEntry.create(column1=row['column1'], column2=row['column2'], 
                                column3=row['column3'], column4=row['column4'])
            # Ģenerē grafikus
            generate_visualizations(df)
            return render_template('results.html')
    return render_template('index.html')

@app.route('/filter/<filter_value>')
def filter_by_column2(filter_value):
    # Filtrēšana pēc column2
    query = DataEntry.select().where(DataEntry.column2 == filter_value)
    df = pd.DataFrame([(d.column1, d.column2, d.column3, d.column4) for d in query], 
                      columns=['column1', 'column2', 'column3', 'column4'])
    generate_visualizations(df)
    return render_template('results.html')

def generate_visualizations(df):
    # Histogramma priekš column4
    plt.figure(figsize=(8, 6))
    sns.histplot(df['column4'], bins=10, color='skyblue')
    plt.title('Column4 vērtību sadalījums')
    plt.savefig('static/histogram.png')
    plt.close()
    
    # Stabiņu diagramma vidējām column4 vērtībām pa column3
    plt.figure(figsize=(8, 6))
    sns.barplot(x='column3', y='column4', data=df, estimator=lambda x: sum(x)/len(x), color='salmon')
    plt.title('Column4 vidējās vērtības pa Column3')
    plt.savefig('static/bar_chart.png')
    plt.close()

if name == '__main__':
    if not os.path.exists('static'):
        os.makedirs('static')
    app.run(debug=True)