# Realtime Auction Web App

This is a real-time auction web application built with **Flask** and **Socket.IO**, enabling live bidding on items. The app supports an **admin user** who can start/end auctions and **authenticated users** who can place bids. The UI is styled with **Bootstrap 5**, and auction updates are pushed in real-time to all connected clients.

##  Features

- Real-time bidding with live updates using Socket.IO
- Admin control panel to start and end auctions
- Secure login system for users and admin
- Auction countdown timer and bid history
- Auto-scroll to auction results after auction ends
- Simple and clean Bootstrap-based interface

##  Tech Stack

- **Backend**: Python, Flask, Flask-SocketIO
- **Frontend**: HTML, Jinja2 Templates, Bootstrap 5, JavaScript
- **Socket Communication**: Flask-SocketIO

##  Users

- **Admin**
  - Username: `admin`
  - Password: `adminpass`
- **Regular Users** (examples):
  - User ID: `101`, Password: `pass101`
  - User ID: `201`, Password: `pass201`
  - ... up to `701`

(Users are pre-defined in the `app.py` file. In a real-world app, this would be backed by a database.)

##  File Structure

├── app.py                  # Flask backend and routing logic
├── templates/
│   ├── layout.html         # Shared base layout with Bootstrap and Socket.IO
│   ├── login.html          # Login page for users
│   ├── index.html          # Main auction page (extends layout)



##  How to Run

1. **Install dependencies**:
    ```bash
    pip install flask flask-socketio
    ```

2. **Run the app**:
    ```bash
    python app.py
    ```

3. **Visit the app**:
    Open your browser and go to [http://localhost:5001](http://localhost:5001)

## Notes

- This app uses in-memory state (Python dictionaries) for simplicity.
- All auction data is lost when the server restarts.
- No persistent database or password hashing is used—this is intended for demonstration purposes only.

## Future Improvements

- Add persistent storage (e.g., SQLite, PostgreSQL)
- Add user registration and password hashing
- Mobile responsiveness improvements
- Email notifications for winning bids

---
