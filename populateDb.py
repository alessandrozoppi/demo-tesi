import os
from app import app, db
from app.models import Recipe, Ingredient, Step, Counter

def resetDb():
	print("========== RESET DATABASE ==========\n")
	basedir = os.path.abspath(os.path.dirname(__file__))
	targetDbPath = os.path.join(basedir, 'database.db')
	os.remove(targetDbPath)
	print("Database successfully deleted") 
	db.create_all()
	print("Databse successfully reset\n")

def setCountersValues():
	print("========== COUNTERS ==========\n")
	gbRecipeId = Counter(name="gbRecipeId", counter=1)
	gbStepNumber = Counter(name="gbStepNumber", counter=2)
	db.session.add(gbRecipeId)
	print("Added gbRecipeId")
	db.session.add(gbStepNumber)
	print("Added gbStepNumber")
	db.session.commit()
	print("Counters successfully set\n")

def populateRecipesList():
	print("========== RECIPES ==========\n")
	recipesList = ["pasta carbonara", "chocolate cake"]
	for recipe in recipesList:
		recipeUrlTitle = recipe.replace(" ", "")
		newRecipeEntry = Recipe(title=recipe, url_title=recipeUrlTitle)
		db.session.add(newRecipeEntry)
		print("Added, "'"' + recipe + '"')
	db.session.commit()
	print("Recipes successfully saved into the database\n")

def populateIngredientsList():
	print("========== INGREDIENTS ==========\n")
	
	def addIngredientsToRecipe(ingredientsList, recipeId):
		for ingredient in ingredientsList:
			newIngredientEntry = Ingredient(name=ingredient, recipe_id=recipeId)
			db.session.add(newIngredientEntry)
			print("Added", '"' + ingredient + '"')
		print("\n")

	carbonaraIngredientsList = [
								"150 grams of guanciale",
								"6 egg yolks",
								"50 grams of pecorino romano",
								"Salt qs.",
								"Pepper qs."]
	chococakeIngredientsList = [
								"200 grams of dark chocolate",
								"4 eggs",
								"100 grams of butter",
								"200 grams of sugar",
								"1 vanilla sachet"]

	addIngredientsToRecipe(carbonaraIngredientsList, 1)
	addIngredientsToRecipe(chococakeIngredientsList, 2)
	db.session.commit()
	print("Ingredients successfully saved into the database\n")

def populateStepsList():
	print("========== STEPS ==========")
	
	def addStepsToRecipe(stepsList, recipeId):
		orderCounter = 1
		for step in stepsList:
			newStepEntry = Step(order=orderCounter, content=step, recipe_id=recipeId)
			db.session.add(newStepEntry)
			orderCounter += 1
			print("Added", '"' + step + '"', "with oreder =", orderCounter-1)
		print("\n")

	carbonaraStepsList = [
							"start by putting on the cooker a pot filled with salted water",
							"cut the guanciale in stripes and brown them in a cooking pan for 15 minutes",
							"as soon as the water starts boiling, add the pasta inside the pot for the amount of time suggested by the package",
							"mix the egg yolks with the pecorino using a kitchen whisk",
							"finally drain the pasta, add the mixture and spice it with pepper"]
	chococakeStepsList = [
							"start by melting the dark chocolate with the butter on the cooker, preferably with the water bath method",
							"mix the egg yolks with sugar and the vanilla using a kitchen whisk",
							"whip the egg whites and mix everything together",
							"finally pour the mixture into a buttered baking tin and cook it in the oven for 40 minutes at 180 degrees celsius"]
	
	addStepsToRecipe(carbonaraStepsList, 1)
	addStepsToRecipe(chococakeStepsList, 2)
	db.session.commit()
	print("Steps successfully saved into the database\n")

resetDb()
setCountersValues()
populateRecipesList()
populateIngredientsList()
populateStepsList()

print("You are good to go!")

