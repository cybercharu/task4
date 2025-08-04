def userEntity(item) -> dict:
    return {
        "username" : item["username"],
        "email": item["email"],
        "password" : item["password"],
        "role" : item["role"]
    }

def moviesEntity(items) -> dict:
    return{
        "movie_id" : items["movie_id"],
        "moviename" : items["moviename"],
        "moviedesc" : items["moviedesc"],
        "moviegenre": items["moviegenre"],
        "movieyear": items["movieyear"]
    }