import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split

# ---------------------------
# (a) Load and explore data
# ---------------------------
dataDir = "/Users/paolacassinelli/Desktop/Foundation of Machine Learning/Assignment_1_FML_DSBA/"
path = dataDir + "fantasy_100.json"

with open(path) as f:
    data = [json.loads(line) for line in f]

ratings = [d["rating"] for d in data]

rating_counts = Counter(ratings)

plt.bar(rating_counts.keys(), rating_counts.values(), color="skyblue")
plt.xlabel("Star Rating")
plt.ylabel("Number of Reviews")
plt.title("Distribution of Ratings")
for rating, count in rating_counts.items():
    plt.text(rating, count + 0.1, str(count), ha="center", va="bottom")
plt.show()

# ---------------------------
# (b) Simple linear regression: rating ~ review length
# ---------------------------
X = np.array([len(d["review_text"]) for d in data]).reshape(-1, 1)
y = np.array(ratings)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = LinearRegression()
model.fit(X_train, y_train)

theta0 = model.intercept_
theta1 = model.coef_[0]

y_pred_train = model.predict(X_train)
y_pred_test = model.predict(X_test)

mse_train = mean_squared_error(y_train, y_pred_train)
mse_test = mean_squared_error(y_test, y_pred_test)

print("\n--- (b) Simple Linear Regression ---")
print(f"Theta0: {theta0:.4f}, Theta1: {theta1:.8f}")
print(f"MSE (train): {mse_train:.4f}")
print(f"MSE (test): {mse_test:.4f}")

# ---------------------------
# (c) Linear regression: rating ~ review length + n_comments
# ---------------------------
X2 = np.array([[len(d["review_text"]), d["n_comments"]] for d in data])
X2_train, X2_test, y_train, y_test = train_test_split(X2, y, test_size=0.2, random_state=42)

model2 = LinearRegression()
model2.fit(X2_train, y_train)

theta0, theta1, theta2 = model2.intercept_, model2.coef_[0], model2.coef_[1]

y_pred_train2 = model2.predict(X2_train)
y_pred_test2 = model2.predict(X2_test)

mse_train2 = mean_squared_error(y_train, y_pred_train2)
mse_test2 = mean_squared_error(y_test, y_pred_test2)

print("\n--- (c) Linear Regression with Two Features ---")
print(f"Theta0: {theta0:.4f}, Theta1 (length): {theta1:.8f}, Theta2 (n_comments): {theta2:.8f}")
print(f"MSE (train): {mse_train2:.4f}")
print(f"MSE (test): {mse_test2:.4f}")

# ---------------------------
# (d) Polynomial features: rating ~ poly(review length, n_comments)
# ---------------------------
poly = PolynomialFeatures(degree=2, include_bias=False)
X_train_poly = poly.fit_transform(X2_train)
X_test_poly = poly.transform(X2_test)

model_poly = LinearRegression()
model_poly.fit(X_train_poly, y_train)

y_pred_train_poly = model_poly.predict(X_train_poly)
y_pred_test_poly = model_poly.predict(X_test_poly)

mse_train_poly = mean_squared_error(y_train, y_pred_train_poly)
mse_test_poly = mean_squared_error(y_test, y_pred_test_poly)

feature_names = poly.get_feature_names_out(["length", "n_comments"])
print("\n--- (d) Polynomial Linear Regression (degree=2) ---")
print(f"Intercept (theta0): {model_poly.intercept_:.4f}")
print("Coefficients (theta vector aligned with feature list):")
for name, coef in zip(feature_names, model_poly.coef_):
    print(f"{name}: {coef:.8f}")
print(f"MSE (train): {mse_train_poly:.4f}")
print(f"MSE (test): {mse_test_poly:.4f}")
