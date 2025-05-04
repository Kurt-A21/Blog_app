# 🌐 FastAPI Social Media App

A lightweight social media backend built with **FastAPI**, designed for speed, simplicity, and modern authentication using **OAuth2**.

---

## 🚀 Features

- 🧑‍💻 User registration & login via \*\*OAuth2
- 🔐 Secure authentication with JWT tokens
- 📸 Post creation and retrieval
- 👍 Reactions functionality
- 🧵 Commenting system
- 🔄 Follow/unfollow users
- 🛡️ Protected routes with user permissions
- 🛡️ Role-based access control (User vs Admin)
- 🧙‍♂️ Admin endpoints for user & content management

---

## 🛠️ Tech Stack

- FastAPI
- OAuth2 with Password and Bearer
- SQLAlchemy
- SQLite
- JWT

---

## 📦 Setup Instructions

### 1. Clone Repo

```bash
git clone git@github.com:Kurt-A21/social_media_api.git
cd social_media_api
```

### 2. Create Virtual Environment

```bash
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

Create .env in social_media_api/app

```bash
SECRET_KEY="" # Use openssl rand -base64 48 in terminal
ALGORITHM="HS256"
DATABASE_URL="sqlite:///./social_media_app.db"
EMAIL_ADDRESS="youremail@gmail.com"
APP_PASSWORD="" # Your email app password. Remove all whitepaces
SMTP_SERVER="" # Your smtp server e.g. smtp.gmail.com
SMTP_PORT= #e.g 465
```

### 5. Run App

```bash
uvicorn app.main:app --reload
```

### 6. Open Swagger UI

```bash
http://127.0.0.1:8000/docs
```

---

## 📬 API Endpoints

### 🔐 Auth

| Method | Endpoint                      | Description                                        | Auth Required |
| ------ | ----------------------------- | -------------------------------------------------- | ------------- |
| POST   | /auth/regsiter                | Create a user                                      |               |
| POST   | /auth/login                   | Login and create bearer token                      |               |
| POST   | /auth/forgot_password/{email} | Sends JWT reset token to email                     |               |
| PUT    | /auth/reset_password/         | Validates JWT reset token to enable password reset |               |
| POST   | /auth/logout                  | Logout account                                     | Yes(JWT)      |

### 🧙‍♂️ Admin Routes (Role: Admin)

| Method | Endpoint                                   | Description                       | Auth Required |
| ------ | ------------------------------------------ | --------------------------------- | ------------- |
| GET    | /admin/                                    | Get all users details             | Yes(Admin)    |
| GET    | /admin/get_user_by_id                      | Get user by user id or account id | Yes(Admin)    |
| DELETE | /admin/user/{user_id}/delete_user          | Delete a user                     | Yes(Admin)    |
| DELETE | /admin/post/{post_id}/delete_post          | Delete a user's post              | Yes(Admin)    |
| DE:ETE | /admin/post/{post_id}/comment/{comment_id} | Delete a comment                  | Yes(Admin)    |

### 🧑 User Routes

| Method | Endpoint                      | Description                                  | Auth Required |
| ------ | ----------------------------- | -------------------------------------------- | ------------- |
| GET    | /users                        | Get all users, their followers and following | No            |
| GET    | /users/current_user           | Get current user details                     | Yes(JWT)      |
| PUT    | /users/change_password        | Update current user password                 | Yes(JWT)      |
| PUT    | /users/update_user            | Update current user details                  | Yes(JWT)      |
| PUT    | /users/update_email           | Update current user details                  | Yes(JWT)      |
| POST   | /users/upload_profile_picture | Upload a profile picture                     | Yes(JWT)      |
| PUT    | /users/update_profile_picture | Update profile picture                       | Yes(JWT)      |
| DELETE | /users/remove_profile_picture | Remove profile picture                       | Yes(JWT)      |
| DELETE | /users/deactivate_account     | Delete account and all related user data     | Yes(JWT)      |

### 👥 Follow Routes

| Method | Endpoint                   | Description                     | Auth Required |
| ------ | -------------------------- | ------------------------------- | ------------- |
| GET    | /users/{user_id}followers  | Get a specific user's followers | No            |
| GET    | /users/{user_id}/following | Get a specific user's following | No            |
| POST   | /users/{user_id}/follow    | Follow a user                   | Yes(JWT)      |
| DELETE | /users/{user_id}/unfollow  | Unfollow a user                 | Yes(JWT)      |

### 📸 Post Routes

| Method | Endpoint                      | Description                                                                                | Auth Required |
| ------ | ----------------------------- | ------------------------------------------------------------------------------------------ | ------------- |
| GET    | /posts                        | Get all posts by users, along with their comments and reactions on both posts and comments | No            |
| GET    | /posts/user/{user_id}         | Get a specific user's timeline of posts                                                    | No            |
| POST   | /posts/create                 | Create a post, tag users                                                                   | Yes(JWT)      |
| PUT    | /posts/{post_id}/update_post  | Update a post                                                                              | Yes(JWT)      |
| DELETE | /posts/{post_id}/delete_tag   | Remove user tags from a post                                                               | Yes(JWT)      |
| DELETE | /posts/{post_id}/delete_post  | Delete a post                                                                              | Yes(JWT)      |
| POST   | /posts/{post_id}/upload_image | Upload a image to a post                                                                   | Yes(JWT)      |
| DELETE | /posts/{post_id}/update_image | Update image on a post                                                                     | Yes(JWT)      |
| DELETE | /posts/{post_id}/remove_image | Remove image from a post                                                                   | Yes(JWT)      |

### 💬 Comment Routes

| Method | Endpoint                              | Description       | Auth Required |
| ------ | ------------------------------------- | ----------------- | ------------- |
| POST   | /posts/{post_id}comment               | Comment on a post | Yes(JWT)      |
| PUT    | /posts/{post_id}/comment/{comment_id} | Update a comment  | Yes(JWT)      |
| DELETE | /posts/{post_id}/comment/{comment_id} | Delete a comment  | Yes(JWT)      |

### 💬 Comment Reply Routes

| Method | Endpoint                                               | Description        | Auth Required |
| ------ | ------------------------------------------------------ | ------------------ | ------------- |
| POST   | /posts/{post_id}comment/{comment_id}/reply             | Reply on a comment | Yes(JWT)      |
| PUT    | /posts/{post_id}/comment/{comment_id}/reply/{reply_id} | Update a reply     | Yes(JWT)      |
| DELETE | /posts/{post_id}/comment/{comment_id}/reply/{reply_id} | Delete a reply     | Yes(JWT)      |

### 👍 Reaction Routes

| Method | Endpoint                                                                      | Description                    | Auth Required |
| ------ | ----------------------------------------------------------------------------- | ------------------------------ | ------------- |
| POST   | /posts/{post_id}/reaction                                                     | React on a post                | Yes(JWT)      |
| POST   | /posts/{post_id}/comment/{comment_id}/reaction                                | React on a comment             | Yes(JWT)      |
| POST   | /posts/{post_id}/comment/{comment_id}/reply/{reply_id}/reaction               | React on a reply               | Yes(JWT)      |
| PUT    | /posts/{post_id}/reaction/{reaction_id}                                       | Update a reaction on a post    | Yes(JWT)      |
| PUT    | /posts/{post_id}/comment/{comment_id}/reaction/{reaction_id}                  | Update a reaction on a comment | Yes(JWT)      |
| PUT    | /posts/{post_id}/comment/{comment_id}/reply/{reply_id}/reaction/{reaction_id} | Update a reaction on a reply   | Yes(JWT)      |
| DELETE | /posts/{post_id}/reaction/{reaction_id}                                       | Undo a reaction on a post      | Yes(JWT)      |
| DELETE | /posts/{post_id}/comment/{comment_id}/reaction/{reaction_id}                  | Undo a reaction on a comment   | Yes(JWT)      |
| DELETE | /posts/{post_id}/comment/{comment_id}/reply/{reply_id}/reaction/{reaction_id} | Undo a reaction on a reply     | Yes(JWT)      |

## 📄 License

This project is licensed under the MIT License. Feel free to use, modify, and distribute.
