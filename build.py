import os
import re
import shutil
import pandas as pd
from jinja2 import Environment, FileSystemLoader
from collections import defaultdict

# ============================================
# CONFIG
# ============================================

recipes_url = "https://docs.google.com/spreadsheets/d/19EdezjfCuFwYmWSd4SKlamLAJeOOR2Yn7b2QFPCBN0s/export?format=csv&gid=0"

ingredients_url = "https://docs.google.com/spreadsheets/d/19EdezjfCuFwYmWSd4SKlamLAJeOOR2Yn7b2QFPCBN0s/export?format=csv&gid=1549265114"

instructions_url = "https://docs.google.com/spreadsheets/d/19EdezjfCuFwYmWSd4SKlamLAJeOOR2Yn7b2QFPCBN0s/export?format=csv&gid=112480317"

OUTPUT_DIR = "dist"
RECIPE_OUTPUT_DIR = os.path.join(OUTPUT_DIR, "recipes")
CATEGORY_DIR = os.path.join(OUTPUT_DIR, "category")

# ============================================
# CLEAN BUILD
# ============================================

if os.path.exists(OUTPUT_DIR):
    shutil.rmtree(OUTPUT_DIR)

os.makedirs(RECIPE_OUTPUT_DIR)
os.makedirs(CATEGORY_DIR)

# ============================================
# LOAD DATA
# ============================================

recipes_df = pd.read_csv(recipes_url)
ingredients_df = pd.read_csv(ingredients_url)
instructions_df = pd.read_csv(instructions_url)

#remove empty rows
def clean_df(df):
    df = df.dropna(how="all")
    df = df[df["recipe_id"].notna()]
    return df

recipes_df = clean_df(recipes_df)
ingredients_df = clean_df(ingredients_df)
instructions_df = clean_df(instructions_df)

# ============================================
# TEMPLATE ENGINE
# ============================================

env = Environment(loader=FileSystemLoader("templates"))

index_template = env.get_template("index.html")
category_template = env.get_template("category.html")
cuisine_template = env.get_template("cuisine.html")
recipe_template = env.get_template("recipe.html")

# ============================================
# HELPERS
# ============================================

def slugify(text):
    text = str(text).lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")

def clean(val):
    if pd.isna(val) or str(val).strip() == "":
        return "Uncategorised"
    return str(val).strip()

# ============================================
# DATA STRUCTURE
# ============================================

structure = defaultdict(lambda: defaultdict(list))

all_recipes = []

# ============================================
# BUILD RECIPES
# ============================================

for _, recipe in recipes_df.iterrows():

    recipe_id = recipe["recipe_id"]

    ingredients = ingredients_df[ingredients_df["recipe_id"] == recipe_id].to_dict("records")
    steps = instructions_df[instructions_df["recipe_id"] == recipe_id].sort_values("step").to_dict("records")

    category = clean(recipe.get("category"))
    cuisine = clean(recipe.get("cuisine"))
    slug = slugify(recipe["recipe_name"])

    recipe_data = {
        "id": recipe_id,
        "recipe_name": recipe["recipe_name"],
        "servings": recipe.get("servings", ""),
        "source": recipe.get("source", ""),
        "category": category,
        "cuisine": cuisine,
        "ingredients": ingredients,
        "steps": steps,
        "slug": slug
    }


    # Save recipe page
    recipe_html = recipe_template.render(recipe=recipe_data, title=recipe_data["recipe_name"])

    with open(os.path.join(RECIPE_OUTPUT_DIR, f"{slug}.html"), "w", encoding="utf-8") as f:
        f.write(recipe_html)

    structure[category][cuisine].append(recipe_data)
    all_recipes.append(recipe_data)


print("CATEGORIES:", list(structure.keys()))

# ============================================
# INDEX PAGE (CATEGORIES ONLY)
# ============================================

index_html = index_template.render(
    categories=sorted(structure.keys()),
    title="Recipes"
)

with open(os.path.join(OUTPUT_DIR, "index.html"), "w", encoding="utf-8") as f:
    f.write(index_html)

# ============================================
# CATEGORY PAGES (SHOW CUISINES)
# ============================================

for category, cuisines in structure.items():

    category_slug = slugify(category)

    category_html = category_template.render(
        category=category,
        cuisines=sorted(cuisines.keys())
    )

    folder = os.path.join(CATEGORY_DIR, category_slug)
    os.makedirs(folder, exist_ok=True)

    with open(os.path.join(folder, "index.html"), "w", encoding="utf-8") as f:
        f.write(category_html)

# ============================================
# CUISINE PAGES (SHOW RECIPES)
# ============================================

for category, cuisines in structure.items():
    for cuisine, recipes in cuisines.items():

        category_slug = slugify(category)
        cuisine_slug = slugify(cuisine)

        cuisine_html = cuisine_template.render(
            category=category,
            cuisine=cuisine,
            recipes=recipes
        )

        folder = os.path.join(CATEGORY_DIR, category_slug, cuisine_slug)
        os.makedirs(folder, exist_ok=True)

        with open(os.path.join(folder, "index.html"), "w", encoding="utf-8") as f:
            f.write(cuisine_html)

# ============================================
# STATIC FILES
# ============================================

if os.path.exists("static"):
    shutil.copytree("static", OUTPUT_DIR, dirs_exist_ok=True)

print("Build complete")
