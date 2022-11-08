from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from utilities.database_utility import DatabaseUtilities

# import routers
from routers import user_auth
from routers import contributions

# Create the metadata for OpenAPI auto documentation
tags_metadata = [
    {
        'name':"user_auth",
        'description':'Contains all endpoints related to user authentification. This includes an endpoint for creating an account, an endpoint for logging in (using JWT tokens) and finally an endpoint for verifiying the JWT token if the API recieves a request that requires authentification.'
    },
    {
        'name':"contribute",
        'description':'Contains all endpoints related to community contributions.'
    },
]

# Check vailidity of the database
database_utilities = DatabaseUtilities()
database_utilities.verifyDatabase()

# Create a FastAPI application instance
# provide the generated metadata for the swagger auto-documentation
app = FastAPI(openapi_tags=tags_metadata)

# Allow all origins through the CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# include routers
app.include_router(user_auth.router)
app.include_router(contributions.router)