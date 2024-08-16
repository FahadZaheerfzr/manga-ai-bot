from components.campaign import get_hashed_password


passw = get_hashed_password("pass")

print(passw)