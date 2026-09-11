from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Veritabanı Bağlantı Ayarları
DB_USER = 'postgres'
DB_PASSWORD = '1336481+qW'  # Kendi şifren
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_NAME = 'unitrack_db'

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql+psycopg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ----------------- MODELLER -----------------

class Course(db.Model):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    credit = db.Column(db.Integer, nullable=False)
    ects = db.Column(db.Integer, nullable=False)
    midterm = db.Column(db.Float, default=0.0)
    final = db.Column(db.Float, default=0.0)

    def calculate_average(self):
        return round((self.midterm * 0.4) + (self.final * 0.6), 2)

    def get_letter_and_grade_point(self):
        avg = self.calculate_average()
        if avg >= 90: return 'AA', 4.0
        elif avg >= 85: return 'BA', 3.5
        elif avg >= 80: return 'BB', 3.0
        elif avg >= 75: return 'CB', 2.5
        elif avg >= 65: return 'CC', 2.0
        elif avg >= 58: return 'DC', 1.5
        elif avg >= 50: return 'DD', 1.0
        elif avg >= 40: return 'FD', 0.5
        else: return 'FF', 0.0

    def to_dict(self):
        letter, gpa_point = self.get_letter_and_grade_point()
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name,
            "credit": self.credit,
            "ects": self.ects,
            "midterm": self.midterm,
            "final": self.final,
            "average": self.calculate_average(),
            "letter": letter,
            "grade_point": gpa_point
        }

# ----------------- ENDPOINT'LER -----------------

@app.route('/')
def home():
    return render_template('index.html')

# Tüm dersleri listele
@app.route('/api/courses', methods=['GET'])
def get_courses():
    courses = Course.query.order_by(Course.id.asc()).all()
    return jsonify([c.to_dict() for c in courses]), 200

# Yeni ders ekle
@app.route('/api/courses', methods=['POST'])
def add_course():
    data = request.get_json()
    new_course = Course(
        code=data['code'].upper().strip(),
        name=data['name'].strip(),
        credit=data['credit'],
        ects=data['ects'],
        midterm=data.get('midterm', 0.0),
        final=data.get('final', 0.0)
    )
    db.session.add(new_course)
    db.session.commit()
    return jsonify({"message": "Ders eklendi", "course": new_course.to_dict()}), 201

# Ders sil
@app.route('/api/courses/<int:course_id>', methods=['DELETE'])
def delete_course(course_id):
    course = Course.query.get_or_404(course_id)
    db.session.delete(course)
    db.session.commit()
    return jsonify({"message": f"{course.code} başarıyla silindi!"}), 200

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, port=5000)