# app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_socketio import SocketIO, emit
import os
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
socketio = SocketIO(app)

# User database - In a real app, use a proper database
users = {
    "101": {"password": "pass101", "name": "Friend 1"},
    "201": {"password": "pass201", "name": "Friend 2"},
    "301": {"password": "pass301", "name": "Friend 3"},
    "401": {"password": "pass401", "name": "Friend 4"},
    "501": {"password": "pass501", "name": "Friend 5"},
    "601": {"password": "pass601", "name": "Friend 6"},
    "701": {"password": "pass701", "name": "Friend 7"}
}

# Auction state
auction_state = {
    "active": False,
    "item_name": "No item",
    "starting_bid": 0,
    "current_bid": 0,
    "highest_bidder": None,
    "highest_bidder_name": None,
    "end_time": None,
    "bid_history": []  # Will store bid history as [{time, user_id, user_name, amount}]
}

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    is_admin = session.get('is_admin', False)
    return render_template('index.html', auction=auction_state, is_admin=is_admin)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        password = request.form.get('password')
        
        # Special admin user for the host (you can customize this)
        if user_id == 'admin' and password == 'adminpass':
            session['user_id'] = 'admin'
            session['name'] = 'Admin'
            session['is_admin'] = True
            flash('Logged in as Admin')
            return redirect(url_for('index'))
        
        if user_id in users and users[user_id]['password'] == password:
            session['user_id'] = user_id
            session['name'] = users[user_id]['name']
            session['is_admin'] = False
            flash(f'Logged in as {users[user_id]["name"]}')
            return redirect(url_for('index'))
        
        flash('Invalid credentials')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/start_auction', methods=['POST'])
def start_auction():
    if session.get('is_admin', False):
        item_name = request.form.get('item_name')
        starting_bid = float(request.form.get('starting_bid'))
        duration = int(request.form.get('duration'))  # Duration in minutes
        
        auction_state['active'] = True
        auction_state['item_name'] = item_name
        auction_state['starting_bid'] = starting_bid
        auction_state['current_bid'] = starting_bid
        auction_state['highest_bidder'] = None
        auction_state['highest_bidder_name'] = None
        auction_state['end_time'] = datetime.now().timestamp() + duration * 60
        auction_state['bid_history'] = []  # Clear bid history for new auction
        
        # Add initial bid as system bid
        timestamp = datetime.now().strftime("%H:%M:%S")
        auction_state['bid_history'].append({
            'time': timestamp,
            'user_id': 'system',
            'user_name': 'System',
            'amount': starting_bid
        })
        
        socketio.emit('auction_update', auction_state)
        
    return redirect(url_for('index'))

@app.route('/end_auction')
def end_auction():
    if session.get('is_admin', False):
        auction_state['active'] = False
        
        # Create a comprehensive end-of-auction notification
        end_data = {
            'item_name': auction_state['item_name'],
            'final_bid': auction_state['current_bid'],
            'winner': auction_state['highest_bidder_name'] or 'No winner',
            'bid_history': auction_state['bid_history'],
            'total_bids': len(auction_state['bid_history']) - 1,  # Subtract the initial system bid
            'auction_duration': get_auction_duration()
        }
        
        # Emit the auction ended event to all connected clients
        socketio.emit('auction_ended', end_data)
        
    return redirect(url_for('index'))

# Helper function to calculate auction duration
def get_auction_duration():
    if not auction_state['bid_history'] or len(auction_state['bid_history']) < 2:
        return "N/A"
    
    start_time = auction_state['bid_history'][0]['time']
    last_time = auction_state['bid_history'][-1]['time']
    
    # Convert from string format to datetime objects
    start_dt = datetime.strptime(start_time, "%H:%M:%S")
    end_dt = datetime.strptime(last_time, "%H:%M:%S")
    
    # Calculate duration
    delta = end_dt - start_dt
    minutes, seconds = divmod(delta.seconds, 60)
    return f"{minutes}m {seconds}s"

@app.route('/place_bid', methods=['POST'])
def place_bid():
    if 'user_id' in session and not session.get('is_admin', False) and auction_state['active']:
        bid_amount = float(request.form.get('bid_amount'))
        
        if bid_amount > auction_state['current_bid']:
            auction_state['current_bid'] = bid_amount
            auction_state['highest_bidder'] = session['user_id']
            auction_state['highest_bidder_name'] = session['name']
            
            # Add to bid history
            timestamp = datetime.now().strftime("%H:%M:%S")
            auction_state['bid_history'].append({
                'time': timestamp,
                'user_id': session['user_id'],
                'user_name': session['name'],
                'amount': bid_amount
            })
            
            socketio.emit('auction_update', auction_state)
            flash('Your bid has been placed!')
        else:
            flash('Your bid must be higher than the current bid')
    
    return redirect(url_for('index'))

@socketio.on('connect')
def handle_connect():
    emit('auction_update', auction_state)

if __name__ == '__main__':
    # Use a different port (5001) to avoid conflicts
    port = 5001
    socketio.run(app, debug=True, host='0.0.0.0', port=port)