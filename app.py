import os
import requests
from flask import Flask, request, jsonify
from pymongo import MongoClient
import codecs
from chatGpt import getReview

app = Flask(__name__)

# Connect to MongoDB
client = MongoClient(
    'mongodb+srv://batch6:herovired@cluster0.aqifkg2.mongodb.net/')
# Replace 'assignment_review' with your preferred database name
db = client['assignment_review']
students_collection = db['students']


@app.route('/review_assignment', methods=['POST'])
def review_assignment():
    # Get the student's GitHub repository URL and assignment details from the request
    data = request.json
    github_repo_url = data.get('github_repo_url')
    assignment_name = data.get('assignment_name')
    assignment_details = data.get('assignment_details')

    # Extract the student name from the GitHub repository URL
    student_name = extract_student_name(github_repo_url)

    # Create a folder for the student if it doesn't exist
    student_folder = os.path.join('assignments', student_name)
    if not os.path.exists(student_folder):
        os.makedirs(student_folder)

    # Create a folder for the assignment inside the student's folder
    assignment_folder = os.path.join(student_folder, assignment_name)
    os.makedirs(assignment_folder)

    # Download the assignment from the student's GitHub repository
    download_assignment(github_repo_url, assignment_folder)

    # Read the contents of the files in the assignment folder
    file_contents = read_assignment_files(assignment_folder)

    # Get review for the assignment using the assignment data and file contents
    assignment_review = getReview(assignment_details, file_contents)

    # Save the student's GitHub repository URL, assignment name, and file contents in the database
    save_assignment_data(student_name, github_repo_url,
                         assignment_name, assignment_details, file_contents)

    # Construct the response
    response = {
        'message': 'Assignment reviewed successfully',
        'review': assignment_review
    }

    return (assignment_review)


def extract_student_name(github_repo_url):
    # Extract the student name from the GitHub repository URL
    # You can customize this based on the structure of your GitHub repository URLs
    # For example, if the URL is https://github.com/username/repo-name, the student name can be extracted as follows:
    parts = github_repo_url.split('/')
    return parts[-2]


def download_assignment(github_repo_url, destination_folder):
    # Download the assignment from the student's GitHub repository and save it in the destination folder
    # You can use any method or library to download the assignment, such as the `requests` library
    # For example:
    response = requests.get(github_repo_url + '/archive/master.zip')
    zip_path = os.path.join(destination_folder, 'assignment.zip')
    with open(zip_path, 'wb') as file:
        file.write(response.content)

    # Extract the downloaded zip file
    # You can use any method or library to extract the zip file, such as the `zipfile` module
    # For example:
    import zipfile
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(destination_folder)

    # Remove the downloaded zip file
    os.remove(zip_path)


def read_assignment_files(assignment_folder):
    # Read the contents of the files in the assignment folder
    file_contents = {}
    for root, dirs, files in os.walk(assignment_folder):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    file_contents[file_path] = file.read()
            except UnicodeDecodeError:
                print(
                    f"Skipping file '{file_path}' due to unsupported encoding")
    return file_contents


def save_assignment_data(student_name, github_repo_url, assignment_name, assignment_details, file_contents):
    # Save the student's GitHub repository URL, assignment name, assignment details, and file contents in the database
    student = students_collection.find_one({'name': student_name})
    if student:
        # Update the existing student's assignment data
        students_collection.update_one(
            {'_id': student['_id']},
            {'$set': {
                'github_repo_url': github_repo_url,
                'assignments': {
                    assignment_name: {
                        'details': assignment_details,
                        'file_contents': file_contents
                    }
                }
            }}
        )
    else:
        # Insert a new student with their assignment data
        students_collection.insert_one({
            'name': student_name,
            'github_repo_url': github_repo_url,
            'assignments': {
                assignment_name: {
                    'details': assignment_details,
                    'file_contents': file_contents
                }
            }
        })


if __name__ == '__main__':
    app.run(debug=False, port=8500)
