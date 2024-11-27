from flask import Flask, request, jsonify, render_template, send_from_directory
from db_manager import get_image_by_id, initialize_db, get_issue
import google.generativeai as genai  # Gemini API 추가
import os
import json

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Gemini API 설정
GOOGLE_API_KEY = "YOUR_GEMINI_API_KEY"  # 실제 키로 교체
genai.configure(api_key=GOOGLE_API_KEY)

generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

# Gemini 모델과 채팅 초기화
model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    generation_config=generation_config,
    system_instruction="당신은 팀 프로젝트 계획을 돕기 위해 설계된 대화형 챗봇입니다. 사용자와 한국어로 대화하며, 필요한 정보를 단계적으로 수집하고 이를 JSON 형식으로 정리합니다.",
)
chat = model.start_chat(history=[])

# 데이터베이스 초기화
initialize_db()

@app.route('/image/<int:image_id>')
def serve_profile_image(image_id):
    file_name = get_image_by_id(image_id)
    if file_name:
        return send_from_directory(app.config['UPLOAD_FOLDER'], file_name)
    else:
        return "이미지를 찾을 수 없습니다", 404

@app.route('/')
def page_index():
    return render_template('index.html')

@app.route('/import_proj')
def page_import_proj():
    issue_list = get_issue()
    for issue in issue_list:
        issue["deadline"] = issue["deadline"]  # 필요시 변환
        issue["status"] = "completed" if issue["is_resolved"] else "in-progress"
    issue_list_json = json.dumps(issue_list, ensure_ascii=False)
    return render_template('import_proj.html', issue=issue_list_json)

@app.route('/test')
def test():
    return render_template('test.html')

@app.route('/new_proj', methods=['GET', 'POST'])
def new_proj():
    if request.method == 'GET':
        state_list = ['completed', '', '', '', '']  # 상태 리스트
        return render_template('new_proj.html', state=state_list)
    elif request.method == 'POST':
        user_message = request.json.get('message')
        if not user_message:
            return jsonify({"error": "Message is required"}), 400

        response = chat.send_message(user_message)
        return jsonify({"response": response.text})

# 프로젝트 데이터를 메모리에 저장
saved_projects = []

@app.route('/save_project', methods=['POST'])
def save_project():
    project_data = request.json
    if not project_data:
        return jsonify({"error": "Invalid data"}), 400
    saved_projects.append(project_data)
    return jsonify({"message": "Project saved successfully!"}), 200

@app.route('/get_saved_project', methods=['GET'])
def get_saved_project():
    if not saved_projects:
        return jsonify({"tasks": []}), 200
    return jsonify(saved_projects[-1]), 200  # 마지막 저장된 프로젝트 반환

tasks = []  # 태스크를 저장할 리스트

@app.route('/add_issue', methods=['GET'])
def add_issue():
    title = request.args.get("title")
    description = request.args.get("description")
    deadline = request.args.get("deadline")
    priority = request.args.get("priority")
    assignee = request.args.get("assignee")

    if not (title and deadline and priority and assignee):
        return jsonify({"error": "Missing required fields"}), 400

    new_issue = {
        "title": title,
        "description": description,
        "deadline": deadline,
        "priority": priority,
        "assignee": assignee,
        "status": "open",
    }

    tasks.append(new_issue)  # 새 태스크 저장
    print("새로운 이슈 추가:", new_issue)
    return jsonify({"message": "Task added successfully"}), 200


if __name__ == '__main__':
    app.run('0.0.0.0', port=1128, debug=True)
