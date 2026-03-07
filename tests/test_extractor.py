import json
from app.tools.extractor import extract_travel


tests = [
    {
        "message": "Trip from Paris to Rome 2026-04-01 to 2026-04-05 for 2 adults",
        "expected": {"origin": "Paris", "destination": "Rome", "rooms": 2, "rooms_specified": False}
    },
    {
        "message": "Travel from Berlin to Madrid from 10 june 2026 to 15 june 2026 for 1 adult and 1 child",
        "expected": {"departure_date": "2026-06-10", "return_date": "2026-06-15", "children": 1, "rooms": 1, "rooms_specified": False}
    },
    {
        "message": "Trip from Paris to Rome 2026-04-01 to 2026-04-05 for 3 adults and 5 room",
        "expected": {"adults": 3, "rooms": 5, "rooms_specified": True}
    }
]


passed = 0

for i, test in enumerate(tests, 1):
    try:
        result = json.loads(extract_travel.invoke({"message": test["message"]}))

        success = True
        for key, value in test["expected"].items():
            if result.get(key) != value:
                success = False

        if success:
            print(f"Test {i}: PASSED")
            passed += 1
        else:
            print(f"Test {i}: FAILED")
            print("Expected:", test["expected"])
            print("Got:", result)

    except Exception as e:
        print(f"Test {i}: ERROR - {e}")

print("\n-----------------------")
print(f"{passed}/{len(tests)} tests passed")

if passed == len(tests):
    print("ALL TESTS PASSED")
else:
    print("SOME TESTS FAILED")