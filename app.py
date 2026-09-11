from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

# DİKKAT: 'postgres123' yerine pgAdmin/PostgreSQL kurarken belirlediğin kendi şifreni yaz!
DB_USER = 'postgres'
DB_PASSWORD = '1336481+qW'
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_NAME = 'unitrack_db'

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ----------------- MODELLER -----------------

class Course(db.Model):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)   # Örn: BSM301
    name = db.Column(db.String(100), nullable=False)               # Örn: Operating Systems
    credit = db.Column(db.Integer, nullable=False)                 # Örn: 3
    ects = db.Column(db.Integer, nullable=False)                   # Örn: 4
    midterm = db.Column(db.Float, default=0.0)                     # Vize notu
    final = db.Column(db.Float, default=0.0)                       # Final notu

    def calculate_average(self):
        return round((self.midterm * 0.4) + (self.final * 0.6), 2)

    def to_dict(self):
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name,
            "credit": self.credit,
            "ects": self.ects,
            "midterm": self.midterm,
            "final": self.final,
            "average": self.calculate_average()
        }

# ----------------- ENDPOINT'LER -----------------

@app.route('/')
def home():
    return render_template('index.html')

# Tüm dersleri listele
@app.route('/api/courses', methods=['GET'])
def get_courses():
    courses = Course.query.all()
    return jsonify([c.to_dict() for c in courses]), 200

# Yeni ders ekle
@app.route('/api/courses', methods=['POST'])
def add_course():
    data = request.get_json()
    new_course = Course(
        code=data['code'],
        name=data['name'],
        credit=data['credit'],
        ects=data['ects'],
        midterm=data.get('midterm', 0.0),
        final=data.get('final', 0.0)
    )
    db.session.add(new_course)
    db.session.commit()
    return jsonify({"message": "Ders başarıyla eklendi!", "course": new_course.to_dict()}), 201

# Uygulama başlarken tabloları PostgreSQL'de otomatik oluştur
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, port=5000)