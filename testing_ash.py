import streamlit_authenticator as stauth

hashed_passwords = stauth.Hasher(['Bunmaska']).generate()
print(hashed_passwords)