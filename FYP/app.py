import csv
import time
import cv2
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_file, send_from_directory
from flask_cors import CORS
import pandas as pd
from waitress import serve
from Nude.nude_detector import NudeDetector
from Nude.video_detector import VideoDetector
from Foul.mute import Audio
from Blood.blood_class import BlurBlood
import os
import uuid
from moviepy.editor import VideoFileClip
from flask import send_from_directory
import click
import socket

app = Flask(__name__, static_url_path='/static')
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = os.urandom(24)
CORS(app)

# Set the path for storing censored images

app.config['UPLOAD_FOLDER'] = 'uploads\original'
app.config['CENSORED_FOLDER'] = 'uploads\censored'

# update csv
def update_csv(filename, id, colname, data):
    """
    Update a specific column in a CSV file where the first column matches the given ID.
    # Example usage:
    update_csv('example.csv', '123', 'Age', '45')

    Args:
    filename (str): The path to the CSV file.
    id (str): The ID value to search for in the first column.
    colname (str): The column name where the data should be updated.
    data (str): The new data to be inserted into the specified column.

    Returns:
    bool: True if the row was updated, False otherwise.
    """
    updated = False
    rows = []
    try:
        # Read the existing data
        with open(filename, mode='r', newline='') as file:
            reader = csv.DictReader(file)
            fieldnames = reader.fieldnames

            # Check if colname is a valid column
            if colname not in fieldnames:
                raise ValueError(f"Column {colname} does not exist in the file.")

            # Process rows and update as necessary
            for row in reader:
                if row[fieldnames[0]] == id:
                    row[colname] = data
                    updated = True
                rows.append(row)

        # Write the updated data back to the CSV file
        if updated:
            with open(filename, mode='w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)

    except IOError as e:
        print(f"An IOError occurred: {e}")
        return False
    except ValueError as e:
        print(e)
        return False

    return updated

# append data to csv
def append_to_csv(filename, data):
    """
    Append a new row of data to the end of a CSV file.
    # Example usage:
    ['John Doe', '30', 'Engineer']

    Args:
    filename (str): The path to the CSV file.
    data (list): A list of data values to be appended as a new row in the CSV.

    Returns:
    bool: True if the operation is successful, False otherwise.
    """
    try:
        # Open the file in append mode
        with open(filename, mode='a', newline='') as file:
            writer = csv.writer(file)
            # Write the new row of data
            writer.writerow(data)
            return True
    except IOError as e:
        print(f"An IOError occurred: {e}")
        return False

# check login
def check_user_credentials(username, password):
    with open('users.csv', 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['username'] == username and row['password'] == password:
                return row['tier']
        return "none"
    
@app.route('/')
def index():
    return render_template('homepage_nonuser.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        temp = check_user_credentials(username, password)
        if temp != "none":
            session['username'] = username
            session['tier'] = temp
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html')

@app.route('/homepage.html')
def dashboard():
    if 'username' in session:
        return render_template('homepage.html', username=session['username'])
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))


@app.route('/upload_v.html')
def video():
    if 'username' in session:
        return render_template('upload_v.html')
    else:
        flash('Please login to continue', 'danger')
    return redirect(url_for('index'))

@app.route('/upload_a.html')
def audio():
    if 'username' in session:
        return render_template('upload_a.html')
    else:
        flash('Please login to continue', 'danger')
    return redirect(url_for('index'))

@app.route('/upload_p.html')
def photo():
    if 'username' in session:
        return render_template('upload_p.html')
    else:
        flash('Please login to continue', 'danger')
    return redirect(url_for('index'))

@app.route('/blood.html')
def blood():
    if 'username' in session:
        return render_template('blood.html')
    else:
        flash('Please login to continue', 'danger')
    return redirect(url_for('index'))

@app.route('/blur_effect.html')
def test():
    if 'username' in session:
        return render_template('blur_effect.html')
    else:
        flash('Please login to continue', 'danger')
    return redirect(url_for('index'))



@app.route('/report.html', methods=['GET', 'POST'])
def report():
    if request.method == 'POST':
        filedata = request.form['filedata']
        filename = filedata.split(',')[0].strip("'[]' ")
        blurfilename = filedata.split(',')[1].strip("'[]' ")
        blurtype = filedata.split(',')[2].strip("'[]' ")
        filetype = filedata.split(',')[3].strip("'[]' ")
        date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        reason = request.form['reason']
        username = session['username']
        
        append_to_csv('report.csv', [username, filename, blurfilename, blurtype, filetype, reason, date])
        
        return render_template('report.html', success=True)
        
        
    else:
        if session['username'] == 'admin':
            return render_template('report.html', Isadmin = True, reports=read_report_files(), files=read_user_files('admin'))
        elif 'username' in session:
            username = session['username']
            files = read_user_files(username)
            return render_template('report.html' ,files=files)
        else:
            flash('Please login to continue', 'danger')
        return redirect(url_for('index'))
    
def read_report_files():
    # Load the CSV data
    df = pd.read_csv('report.csv')
    return df.to_dict(orient='records')

def read_user_files(username):
    # Load the CSV data
    df = pd.read_csv('userFiles.csv')
    # Filter files based on the user and file types
    filtered_df = df[(df['UserID'] == username) & (df['filetype'].isin(['photo', 'video', 'audio']))]
    return filtered_df.to_dict(orient='records')

@app.route('/uploads/<path:filename>')
def custom_static(filename):
    return send_from_directory('uploads', filename)


@app.route('/blur_effect_nonuser.html')
def test_nonuser():
    return render_template('blur_effect_nonuser.html')

@app.route('/register.html')
def register():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register_help():
    username = request.form['username']
    password = request.form['password']
    print(username, password)
    
    tier = "free"
    data = [username, password, tier]

    success = append_to_csv('users.csv', data)
    if success:
        return "Registration Successful"
    else:
        return "Failed to register", 500



@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),'img/favicon.ico', mimetype='image/vnd.microsoft.icon')

# Define a route to handle image upload and censoring

@app.route('/I_censor', methods=['POST'])
def censor_image():
    # Check if an image file was sent
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400

    image_file = request.files['image']

    # Check if the file is empty
    if image_file.filename == '':
        return jsonify({'error': 'Empty file provided'}), 400

    # Save the image file to a temporary location with a unique filename
    #global unique_filename
    unique_filename = str(uuid.uuid4()) + os.path.splitext(image_file.filename)[1]
    #filename = image_file.filename
    temp_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
    print(temp_path)
    image_file.save(temp_path)
    # file_name, file_extension = os.path.splitext(temp_path)
    # if(file_extension == ""):
    #     os.remove(temp_path)
    #     image_file.save(temp_path+".jpg")
        
    

    # Perform censorship using the nude_detector.censor function
    output_path = os.path.join(app.config['CENSORED_FOLDER'], 'censor_' + unique_filename)

    nude_detector = NudeDetector()
    classes = []
    need_classes = request.form.getlist('classes[]')
    for need_class in need_classes:
        classes.append(need_class)
    
    effect = request.form.get('effect')

    nude_detector.censor(image_path=temp_path, output_path=output_path, classes=classes, mode=effect)
    
    append_to_csv('userFiles.csv', [unique_filename, 'censor_' + unique_filename ,session['username'], 'photo', 'sexy'])


    # Remove the temporary image file
    #os.remove(temp_path)
    
    return unique_filename


# Define a route to serve the censored image

@app.route('/getimage', methods=['GET'])
def get_image():
    Fname = request.values.get('name')
    filename = 'uploads/censored/censor_'+Fname
    return send_file(filename, mimetype='image')

# Define a route to handle video upload and censoring

@app.route('/get_time', methods=['POST'])
def get_time():
    if 'file' not in request.files:
        return "No file found", 400

    video = request.files['file']
    video_path = 'uploaded_video.mp4'  # Path to save the uploaded video

    video.save(video_path)

    try:
        clip = VideoFileClip(video_path)
        duration = clip.duration
        clip.close()
        os.remove(video_path)  # Remove the temporary video file
        return duration
    except Exception as e:
        return f"Error occurred: {str(e)}", 500

@app.route('/V_censor', methods=['POST'])
def censor_video():
    # Check if a video file was sent
    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400

    video_file = request.files['video']

    # Check if the file is empty
    if video_file.filename == '':
        return jsonify({'error': 'Empty file provided'}), 400

    # Save the video file to a temporary location with a unique filename
    # global vname 
    vname = video_file.filename
    unique_filename = str(uuid.uuid4()) + os.path.splitext(vname)[1]
    temp_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
    video_file.save(temp_path)

    # Perform censorship using the nude_detector.censor function
    output_path = os.path.join(app.config['CENSORED_FOLDER'], unique_filename+'_censored.avi')

    nude_detector = VideoDetector()
    classes = []
    need_classes = request.form.getlist('classes[]')
    for need_class in need_classes:
        classes.append(need_class)

    FoulMute = False

    if request.form.get('foul'):
        FoulMute = True
        
    effect = request.form.get('effect')

    nude_detector.censor(video_path=temp_path, v_output_path=output_path, classes=classes, FoulMute=FoulMute, mode=effect)
    
    append_to_csv('userFiles.csv', [unique_filename, unique_filename+'_censored.mp4' ,session['username'], 'video', 'sexy'])

    print(temp_path)
    #os.remove(temp_path)
    
    return unique_filename

@app.route('/getvideo')
def get_video():
    Fname = request.values.get('name')
    filename = 'uploads/censored/'+Fname+'_censored.mp4'
    return send_file(filename, mimetype='video')

@app.route('/A_censor', methods=['POST'])
def censor_audio():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400

    audio_file = request.files['audio']

    
    if audio_file.filename == '':
        return jsonify({'error': 'Empty file provided'}), 400
    
    unique_filename = str(uuid.uuid4()) + os.path.splitext(audio_file.filename)[1]
    temp_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
    audio_file.save(temp_path)

    output_path = os.path.join(app.config['CENSORED_FOLDER'], 'muted_' + unique_filename)

    Audio.mute_audio(temp_path, output_path=output_path)
    
    append_to_csv('userFiles.csv', [unique_filename, 'muted_' + unique_filename ,session['username'], 'audio', 'foul'])

    #os.remove(temp_path)
    return unique_filename

@app.route('/getaudio')
def get_audio():
    Fname = request.values.get('name')
    filename = 'uploads/censored/muted_'+Fname
    return send_file(filename, mimetype='audio')

# Blood

@app.route('/B_censor', methods=['POST'])
def censor_blood():
    # Check if an image file was sent
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400

    image_file = request.files['image']

    # Check if the file is empty
    if image_file.filename == '':
        return jsonify({'error': 'Empty file provided'}), 400

    # Save the image file to a temporary location with a unique filename
    unique_filename = str(uuid.uuid4()) + os.path.splitext(image_file.filename)[1]
    temp_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
    image_file.save(temp_path)

    # Perform censorship using the nude_detector.censor function
    output_path = os.path.join(app.config['CENSORED_FOLDER'], 'blurred_' + unique_filename)

    blur_blood = BlurBlood()
    results = blur_blood.blur_blood_image(temp_path, output_path)

    if results == False:
        return "No blood detected in the image." 

        
    append_to_csv('userFiles.csv', [unique_filename, 'blurred_' + unique_filename ,session['username'], 'photo', 'blood'])


    # Remove the temporary image file
    #os.remove(temp_path)

    return unique_filename

@app.route('/getbimage', methods=['GET'])
def get_bimage():
    Fname = request.values.get('name')
    filename = 'uploads/censored/blurred_'+Fname
    return send_file(filename, mimetype='image')

def get_latest_id(csv_file):
    try:
        with open(csv_file, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            last_row = None
            for row in reader:
                last_row = row
            if last_row:
                return int(last_row[0])
            else:
                return 0
    except FileNotFoundError:
        return 0

@app.route('/addfoul', methods=['GET'])
def addfoul():
    # Get the words from the query parameter
    words = request.args.get('word', None)
    if not words:
        return jsonify({'error': 'No word provided'}), 400

    words = words.split(',')

    # Path to the CSV file
    csv_file = 'Foul/utils/DirtyWords.csv'

    # Get the latest ID
    latest_id = get_latest_id(csv_file)

    added_words = []

    # Process each word
    for word in words:
        word = word.strip().lower()  # Remove any extra spaces
        new_id = latest_id + 1
        latest_id = new_id  # Update latest_id for the next word

        # Prepare the new row to be added
        new_row = [new_id, word, 'en']

        # Write the new row to the CSV file
        with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(new_row)

        added_words.append({'id': new_id, 'word': word, 'language': 'en'})

    return jsonify({'message': 'Words added successfully', 'added_words': added_words}), 200



@app.route('/I_censor4app', methods=['POST'])
def censor_image4app():
    # Check if an image file was sent
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400

    image_file = request.files['image']

    # Check if the file is empty
    if image_file.filename == '':
        return jsonify({'error': 'Empty file provided'}), 400

    # Save the image file to a temporary location with a unique filename
    #global unique_filename

    unique_filename = str(uuid.uuid4()) + os.path.splitext(image_file.filename)[1]
    #filename = image_file.filename
    temp_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
    image_file.save(temp_path)

        
    

    # Perform censorship using the nude_detector.censor function
    output_path = os.path.join(app.config['CENSORED_FOLDER'], 'censor_' + unique_filename)

    nude_detector = NudeDetector()
    classes = []
    need_classes = request.form.getlist('classes[]')
    for need_class in need_classes:
        classes.append(need_class)

    nude_detector.censor(image_path=temp_path, output_path=output_path, classes=classes)


    # Remove the temporary image file

    
    return unique_filename

@app.route('/I_censor4extension', methods=['POST'])
def censor_image4extension():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400

    image_file = request.files['image']
    if image_file.filename == '':
        return jsonify({'error': 'Empty file provided'}), 400

    unique_filename = str(uuid.uuid4()) + os.path.splitext(image_file.filename)[1]
    temp_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
    image_file.save(temp_path)

    output_path = os.path.join(app.config['CENSORED_FOLDER'], 'censor_' + unique_filename)
    classes = []
    need_classes = request.form.getlist('classes[]')
    need_classes = need_classes[0].split(',')
    for need_class in need_classes:
        classes.append(need_class)
    
    #Assuming NudeDetector and censoring logic are properly defined
    nude_detector = NudeDetector()

    nude_detector.censor(image_path=temp_path, output_path=output_path, classes=classes)

    
    return jsonify({'filename': unique_filename})



@app.route('/V_censor4app', methods=['POST'])
def censor_video4app():
    # Check if a video file was sent
    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400

    video_file = request.files['video']

    # Check if the file is empty
    if video_file.filename == '':
        return jsonify({'error': 'Empty file provided'}), 400

    # Save the video file to a temporary location with a unique filename
    vname = video_file.filename
    unique_filename = str(uuid.uuid4()) + os.path.splitext(vname)[1]
    temp_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
    video_file.save(temp_path)

    # Perform censorship using the nude_detector.censor function
    output_path = os.path.join(app.config['CENSORED_FOLDER'], vname+'_censored.avi')

    nude_detector = VideoDetector()
    classes = []
    need_classes = request.form.getlist('classes[]')
    for need_class in need_classes:
        classes.append(need_class)

    FoulMute = False

    if request.form.get('foul'):
        FoulMute = True

    nude_detector.censor(video_path=temp_path, v_output_path=output_path, classes=classes, FoulMute=FoulMute)

    print(temp_path)

    
    return unique_filename


@app.route('/A_censor4app', methods=['POST'])
def censor_audio4app():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400

    audio_file = request.files['audio']

    
    if audio_file.filename == '':
        return jsonify({'error': 'Empty file provided'}), 400
    
    unique_filename = str(uuid.uuid4()) + os.path.splitext(audio_file.filename)[1]
    temp_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
    audio_file.save(temp_path)
    
    output_path = os.path.join(app.config['CENSORED_FOLDER'], 'muted_' + unique_filename)

    Audio.mute_audio(temp_path, output_path=output_path)


    return unique_filename


# Blood

@app.route('/B_censor4app', methods=['POST'])
def censor_blood4app():
    # Check if an image file was sent
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400

    image_file = request.files['image']

    # Check if the file is empty
    if image_file.filename == '':
        return jsonify({'error': 'Empty file provided'}), 400

    # Save the image file to a temporary location with a unique filename
    unique_filename = str(uuid.uuid4()) + os.path.splitext(image_file.filename)[1]
    temp_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
    image_file.save(temp_path)

    # Perform censorship using the nude_detector.censor function
    output_path = os.path.join(app.config['CENSORED_FOLDER'], 'blurred_' + unique_filename)

    blur_blood = BlurBlood()
    results = blur_blood.blur_blood_image(temp_path, output_path)

    if results == False:
        return "No blood detected in the image." 



    return unique_filename










def get_ipv4_addresses():
    ip_list = []
    for ip_info in socket.getaddrinfo(socket.gethostname(), None):
        ip_address = ip_info[4][0]
        # Check if the address is IPv4
        if ip_address.count('.') == 3 and ip_address not in ip_list:
            ip_list.append(f"http://{ip_address}:5000")
    return ip_list

@click.command()
@click.option('--mode', type=click.Choice(['1', '2']), prompt='Select mode (1 for dev or 2 for prod): ')
def runser(mode):
    if mode == '1':
        # Running in development mode
        app.run(host='0.0.0.0', port=5000)
    else:
        # Running in production mode
        print("Running in production mode")
        ip_addresses = get_ipv4_addresses()
        if ip_addresses:
            print("Server IPs:")
            for ip in ip_addresses:
                print(ip)
        else:
            print("No IPv4 addresses found.")
        from waitress import serve
        serve(app, host='0.0.0.0', port=5000, threads=2, url_scheme='https')

if __name__ == '__main__':
    runser()
