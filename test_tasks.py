from db_operations import (
    add_update,
    get_project_updates,
    add_decision,
    get_project_decisions
)

# Add project updates
add_update(1, 1, "Database design completed.")
add_update(1, 2, "Dashboard development started.")

# Add project decisions
add_decision(1, 1, "SQLite selected for database management.")
add_decision(1, 2, "Streamlit selected for frontend development.")

# Display updates
print("\nPROJECT UPDATES")

for update in get_project_updates(1):
    print(update)

# Display decisions
print("\nPROJECT DECISIONS")

for decision in get_project_decisions(1):
    print(decision)

print("\nProject history saved successfully!")