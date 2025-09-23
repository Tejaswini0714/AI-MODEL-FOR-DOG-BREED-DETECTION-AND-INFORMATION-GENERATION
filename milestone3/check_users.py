
import pandas as pd
import os
from database import get_all_users

# Fetch all users
users = get_all_users()

# Convert BLOBs to string if needed
def ensure_str(val):
    if isinstance(val, bytes):
        return val.decode(errors="ignore")
    return val

# Create DataFrame
df = pd.DataFrame(users, columns=["id", "first_name", "last_name", "email", "password", "profile_pic"])

# Ensure profile_pic is string
df["profile_pic"] = df["profile_pic"].apply(ensure_str)

# Optional: make profile_pic clickable (works in Jupyter/HTML)
def make_clickable(path):
    if path and isinstance(path, str):
        if path.startswith("http"):
            return f'<a href="{path}" target="_blank">Profile Pic</a>'
        elif os.path.exists(path):
            return f'<a href="file:///{os.path.abspath(path)}" target="_blank">Profile Pic</a>'
    return "No Image"

df["profile_pic_link"] = df["profile_pic"].apply(make_clickable)

# Print DataFrame
print(df)

# Save to CSV
df.to_csv("users_list.csv", index=False)
print("\nUsers saved to users_list.csv")
