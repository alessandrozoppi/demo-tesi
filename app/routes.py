import webbrowser

from app import app, db
from flask import render_template
from app.models import Recipe, Ingredient, Step, Counter

from app import ask
from flask_ask import statement, question

########## FLASK ROUTES ##########

@app.route('/home/')
def home():
	recipes = Recipe.query.all()
	return render_template('index.html', recipes=recipes)
	
@app.route('/recipe/<recipeTitle>/')
def recipe(recipeTitle):
	recipe = Recipe.query.filter_by(url_title=recipeTitle).first()
	recipeId = recipe.id
	ingredients = Ingredient.query.join(Ingredient.recipe).filter(Recipe.id==recipeId).all()
	return render_template('recipe.html', recipe=recipe, ingredients=ingredients)
	
@app.route('/recipe/<recipeTitle>/step/<stepNumber>/')
def step(recipeTitle, stepNumber):
	targetRecipe = Recipe.query.filter_by(url_title=recipeTitle).first()
	targetStep = Step.query.filter_by(id=stepNumber).first()
	return render_template('step.html', recipe=targetRecipe,
										step=targetStep,
										stepNumber=stepNumber,
										stepContent=targetStep.content)

########## ASK INTENTS ##########

# appends title/name from a query to a list
def listify(query):
	queryList = []
	try:
		for item in query: #recipes
			queryList.append(item.title)
	except AttributeError:	#listyfy works for both Recipe.title and Ingredient.name
		for item in query: #ingredients
			if item.unit != "":
				fmtItem = "{} {} of {}".format(item.quantity, item.unit, item.name)
				queryList.append(fmtItem)
			else: #in case the unit value is empty "es. 2 egg yolks"
				fmtItem = "{} {}".format(item.quantity, item.name)
				queryList.append(fmtItem)
	return queryList

# format a list from a query to make it readable for Alexa
def commaFormat(itemList):
	comma = ', '
	fmtCommaList = comma.join(itemList)
	return fmtCommaList

@ask.launch
def start_demo():
	message = "The demo is up and running!"
	return statement(message)

@ask.intent("ReadCookBookIntent")
def readCookBook():
	recipes = Recipe.query.all()
	recipesList = listify(recipes)
	fmtRecipesList = commaFormat(recipesList)
	message = "The recipes in your cookbook are {}".format(fmtRecipesList)
	return statement(message)

@ask.intent("ReadIngredientsIntent")
def readIngredients(recipe):
	fmtRecipe = recipe.replace(" ", "")
	targetRecipe = Recipe.query.filter_by(url_title=fmtRecipe).first()
	targetIngredients = Ingredient.query.join(Ingredient.recipe).filter(Recipe.url_title==fmtRecipe).all()
	ingredientsList = listify(targetIngredients)
	fmtIngredientsList = commaFormat(ingredientsList)
	message = "The ingredients for {} are {}".format(targetRecipe.title, fmtIngredientsList)
	return statement(message)

@ask.intent("ShowCookBookIntent")
def showCookBook():
	webbrowser.get('firefox').open('http://localhost:5000/home/')
	message = "opening your cookbook"
	return statement(message)
	
@ask.intent("ShowRecipeIntent")
def showRecipe(recipe):
	fmtRecipe = recipe.replace(" ", "")
	print(fmtRecipe)
	webbrowser.get('firefox').open('http://localhost:5000/recipe/' + fmtRecipe)
	message = "opening your"  + recipe + " recipe"
	return statement(message)

@ask.intent("StartCookingIntent")
def startCooking(recipe):
	fmtRecipe = recipe.replace(" ", "")
	targetRecipe = Recipe.query.filter_by(url_title=fmtRecipe).first()
	gbRecipeId = Counter.query.filter_by(id=1).first()
	gbRecipeId.counter = targetRecipe.id
	gbStepNumber = Counter.query.filter_by(id=2).first()
	gbStepNumber.counter = 0
	db.session.commit()
	print(gbStepNumber.counter, gbRecipeId.counter)
	message = "I'm ready to start cooking {}".format(recipe)
	return statement(message)

@ask.intent("NextStepIntent")
def nextStep():
	gbStepNumber = Counter.query.filter_by(id=2).first()
	gbRecipeId = Counter.query.filter_by(id=1).first()
	print(gbStepNumber.counter, '\n')
	print(gbRecipeId.counter, '\n')
	stepsOfCurrentRecipe = Step.query.filter_by(recipe_id=gbRecipeId.counter).all()
	if gbStepNumber.counter < len(stepsOfCurrentRecipe):
		gbStepNumber.counter += 1
		db.session.commit()
		print(gbRecipeId.counter)
		currentStep = Step.query.filter(Step.recipe_id==gbRecipeId.counter, Step.order==gbStepNumber.counter).first()
		if currentStep.extra == None:
			message = "Step {}, {}".format(gbStepNumber.counter, currentStep.content)
		else:
			message = "Step {}, {}. {}".format(gbStepNumber.counter, currentStep.content, currentStep.extra)
		return statement(message)
	else:
		return statement("You completed this recipe!")

@ask.intent("PreviousStepIntent")
def previousStep():
	gbStepNumber = Counter.query.filter_by(id=2).first()
	gbRecipeId = Counter.query.filter_by(id=1).first()
	if gbStepNumber.counter > 1:
		gbStepNumber.counter -= 1
		db.session.commit()
		currentStep = Step.query.filter(Step.recipe_id==gbRecipeId.counter, Step.order==gbStepNumber.counter).first()
		message = "Step {}, {}".format(gbStepNumber.counter, currentStep.content)
		return statement(message)
	else:
		return statement("Sorry, there are no previous steps")

@ask.intent("RepeatStepIntent")
def repeatStep():
	gbStepNumber = Counter.query.filter_by(id=2).first()
	gbRecipeId = Counter.query.filter_by(id=1).first()
	currentStep = Step.query.filter(Step.recipe_id==gbRecipeId.counter, Step.order==gbStepNumber.counter).first()
	message = "Sure, {}".format(currentStep.content)
	return statement(message)

@ask.intent("ShowThisStepIntent")
def showThisStep():
	gbStepNumber = Counter.query.filter_by(id=2).first()
	gbRecipeId = Counter.query.filter_by(id=1).first()
	targetRecipe = Recipe.query.filter_by(id=gbRecipeId.counter).first()
	if gbStepNumber.counter != 0:
		webbrowser.get('firefox').open('http://localhost:5000/recipe/{}/step/{}'.format(targetRecipe.url_title, gbStepNumber.counter))
		message = ("I'm opening step {} on your device".format(gbStepNumber.counter))
		return statement(message)
	else:
		return statement("you haven't opened any step yet, try to say: Alexa, tell demo next step")





