from db_operations import add_member, get_project_members

# Add team members to Project ID 1

member1 = add_member(
    1,
    "Rahul Sharma",
    "Backend Developer",
    "rahul@example.com"
)

member2 = add_member(
    1,
    "Priya Patil",
    "Frontend Developer",
    "priya@example.com"
)

print("Team members added successfully!")

# Retrieve team members

members = get_project_members(1)

print("\nProject Team Members:")

for member in members:
    print(member)