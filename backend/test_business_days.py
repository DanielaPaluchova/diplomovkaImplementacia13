"""
Quick test for business days calculation
Run: python backend/test_business_days.py
"""
from datetime import datetime, timedelta


def count_business_days(start_date: datetime, end_date: datetime) -> int:
    """Count business days (Mon-Fri) between two dates, excluding weekends"""
    if start_date > end_date:
        return 0
    
    # Normalize to start of day for accurate counting
    start = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
    end = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Calculate total days
    total_days = (end - start).days + 1
    
    # Calculate full weeks and remaining days
    full_weeks = total_days // 7
    remaining_days = total_days % 7
    
    # Full weeks contribute 5 business days each
    business_days = full_weeks * 5
    
    # Count business days in remaining days
    current = start + timedelta(days=full_weeks * 7)
    for _ in range(remaining_days):
        if current.weekday() < 5:  # Monday-Friday
            business_days += 1
        current += timedelta(days=1)
    
    return business_days


# Test cases
print("=" * 60)
print("BUSINESS DAYS CALCULATOR TEST")
print("=" * 60)
print()

# Test 1: Monday to Friday (same week) = 5 days
start = datetime(2024, 1, 1)  # Monday
end = datetime(2024, 1, 5)    # Friday
result = count_business_days(start, end)
print(f"Test 1: Monday to Friday (same week)")
print(f"  From: {start.strftime('%Y-%m-%d %A')}")
print(f"  To:   {end.strftime('%Y-%m-%d %A')}")
print(f"  Result: {result} business days")
print(f"  Expected: 5 ✓" if result == 5 else f"  Expected: 5 ✗")
print()

# Test 2: Monday to Sunday (1 week) = 5 days (excludes weekend)
start = datetime(2024, 1, 1)  # Monday
end = datetime(2024, 1, 7)    # Sunday
result = count_business_days(start, end)
print(f"Test 2: Monday to Sunday (includes weekend)")
print(f"  From: {start.strftime('%Y-%m-%d %A')}")
print(f"  To:   {end.strftime('%Y-%m-%d %A')}")
print(f"  Result: {result} business days")
print(f"  Expected: 5 ✓" if result == 5 else f"  Expected: 5 ✗")
print()

# Test 3: Monday to next Monday (8 days) = 6 business days
start = datetime(2024, 1, 1)  # Monday
end = datetime(2024, 1, 8)    # Monday
result = count_business_days(start, end)
print(f"Test 3: Monday to next Monday (8 days)")
print(f"  From: {start.strftime('%Y-%m-%d %A')}")
print(f"  To:   {end.strftime('%Y-%m-%d %A')}")
print(f"  Result: {result} business days")
print(f"  Expected: 6 ✓" if result == 6 else f"  Expected: 6 ✗")
print()

# Test 4: Saturday to Sunday (weekend only) = 0 days
start = datetime(2024, 1, 6)  # Saturday
end = datetime(2024, 1, 7)    # Sunday
result = count_business_days(start, end)
print(f"Test 4: Saturday to Sunday (weekend only)")
print(f"  From: {start.strftime('%Y-%m-%d %A')}")
print(f"  To:   {end.strftime('%Y-%m-%d %A')}")
print(f"  Result: {result} business days")
print(f"  Expected: 0 ✓" if result == 0 else f"  Expected: 0 ✗")
print()

# Test 5: Today to 10 calendar days = ? business days
today = datetime.now()
future = today + timedelta(days=10)
result = count_business_days(today, future)
print(f"Test 5: Today + 10 calendar days")
print(f"  From: {today.strftime('%Y-%m-%d %A')}")
print(f"  To:   {future.strftime('%Y-%m-%d %A')}")
print(f"  Result: {result} business days")
print(f"  (Expected: ~7-8 depending on weekday)")
print()

print("=" * 60)
print("✅ All tests completed!")
print("=" * 60)

