import webbrowser

from app import app, db
from flask import render_template, redirect, url_for
from app.models import Recipe, Ingredient, Step, Counter, GroceryList, SeasonalIngredients

from app import ask
from flask_ask import statement, question, session

########## FLASK ROUTES ##########
@app.route('/home/')
def home():
	return render_template('home.html')

@app.route('/cookbook/')
def cookbook():
	recipes = Recipe.query.all()
	return render_template('cookbook.html', recipes=recipes)
	
@app.route('/recipe/<recipeTitle>/')
def recipe(recipeTitle):
	recipe = Recipe.query.filter_by(url_title=recipeTitle).first()
	recipeId = recipe.id
	ingredients = Ingredient.query.join(Ingredient.recipe).filter(Recipe.id==recipeId).all()
	return render_template('recipe.html', recipe=recipe, ingredients=ingredients)
	
@app.route('/recipe/<recipeTitle>/step/<stepNumber>/')
def step(recipeTitle, stepNumber):
	gbStepNumber = Counter.query.filter_by(id=2).first()
	gbRecipeId = Counter.query.filter_by(id=1).first()
	targetRecipe = Recipe.query.filter_by(url_title=recipeTitle).first()
	targetStep = Step.query.filter(Step.recipe_id==targetRecipe.id, Step.order==stepNumber).first()
	return render_template('step.html', recipe=targetRecipe,
										step=targetStep,
										stepNumber=stepNumber,
										stepContent=targetStep.content)

@app.route('/grocery-list/')
def groceryList():
	targetIngredients = GroceryList.query.all()
	return render_template('grocerylist.html', ingredients = targetIngredients)


@app.route('/grocery-list/delete/<ingredientId>')
def deleteIngredientFromList(ingredientId):
	fmtIngredientId = int(ingredientId)
	targetIngredient = GroceryList.query.filter_by(id=fmtIngredientId).first()
	db.session.delete(targetIngredient)
	db.session.commit()
	print(targetIngredient.name + " succesfullt deleted from db")
	return redirect(url_for('groceryList'))

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

# check seasonal ingredients
def checkSeasonalIngredients(ingredientsToCheckList, currentSeason):
	targetTable = SeasonalIngredients.query.filter(SeasonalIngredients.season != currentSeason).all()
	targetIngredientsList = []
	notSeasonalIngredients = []
	for item in targetTable:
		targetIngredientsList.append(item.name)
	for ingredient in ingredientsToCheckList:
		if ingredient in targetIngredientsList:
			print('WARNING: ' + ingredient)
			notSeasonalIngredients.append(ingredient)
		else:
			print("CLEAR: " + ingredient)
	return notSeasonalIngredients

@ask.launch
def start_demo():
	message = "soo-chef is up and running!"
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
	webbrowser.get('firefox').open('http://localhost:5000/cookbook/')
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


@ask.intent("AddOneIngredientToListIntent")
def addOneIngredientToList(ingredient):
	checkIngredientsList = []
	checkIngredientsList.append(ingredient)
	notSeasonalIngredients = checkSeasonalIngredients(checkIngredientsList, 'winter')
	if len(notSeasonalIngredients) == 0:
		newIngredientEntry = GroceryList(name=ingredient)
		db.session.add(newIngredientEntry)
		db.session.commit()
		message= "I added " + ingredient + " to the list"
		return statement(message)
	else:
		message= "{} is not a seasonal ingredient, are you sure you want to add it to the list?".format(ingredient)
		session.attributes['notSeasonalIngredient'] = ingredient
		return question(message)

@ask.intent("AddTwoIngredientsToListIntent")
def addTwoIngredientsToList(ingredientOne, ingredientTwo):
	checkIngredientsList = []
	checkIngredientsList.append(ingredientOne)
	checkIngredientsList.append(ingredientTwo)
	notSeasonalIngredients = checkSeasonalIngredients(checkIngredientsList, 'winter')
	if len(notSeasonalIngredients) == 0:
		for ingredient in checkIngredientsList:
			newEntry = GroceryList(name = ingredient.name)
			db.session.add(newEntry)
			db.session.commit()
			message = "I added {} and {} to your list".format(ingredientOne, ingredientTwo)
			return statement(message)
	elif len(notSeasonalIngredients) == 1:
		if ingredientOne == notSeasonalIngredients[0]:
			session.attributes['notSeasonalIngredient'] = ingredientOne
			newEntry = GroceryList(name=ingredientTwo)
			db.session.add(newEntry)
			db.session.commit()
			message = "I added {}, but {} is not a seasonal ingredient, are you sure you want to add it to the list".format(ingredientTwo, ingredientOne)
			return question(message)
		else:
			session.attributes['notSeasonalIngredient'] = ingredientTwo
			newEntry = GroceryList(name=ingredientOne)
			db.session.add(newEntry)
			db.session.commit()
			message = "I added {}, but {} is not a seasonal ingredient, are you sure you want to add it to the list".format(ingredientOne, ingredientTwo)
			return question(message)
	else:
		session.attributes['notSeasonalIngredientOne'] = ingredientOne
		session.attributes['notSeasonalIngredientTwo'] = ingredientTwo
		message = "{} and {} both aren't seasonal ingredients, are you sure you want to add them".format(ingredientOne, ingredientTwo)
		return question(message)


@ask.intent("YesAddItAnywayIntent")
def yesAddItAnyway():
	notSeasonalIngredientsList = []
	try:
		notSeasonalIngredient = session.attributes['notSeasonalIngredient']
		newEntry = GroceryList(name=notSeasonalIngredient)
		db.session.add(newEntry)
		db.session.commit()
		message = "As you wish, I added {}.".format(notSeasonalIngredient)
		return statement(message)
	except KeyError:
		notSeasonalIngredientOne = session.attributes['notSeasonalIngredientOne']
		notSeasonalIngredientTwo = session.attributes['notSeasonalIngredientTwo']
		notSeasonalIngredientsList.append(notSeasonalIngredientOne)
		notSeasonalIngredientsList.append(notSeasonalIngredientTwo)
		for item in notSeasonalIngredientsList:
			newEntry = GroceryList(name=item)
			db.session.add(newEntry)
		db.session.commit()
		message = "Ok, I added {} and {} to your list".format(notSeasonalIngredientOne, notSeasonalIngredientTwo)
		return statement(message)



@ask.intent("NoRemoveItIntent")
def noRemoveIt():
	notSeasonalIngredientsList = []
	try:
		notSeasonalIngredient = session.attributes['notSeasonalIngredient']
		message = "Good choice, I removed {} from your list".format(notSeasonalIngredient) 
		return statement(message)
	except KeyError:
		notSeasonalIngredientOne = session.attributes['notSeasonalIngredientOne']
		notSeasonalIngredientTwo = session.attributes['notSeasonalIngredientTwo']
		notSeasonalIngredientsList.append(notSeasonalIngredientOne)
		notSeasonalIngredientsList.append(notSeasonalIngredientTwo)
		message = "Good choice, I removed {} and {} from your list".format(notSeasonalIngredientOne, notSeasonalIngredientTwo)
		return statement(message)


@ask.intent("ShowGroceryListIntent")
def showGroceryList():
	webbrowser.get('firefox').open('http://localhost:5000/grocery-list/')
	message = ("I'm opening your grocery list on your device")
	return statement(message)


@ask.intent("ReadGroceryListIntent")
def readGroceryList():
	ingredientsList = GroceryList.query.all()
	ingredientsNameList = []
	for ingredient in ingredientsList:
		ingredientsNameList.append(ingredient.name)
	fmtIngredientsList = commaFormat(ingredientsNameList)
	if len(ingredientsNameList) == 2:
		message = "There are {} and {} in your list".format(ingredientsNameList[0], ingredientsNameList[1])
	elif len(ingredientsNameList) > 1:
		message = "There are {} in your list".format(fmtIngredientsList)
	else:
		message = "There is {} in your list".format(fmtIngredientsList)

	return statement(message)
