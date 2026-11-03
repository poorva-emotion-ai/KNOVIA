from db_operations import (
    add_update,
    get_project_updates,
    add_decision,
    get_project_decisions
)

# Use existing project ID 1
project_id = 1

# Add project updates
add_update(project_id, 1, "Database design completed.")
add_update(project_id, 2, "Dashboard development started.")

# Add decisions
add_decision(project_id, "Database Selection",
             "SQLite selected for database management.")

add_decision(project_id, "Frontend Selection",
             "Streamlit selected for frontend development.")

# Display updates
print("\nPROJECT UPDATES")
for update in get_project_updates(project_id):
    print(update)

# Display decisions
print("\nPROJECT DECISIONS")
for decision in get_project_decisions(project_id):
    print(decision)

print("\nProject history saved successfully!")