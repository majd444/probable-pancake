from setuptools import setup, find_packages

setup(
    name="chatbot-backend",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi==0.95.2",
        "uvicorn==0.22.0",
        "python-dotenv==1.0.0",
        "supabase==2.3.4",
        "requests==2.31.0",
        "pydantic==1.10.7",
        "python-multipart==0.0.6",
        "httpx==0.24.1",
        "python-jose[cryptography]==3.3.0",
        "passlib[bcrypt]==1.7.4"
    ],
    python_requires='>=3.8',
)
