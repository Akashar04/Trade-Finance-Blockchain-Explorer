from pydantic import BaseModel, EmailStr, field_validator, Field


class LoginRequest(BaseModel):
    email: str = Field(..., example="akash@test.com", description="Registered email address")
    password: str = Field(..., example="Test@123", description="Account password")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "akash@test.com",
                "password": "Test@123"
            }
        }
    }


class TokenResponse(BaseModel):
    access_token: str = Field(..., description="JWT access token for API requests (valid 15 minutes)")
    token_type: str = Field(default="bearer", description="Token type (always 'bearer')")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNjc0NzcyODAwLCJleHAiOjE2NzQ3NzMzMDB9",
                "token_type": "bearer"
            }
        }
    }


class SignupRequest(BaseModel):
    name: str = Field(..., example="Akash Ramanni", description="Full name")
    email: EmailStr = Field(..., example="akash@test.com", description="Email address (must be unique)")
    password: str = Field(..., example="Test@123", description="Password (note: max 72 bytes due to bcrypt)")
    org: str = Field(..., example="QWE Bank", description="Organization name")
    role: str = Field(..., example="buyer", description="User role: buyer, seller, auditor, or bank")
    
    @field_validator('password')
    @classmethod
    def validate_password_required(cls, v):
        """Ensure password is not empty. Bcrypt will enforce 72-byte limit."""
        if not v or len(v) < 1:
            raise ValueError('Password is required')
        if len(v.encode('utf-8')) > 72:
            raise ValueError('Password must be 72 bytes or less')
        return v
    
    @field_validator('role')
    @classmethod
    def validate_role(cls, v):
        valid_roles = ['buyer', 'seller', 'auditor', 'bank']
        if v.lower() not in valid_roles:
            raise ValueError(f'Role must be one of: {", ".join(valid_roles)}')
        return v.lower()
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Akash Ramanni",
                "email": "akash@test.com",
                "password": "Test@123",
                "org": "QWE Bank",
                "role": "buyer"
            }
        }
    }


class MessageResponse(BaseModel):
    message: str = Field(..., description="Response message")


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    organization_id: int | None = None
    
    class Config:
        from_attributes = True
