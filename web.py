
import os
os.makedirs("output", exist_ok=True)
print("TEST 123")
with open("output/index.html", "w") as f:
    f.write("<h1>Test</h1>")
