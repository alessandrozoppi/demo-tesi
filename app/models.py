from app import db

class Recipe(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(80))
	portions = db.Column(db.Integer)
	url_title = db.Column(db.String(80))
	step = db.relationship('Step', backref='recipe', cascade='all, delete')
	ingredient = db.relationship('Ingredient', backref='recipe', cascade='all, delete')
	
class Step(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	order = db.Column(db.Integer)
	content = db.Column(db.String(500))
	extra = db.Column(db.String(500))
	recipe_id = db.Column(db.Integer, db.ForeignKey(Recipe.id))

class Ingredient(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(80))
	quantity = db.Column(db.Integer)
	unit = db.Column(db.String)
	recipe_id = db.Column(db.Integer, db.ForeignKey(Recipe.id))
	
class Counter(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(20))
	counter = db.Column(db.Integer, default=1)
	
class GroceryList(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(80))
