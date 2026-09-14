from datetime import date, datetime

from .extensions import db


class Food(db.Model):
    """Продукт. Нутриенты — всегда на 100 г."""
    __tablename__ = "foods"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    brand = db.Column(db.String(120))
    kcal = db.Column(db.Float, nullable=False, default=0)     # на 100 г
    protein = db.Column(db.Float, nullable=False, default=0)
    fat = db.Column(db.Float, nullable=False, default=0)
    carbs = db.Column(db.Float, nullable=False, default=0)
    is_default = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def per_100g(self):
        return {"kcal": self.kcal, "protein": self.protein, "fat": self.fat, "carbs": self.carbs}

    def nutrition_for(self, grams):
        from .calc import scale
        return scale(self.per_100g(), grams)

    def to_dict(self):
        return {
            "id": self.id, "name": self.name, "brand": self.brand,
            "kcal": self.kcal, "protein": self.protein, "fat": self.fat, "carbs": self.carbs,
            "is_default": self.is_default,
        }


class DishIngredient(db.Model):
    __tablename__ = "dish_ingredients"
    id = db.Column(db.Integer, primary_key=True)
    dish_id = db.Column(db.Integer, db.ForeignKey("dishes.id", ondelete="CASCADE"), nullable=False, index=True)
    food_id = db.Column(db.Integer, db.ForeignKey("foods.id"), nullable=False, index=True)
    grams = db.Column(db.Float, nullable=False)
    food = db.relationship("Food", lazy="joined")
    dish = db.relationship("Dish", back_populates="ingredients")

    def to_dict(self):
        f = self.food
        return {
            "food_id": self.food_id,
            "food_name": f.name if f else None,
            "grams": self.grams,
            "kcal": round(f.kcal * self.grams / 100, 1) if f else 0,
            "protein": round(f.protein * self.grams / 100, 1) if f else 0,
            "fat": round(f.fat * self.grams / 100, 1) if f else 0,
            "carbs": round(f.carbs * self.grams / 100, 1) if f else 0,
        }


class Dish(db.Model):
    """Готовое блюдо. Может быть:
      • из ингредиентов (manual=False) — КБЖУ считается автоматически;
      • ручным (manual=True) — КБЖУ задаётся на порцию (как на этикетке блюда).
    Для единообразия логирования всё приводится к нутриентам на 100 г."""
    __tablename__ = "dishes"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    portion_g = db.Column(db.Float, default=100.0, nullable=False)
    manual = db.Column(db.Boolean, default=False, nullable=False)
    # Ручные значения — НА ПОРЦИЮ (имеют смысл только при manual=True)
    kcal = db.Column(db.Float, default=0)
    protein = db.Column(db.Float, default=0)
    fat = db.Column(db.Float, default=0)
    carbs = db.Column(db.Float, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    ingredients = db.relationship("DishIngredient", back_populates="dish",
                                 cascade="all, delete-orphan", lazy="joined")

    def ingredients_nutrition(self):
        total = {"kcal": 0.0, "protein": 0.0, "fat": 0.0, "carbs": 0.0, "weight": 0.0}
        for ing in self.ingredients:
            f = ing.food
            if not f:
                continue
            g = ing.grams or 0
            total["kcal"] += f.kcal * g / 100
            total["protein"] += f.protein * g / 100
            total["fat"] += f.fat * g / 100
            total["carbs"] += f.carbs * g / 100
            total["weight"] += g
        return total

    def per_100g(self):
        if self.manual:
            p = self.portion_g or 100
            return {"kcal": (self.kcal or 0) * 100 / p,
                    "protein": (self.protein or 0) * 100 / p,
                    "fat": (self.fat or 0) * 100 / p,
                    "carbs": (self.carbs or 0) * 100 / p}
        t = self.ingredients_nutrition()
        w = t["weight"] or 0
        if w <= 0:
            return {"kcal": 0, "protein": 0, "fat": 0, "carbs": 0}
        return {"kcal": t["kcal"] * 100 / w, "protein": t["protein"] * 100 / w,
                "fat": t["fat"] * 100 / w, "carbs": t["carbs"] * 100 / w}

    def per_portion(self):
        from .calc import scale
        return scale(self.per_100g(), self.portion_g or 100)

    def nutrition_for(self, grams):
        from .calc import scale
        return scale(self.per_100g(), grams)

    def to_dict(self):
        return {
            "id": self.id, "name": self.name, "portion_g": self.portion_g, "manual": self.manual,
            "kcal": self.kcal, "protein": self.protein, "fat": self.fat, "carbs": self.carbs,
            "per_100g": {k: round(v, 1) for k, v in self.per_100g().items()},
            "per_portion": {k: round(v, 1) for k, v in self.per_portion().items()},
            "ingredients": [i.to_dict() for i in self.ingredients],
        }


class MealItem(db.Model):
    """Запись в дневнике питания. grams — сколько грамм съедено."""
    __tablename__ = "meal_items"

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, index=True)
    meal_type = db.Column(db.String(20), default="other", nullable=False)  # breakfast/lunch/dinner/snack/other
    source_type = db.Column(db.String(10), nullable=False)  # 'food' | 'dish'
    food_id = db.Column(db.Integer, db.ForeignKey("foods.id"))
    dish_id = db.Column(db.Integer, db.ForeignKey("dishes.id"))
    grams = db.Column(db.Float, nullable=False)
    label = db.Column(db.String(200))  # снапшот названия — чтобы дневник читался даже после переименования
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    food = db.relationship("Food")
    dish = db.relationship("Dish")

    def nutrition(self):
        if self.source_type == "food" and self.food:
            return self.food.nutrition_for(self.grams)
        if self.source_type == "dish" and self.dish:
            return self.dish.nutrition_for(self.grams)
        return {"kcal": 0, "protein": 0, "fat": 0, "carbs": 0}

    def display_name(self):
        if self.label:
            return self.label
        if self.source_type == "food" and self.food:
            return self.food.name
        if self.source_type == "dish" and self.dish:
            return self.dish.name
        return "?"

    def to_dict(self):
        n = self.nutrition()
        return {
            "id": self.id, "date": self.date.isoformat(), "meal_type": self.meal_type,
            "source_type": self.source_type, "food_id": self.food_id, "dish_id": self.dish_id,
            "grams": self.grams, "label": self.display_name(),
            "kcal": round(n["kcal"], 1), "protein": round(n["protein"], 1),
            "fat": round(n["fat"], 1), "carbs": round(n["carbs"], 1),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class WeightEntry(db.Model):
    __tablename__ = "weight_entries"
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, index=True)
    weight_kg = db.Column(db.Float, nullable=False)
    note = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {"id": self.id, "date": self.date.isoformat(),
                "weight_kg": self.weight_kg, "note": self.note}


class Activity(db.Model):
    """Активность (этап 2): ходьба/велосипед/прочее. kcal — это ОЦЕНКА, не точное число."""
    __tablename__ = "activities"
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, index=True)
    type = db.Column(db.String(20), nullable=False)  # walk | bike | other
    steps = db.Column(db.Integer, default=0)
    distance_km = db.Column(db.Float, default=0)
    duration_min = db.Column(db.Integer, default=0)
    kcal = db.Column(db.Float, default=0)
    note = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {"id": self.id, "date": self.date.isoformat(), "type": self.type,
                "steps": self.steps, "distance_km": self.distance_km,
                "duration_min": self.duration_min, "kcal": self.kcal, "note": self.note}


class Profile(db.Model):
    """Один профиль-синглтон (id=1). Цели по КБЖУ и стартовые показатели.
    Появится нормальная авторизация — станет per-user (этап 6)."""
    __tablename__ = "profile"
    id = db.Column(db.Integer, primary_key=True)
    target_kcal = db.Column(db.Float, default=2000)
    target_protein_g = db.Column(db.Float, default=130)
    target_fat_g = db.Column(db.Float, default=70)
    target_carbs_g = db.Column(db.Float, default=200)
    height_cm = db.Column(db.Float, default=0)
    start_weight_kg = db.Column(db.Float, default=0)
    activity_level = db.Column(db.String(20), default="low")
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {"target_kcal": self.target_kcal, "target_protein_g": self.target_protein_g,
                "target_fat_g": self.target_fat_g, "target_carbs_g": self.target_carbs_g,
                "height_cm": self.height_cm, "start_weight_kg": self.start_weight_kg,
                "activity_level": self.activity_level}
