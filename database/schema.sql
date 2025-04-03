-- Tạo cơ sở dữ liệu
CREATE DATABASE IF NOT EXISTS smartedu;

USE smartedu;

-- 1. Bảng student
CREATE TABLE student
(
    id              CHAR(11) PRIMARY KEY,
    identity_number CHAR(12) UNIQUE NOT NULL,
    email           VARCHAR(255) UNIQUE,
    phone_number    CHAR(10) UNIQUE,
    first_name      VARCHAR(255)    NOT NULL,
    last_name       VARCHAR(255)    NOT NULL,
    birthday        DATE            NOT NULL,
    address         VARCHAR(255)    NOT NULL,
    avatar_url      VARCHAR(255)    DEFAULT NULL
);

-- 2. Bảng teacher
CREATE TABLE teacher
(
    id                  CHAR(11) PRIMARY KEY,
    identity_number     CHAR(12) UNIQUE NOT NULL,
    email               VARCHAR(255) UNIQUE,
    phone_number        CHAR(10) UNIQUE,
    first_name          VARCHAR(255)    NOT NULL,
    last_name           VARCHAR(255)    NOT NULL,
    birthday            DATE            NOT NULL,
    address             VARCHAR(255)    NOT NULL,
    avatar_url          VARCHAR(255)    DEFAULT NULL,
    bio                 TEXT
);

-- 3. Bảng subject
CREATE TABLE subject
(
    id INT PRIMARY KEY AUTO_INCREMENT,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) UNIQUE NOT NULL,
    credit INT NOT NULL,
    description TEXT
);

-- 4. Bảng Campus
CREATE TABLE campus
(
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) UNIQUE NOT NULL,
    address VARCHAR(255) NOT NULL
);

-- 5. Bảng Grade Type
CREATE TABLE grade_type
(
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) UNIQUE NOT NULL,
    weight FLOAT NOT NULL,
    description TEXT
);

-- 6. Bảng account
CREATE TABLE account
(
    id           INT PRIMARY KEY AUTO_INCREMENT,
    username     VARCHAR(255) UNIQUE                  NOT NULL,
    email        VARCHAR(255) UNIQUE,
    phone_number VARCHAR(15) UNIQUE,
    password     VARCHAR(255)                         NOT NULL,
    role         ENUM ('admin', 'student', 'teacher') NOT NULL,
    student_id   CHAR(11),
    teacher_id   CHAR(11),
    is_active    BOOLEAN DEFAULT TRUE                 NOT NULL,
    created_at   TIMESTAMP  DEFAULT CURRENT_TIMESTAMP,
    updated_at   TIMESTAMP  DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_account_student FOREIGN KEY (student_id) REFERENCES student (id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_account_teacher FOREIGN KEY (teacher_id) REFERENCES teacher (id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- 7. Bảng class
CREATE TABLE class
(
    id INT PRIMARY KEY AUTO_INCREMENT,
    code VARCHAR(50) UNIQUE NOT NULL,
    max_student INT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    subject_id INT,
    CONSTRAINT fk_class_subject FOREIGN KEY (subject_id) REFERENCES subject (id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- 8. Bảng Building
CREATE TABLE building
(
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) UNIQUE NOT NULL,
    campus_id INT,
    CONSTRAINT fk_building_campus FOREIGN KEY (campus_id) REFERENCES campus (id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- 9. Bảng Classroom
CREATE TABLE classroom
(
    id INT PRIMARY KEY AUTO_INCREMENT,
    room_number VARCHAR(50) UNIQUE NOT NULL,
    capacity INT NOT NULL,
    facilities TEXT,
    building_id INT,
    CONSTRAINT fk_classroom_building FOREIGN KEY (building_id) REFERENCES building (id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- 10. Bảng class_student
CREATE TABLE class_student
(
    class_id INT,
    student_id CHAR(11),
    PRIMARY KEY (class_id, student_id),
    CONSTRAINT fk_class_student_class FOREIGN KEY (class_id) REFERENCES class (id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_class_student_student FOREIGN KEY (student_id) REFERENCES student (id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- 11. Bảng class_teacher
CREATE TABLE class_teacher
(
    class_id INT,
    teacher_id CHAR(11),
    PRIMARY KEY (class_id, teacher_id),
    CONSTRAINT fk_class_teacher_class FOREIGN KEY (class_id) REFERENCES class (id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_class_teacher_teacher FOREIGN KEY (teacher_id) REFERENCES teacher (id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- 12. Bảng Schedule
CREATE TABLE schedule
(
    id INT PRIMARY KEY AUTO_INCREMENT,
    class_id INT,
    classroom_id INT,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    day_of_week ENUM ('MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN') NOT NULL,
    specific_date DATE,
    CONSTRAINT fk_schedule_class FOREIGN KEY (class_id) REFERENCES class (id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_schedule_classroom FOREIGN KEY (classroom_id) REFERENCES classroom (id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- 13. Bảng Grade
CREATE TABLE grade
(
    id INT PRIMARY KEY AUTO_INCREMENT,
    student_id CHAR(11),
    class_id INT,
    score FLOAT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    grade_type_id INT,
    CONSTRAINT fk_grade_student FOREIGN KEY (student_id) REFERENCES student (id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_grade_grade_type FOREIGN KEY (grade_type_id) REFERENCES grade_type (id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_grade_class FOREIGN KEY (class_id) REFERENCES class (id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT check_score_range CHECK (score >= 0 AND score <= 10)
);

-- 14. Bảng Notification
CREATE TABLE notification
(
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    type ENUM ('INFO', 'WARNING', 'ERROR') NOT NULL,
    priority ENUM ('LOW', 'MEDIUM', 'HIGH') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_read BOOLEAN DEFAULT FALSE NOT NULL,
    account_id INT,
    CONSTRAINT fk_notification_account FOREIGN KEY (account_id) REFERENCES account (id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- 15. Bảng Feedbacks
CREATE TABLE feedbacks
(
    id INT PRIMARY KEY AUTO_INCREMENT,
    content TEXT NOT NULL,
    student_id CHAR(11),
    teacher_id CHAR(11),
    classroom_id INT,
    class_id INT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    sentiment ENUM ('POSITIVE', 'NEUTRAL', 'NEGATIVE') NOT NULL,
    feedback_type ENUM ('CLASSROOM', 'TEACHER') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_feedbacks_student FOREIGN KEY (student_id) REFERENCES student (id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_feedbacks_teacher FOREIGN KEY (teacher_id) REFERENCES teacher (id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_feedbacks_classroom FOREIGN KEY (classroom_id) REFERENCES classroom (id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_feedbacks_class FOREIGN KEY (class_id) REFERENCES class (id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- 16. Bảng Exam (Kỳ kiểm tra)
CREATE TABLE exam
(
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    exam_date DATE NOT NULL,
    duration_minutes INT NOT NULL,
    class_id INT NOT NULL,
    grade_type_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_exam_class FOREIGN KEY (class_id) REFERENCES class (id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_exam_grade_type FOREIGN KEY (grade_type_id) REFERENCES grade_type (id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- 17. Bảng Exam Question (Đề thi)
CREATE TABLE exam_question
(
    id INT PRIMARY KEY AUTO_INCREMENT,
    exam_id INT NOT NULL,
    question_text TEXT NOT NULL,
    answer_options TEXT,
    correct_answer TEXT,
    points FLOAT NOT NULL,
    question_type ENUM('MULTIPLE_CHOICE', 'TRUE_FALSE', 'ESSAY', 'SHORT_ANSWER') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_exam_question_exam FOREIGN KEY (exam_id) REFERENCES exam (id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Thêm gender vào bảng student và teacher
ALTER TABLE 
    student ADD COLUMN gender ENUM('MALE', 'FEMALE') NOT NULL;

ALTER TABLE 
    teacher ADD COLUMN gender ENUM('MALE', 'FEMALE') NOT NULL;

-- Modify Grade table to reference exams
ALTER TABLE grade
    ADD COLUMN exam_id INT AFTER class_id,
    ADD CONSTRAINT fk_grade_exam FOREIGN KEY (exam_id) REFERENCES exam (id) ON DELETE CASCADE ON UPDATE CASCADE;