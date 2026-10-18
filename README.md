# Social Sphere — Social Media API + Frontend

Portfolio-ready Django REST social application with JWT authentication and a responsive HTML/CSS/JavaScript frontend.

## Features
- Secure signup/login with JWT
- Text posts with captions
- Image/video posts using file upload only (no media URL fields in the Create Post UI)
- Uploaded media is rendered directly in the feed; URLs are internal implementation details
- Full image/video aspect ratio is preserved; media is never cropped by the feed CSS
- Like/unlike, comments, save/unsave, follow/unfollow
- Trending feed and search
- PostgreSQL-ready production configuration
- Cloudinary support for persistent production media storage

## Run locally
```powershell
python -m venv env
env\Scripts\activate
python -m pip install -r requirements.txt
$env:SECRET_KEY = "local-development-secret-change-me"
$env:DEBUG = "True"
python manage.py migrate
python manage.py runserver
```
Frontend in a second terminal:
```powershell
cd frontend
python -m http.server 5500
```
Open `http://127.0.0.1:5500`.

## Production media
Render's local filesystem is temporary. Set `CLOUDINARY_URL` in Render Environment before enabling image/video uploads on the live site. The backend automatically uploads image files as images and video files as videos to Cloudinary and stores only the returned secure media address internally.
