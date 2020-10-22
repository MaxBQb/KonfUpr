def makeUser(user: str) -> dict:
    if not isinstance(user, str):
        raise TypeError(f"str expected, got: {type(user).__name__}")
    home = f"/home/{user}"
    privateKey = f"{home}/.ssh/id_ed25519"
    publicKey = f"{privateKey}.pub"
    return dict(
        home=home,
        privateKey=privateKey,
        publicKey=publicKey
    )
