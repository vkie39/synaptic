import sqlite3

DB_PATH = 'data.db'

# 데이터베이스 초기화 (테이블 생성)
def initialize_db():
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()


    # 기존 테이블 삭제 (필요한 경우)
    cursor.execute('DROP TABLE IF EXISTS images')
    cursor.execute('DROP TABLE IF EXISTS user_data')
    cursor.execute('DROP TABLE IF EXISTS project_issues')
    cursor.execute('DROP TABLE IF EXISTS managing_issues')

    # images 테이블 생성
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Auto Increment ID
            file_name TEXT NOT NULL,                -- 파일 이름
            sample INTEGER                              -- 샘플
        )
    ''')

    # user_data 테이블 생성
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_data (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,  -- User ID (Primary Key)
            user_name TEXT NOT NULL,                    -- 사용자 이름
            email TEXT NOT NULL,                        -- 이메일
            password TEXT NOT NULL,                     -- 암호
            role TEXT NOT NULL,                          -- 역할
            sample INTEGER                              -- 샘플
        )
    ''')

    # project_issues 테이블 생성
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS project_issues (
            issue_id INTEGER PRIMARY KEY AUTOINCREMENT, -- Issue ID (Primary Key)
            issue_list TEXT NOT NULL,                   -- 이슈 목록 (String)
            issue_date TEXT NOT NULL,                   -- 날짜
            is_resolved BOOLEAN NOT NULL,                -- 해결 여부 (True/False)
            member_name TEXT,                           -- 이슈 발생한 팀원 이름 (String)
            priority TEXT,                              -- 중요도
            sample INTEGER                              -- 샘플
        )
    ''')

    # managing_issues 테이블 생성
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS managing_issues (
            id INTEGER PRIMARY KEY AUTOINCREMENT,       -- Auto Increment ID
            user_id INTEGER NOT NULL,                   -- 외래키 (user_data 테이블의 PK)
            issue_id INTEGER NOT NULL,                  -- 외래키 (project_issues 테이블의 PK)
            sample INTEGER,                              -- 샘플
            FOREIGN KEY (user_id) REFERENCES user_data(user_id),
            FOREIGN KEY (issue_id) REFERENCES project_issues(issue_id)
        )
    ''')

    # 샘플 데이터 삽입
    # images 테이블에 샘플 데이터 삽입
    cursor.execute('INSERT INTO images (file_name) VALUES (?)', ('1.png',))

    # user_data 테이블에 샘플 데이터 삽입
    cursor.execute('''
                   INSERT INTO user_data (user_name, email, password, role) 
                   VALUES (?, ?, ?, ?)
                   ''', ('SampleUser', 'sampleuser@example.com', 'password123', 'user'))
    user_id = cursor.lastrowid  # 삽입된 user_id 가져오기

    # project_issues 테이블에 샘플 데이터 삽입
    cursor.execute('''
        INSERT INTO project_issues (issue_list, issue_date, is_resolved, member_name, priority)
        VALUES (?, ?, ?, ?, ?)
    ''', ('Issue1, Issue2', '2024-11-25', False, '최서현', 'Low Priority'))
    issue_id = cursor.lastrowid  # 삽입된 issue_id 가져오기

    # managing_issues 테이블에 샘플 데이터 삽입
    cursor.execute('''
        INSERT INTO managing_issues (user_id, issue_id)
        VALUES (?, ?)
    ''', (user_id, issue_id))

    # 커밋 및 연결 종료
    connection.commit()
    connection.close()

# ID로 이미지 파일명 가져오기
def get_image_by_id(image_id):
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    cursor.execute('SELECT file_name FROM images WHERE id = ?', (image_id,))
    result = cursor.fetchone()
    connection.close()
    return result[0] if result else None

'''
def get_issue():
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM project_issues')
    result = cursor.fetchall()
    connection.close()
    return result if result else None
'''


def get_issue():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute('SELECT issue_id, issue_list AS title, issue_date AS deadline, priority, is_resolved FROM project_issues')
    result = cursor.fetchall()
    connection.close()
    return [dict(row) for row in result] if result else []

#deadline 만들기 캘린더에 보여지려면 deadline도 있어야 함, 이를 위한 테이블 구조 수정

def update_project_issues_table():
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    
    # deadline 열이 이미 존재하는지 확인
    cursor.execute("PRAGMA table_info(project_issues)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'deadline' not in columns:
        # deadline 열 추가
        cursor.execute('ALTER TABLE project_issues ADD COLUMN deadline TEXT')
        # 기존 issue_date 값을 deadline으로 복사
        cursor.execute('UPDATE project_issues SET deadline = issue_date')
        print("Column 'deadline' added and populated successfully.")
    else:
        print("Column 'deadline' already exists.")


#import_project에서 이슈 받아오기
def add_project_issue(issue_list, issue_date, is_resolved, member_name, priority):
    """
    project_issues 테이블에 새 이슈를 추가합니다.
    """
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    cursor.execute('''
        INSERT INTO project_issues (issue_list, issue_date, is_resolved, member_name, priority)
        VALUES (?, ?, ?, ?, ?)
    ''', (issue_list, issue_date, is_resolved, member_name, priority))
    connection.commit()
    connection.close()

initialize_db()