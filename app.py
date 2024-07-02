from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import date

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Sayli%40123@localhost/promotion_ferry'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Promotion(db.Model):
    __tablename__ = 'promotion'
    title = db.Column(db.String(100), nullable=False, primary_key=True)
    code = db.Column(db.String(20), nullable=False, unique=True)
    from_date = db.Column(db.Date, nullable=False)
    to_date = db.Column(db.Date, nullable=False)
    percentage = db.Column(db.Integer, nullable=False)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_promotion', methods=['POST'])
def add_promotion():
    data = request.json
    title = data.get('title')
    code = data.get('code')
    from_date = data.get('from_date')
    to_date = data.get('to_date')
    percentage = data.get('percentage')

    if not title or not code or not from_date or not to_date or not percentage:
        return jsonify({'error': 'All fields are required.'}), 400

    new_promotion = Promotion(
        title=title,
        code=code,
        from_date=from_date,
        to_date=to_date,
        percentage=percentage
    )
    db.session.add(new_promotion)
    db.session.commit()

    return jsonify({'message': 'Promotion added successfully.'})

@app.route('/promotions')
def get_promotions():
    promotions = Promotion.query.all()
    promotion_list = []
    for promo in promotions:
        promotion_list.append({
            'title': promo.title,
            'code': promo.code,
            'from_date': promo.from_date,
            'to_date': promo.to_date,
            'percentage': promo.percentage
        })
    return jsonify({'promotions': promotion_list})

@app.route('/delete_promotion/<string:code>', methods=['DELETE'])
def delete_promotion(code):
    promotion = Promotion.query.filter_by(code=code).first_or_404()
    db.session.delete(promotion)
    db.session.commit()
    return jsonify({'message': 'Promotion deleted successfully.'})

@app.route('/modify_promotion/<string:code>', methods=['PUT'])
def modify_promotion(code):
    data = request.json
    promotion = Promotion.query.filter_by(code=code).first_or_404()

    title = data.get('title')
    from_date = data.get('from_date')
    to_date = data.get('to_date')
    percentage = data.get('percentage')

    if not title or not from_date or not to_date or not percentage:
        return jsonify({'error': 'All fields are required.'}), 400

    promotion.title = title
    promotion.from_date = from_date
    promotion.to_date = to_date
    promotion.percentage = percentage

    db.session.commit()
    return jsonify({'message': 'Promotion modified successfully.'})

def delete_expired_promotions():
    today = date.today()
    expired_promotions = Promotion.query.filter(Promotion.to_date < today).all()

    for promo in expired_promotions:
        db.session.delete(promo)

    db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        delete_expired_promotions()
    app.run(debug=True)