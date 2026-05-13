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

# ============================================
# CLEAN OLD BUILD
# ============================================

if os.path.exists(OUTPUT_DIR):
    shutil.rmtree(OUTPUT_DIR)

os.makedirs(RECIPE_OUTPUT_DIR)

# ============================================
# LOAD DATA
# ============================================

recipes_df = pd.read_csv(recipes_url)
ingredients_df = pd.read_csv(ingredients_url)
instructions_df = pd.read_csv(instructions_url)

# ============================================
# TEMPLATE ENGINE
# ============================================

env = Environment(
    loader=FileSystemLoader("templates")
)

index_template = env.get_template("index.html")
recipe_template = env.get_template("recipe.html")

# ============================================
# HELPERS
# ============================================

def slugify(text):
    text = str(text).lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")

def clean_value(val, fallback="Uncategorised"):
    if pd.isna(val) or str(val).strip() == "":
        return fallback
    return str(val).strip()

# ============================================
# BUILD RECIPE PAGES + GROUP DATA
# ============================================

grouped_recipes = defaultdict(lambda: defaultdict(list))

for _, recipe in recipes_df.iterrows():

    recipe_id = recipe["recipe_id"]

    # ------------------------
    # Get ingredients
    # ------------------------
    recipe_ingredients = ingredients_df[
        ingredients_df["recipe_id"] == recipe_id
    ].to_dict(orient="records")

    # ------------------------
    # Get instructions
    # ------------------------
    recipe_steps = instructions_df[
        instructions_df["recipe_id"] == recipe_id
    ].sort_values("step").to_dict(orient="records")

    # ------------------------
    # Create slug
    # ------------------------
    slug = slugify(recipe["recipe_name"])

    # ------------------------
    # Build recipe object
    # ------------------------
    recipe_data = {
        "id": recipe_id,
        "recipe_name": recipe["recipe_name"],
        "servings": recipe.get("servings", ""),
        "source": recipe.get("source", ""),
        "category": clean_value(recipe.get("category")),
        "cuisine": clean_value(recipe.get("cuisine")),
        "ingredients": recipe_ingredients,
        "steps": recipe_steps,
        "slug": slug
    }

    # ------------------------
    # Render recipe page
    # ------------------------
    recipe_html = recipe_template.render(
        recipe=recipe_data,
        title=recipe["recipe_name"]
    )

    output_path = os.path.join(
        RECIPE_OUTPUT_DIR,
        f"{slug}.html"
    )

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(recipe_html)

    print(f"Built recipe: {slug}")

    # ------------------------
    # GROUPING (Category → Cuisine)
    # ------------------------
    category = recipe_data["category"]
    cuisine = recipe_data["cuisine"]

    grouped_recipes[category][cuisine].append(recipe_data)

# ============================================
# BUILD HOMEPAGE
# ============================================

homepage_html = index_template.render(
    grouped_recipes=grouped_recipes,
    title="Recipe Website",
    description="Easy homemade recipes"
)

with open(
    os.path.join(OUTPUT_DIR, "index.html"),
    "w",
    encoding="utf-8"
) as f:
    f.write(homepage_html)

print("Built homepage")

# ============================================
# COPY STATIC FILES
# ============================================

if os.path.exists("static"):
    shutil.copytree(
        "static",
        OUTPUT_DIR,
        dirs_exist_ok=True
    )
    print("Copied static files")

# ============================================
# BUILD COMPLETE
# ============================================

print("Site build complete")
