import jwt
from fastapi import Header, HTTPException

def verify_supabase_jwt(token: str) -> dict:
    try:
        # Decode the token payload to get the user ID
        payload = jwt.decode(token, options={"verify_signature": False})
        return payload
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_tenant(
    authorization: str = Header(None), 
    x_session_id: str = Header(None)
):
    # Check for Google User (Supabase Token)
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        user_data = verify_supabase_jwt(token)
        return {"type": "member", "id": user_data.get("sub")}
        
    # Check for Guest (Browser Session ID)
    if x_session_id:
        return {"type": "guest", "id": x_session_id}
        
    raise HTTPException(status_code=401, detail="Authentication missing")