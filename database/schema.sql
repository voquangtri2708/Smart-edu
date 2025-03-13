-- Tạo cơ sở dữ liệu
CREATE DATABASE IF NOT EXISTS sedu_v1;

USE sedu_v1;

-- 1. Bảng student (không phụ thuộc bảng nào)
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

-- 2. Bảng teacher (không phụ thuộc bảng nào)
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
    bio                 TEXT,
    specialization      VARCHAR(255),
    achievements        TEXT,
    teaching_philosophy TEXT
);

-- 3. Bảng account (phụ thuộc student và teacher)
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
    is_active    TINYINT(1) DEFAULT 1                 NOT NULL,
    created_at   TIMESTAMP  DEFAULT CURRENT_TIMESTAMP,
    updated_at   TIMESTAMP  DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_account_student FOREIGN KEY (student_id) REFERENCES student (id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_account_teacher FOREIGN KEY (teacher_id) REFERENCES teacher (id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- 4. Bảng subject (không phụ thuộc bảng nào)
CREATE TABLE subject
(
    id          INT PRIMARY KEY AUTO_INCREMENT,
    code        VARCHAR(10) UNIQUE NOT NULL,
    name        VARCHAR(255)       NOT NULL,
    credit      TINYINT UNSIGNED   NOT NULL,
    description TEXT DEFAULT NULL
);

-- 5. Bảng campus (không phụ thuộc bảng nào)
CREATE TABLE campus
(
    id      INT AUTO_INCREMENT PRIMARY KEY,
    name    VARCHAR(255) UNIQUE NOT NULL,
    address VARCHAR(255)        NOT NULL
);

-- 6. Bảng building (phụ thuộc campus)
CREATE TABLE building
(
    id        INT AUTO_INCREMENT PRIMARY KEY,
    name      VARCHAR(255) UNIQUE NOT NULL,
    campus_id INT                 NOT NULL,
    CONSTRAINT fk_building_campus FOREIGN KEY (campus_id) REFERENCES campus (id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- 7. Bảng classroom (phụ thuộc building)
CREATE TABLE classroom
(
    id          INT AUTO_INCREMENT PRIMARY KEY,
    room_number VARCHAR(10) NOT NULL,
    capacity    INT NOT NULL,
    building_id INT,
    campus_id   INT NOT NULL,
    facilities  TEXT,  -- Mô tả các tiện nghi của phòng
    status      ENUM('available', 'maintenance', 'occupied') DEFAULT 'available',
    CONSTRAINT fk_classroom_building FOREIGN KEY (building_id) REFERENCES building(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_classroom_campus FOREIGN KEY (campus_id) REFERENCES campus(id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- 8. Bảng class (phụ thuộc subject)
CREATE TABLE class
(
    id           INT AUTO_INCREMENT PRIMARY KEY,
    code         CHAR(6)        NOT NULL,
    max_student  INT            NOT NULL,
    start_date   DATE           NOT NULL,
    end_date     DATE           NOT NULL,
    subject_id   INT            NOT NULL,
    subject_code VARCHAR(10)    NOT NULL,
    status       ENUM('pending', 'ongoing', 'completed', 'cancelled') DEFAULT 'pending',
    CONSTRAINT fk_class_subject_id FOREIGN KEY (subject_id) REFERENCES subject (id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_class_subject_code FOREIGN KEY (subject_code) REFERENCES subject (code) ON DELETE CASCADE ON UPDATE CASCADE
);

-- 9. Bảng class_schedule (phụ thuộc class và classroom)
CREATE TABLE class_schedule
(
    id          INT PRIMARY KEY AUTO_INCREMENT,
    class_id    INT NOT NULL,
    classroom_id INT NOT NULL,
    day_of_week ENUM('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday') NOT NULL,
    start_time  TIME NOT NULL,
    end_time    TIME NOT NULL,
    CONSTRAINT fk_schedule_class FOREIGN KEY (class_id) REFERENCES class (id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_schedule_classroom FOREIGN KEY (classroom_id) REFERENCES classroom (id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- 10. Bảng class_student (liên kết student với class)
CREATE TABLE class_student
(
    class_id   INT,
    student_id CHAR(11),
    PRIMARY KEY (class_id, student_id),
    CONSTRAINT fk_class_student_class FOREIGN KEY (class_id) REFERENCES class (id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_class_student_student FOREIGN KEY (student_id) REFERENCES student (id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- 11. Bảng class_teacher (liên kết teacher với class)
CREATE TABLE class_teacher
(
    class_id   INT,
    teacher_id CHAR(11),
    PRIMARY KEY (class_id, teacher_id),
    CONSTRAINT fk_class_teacher_class FOREIGN KEY (class_id) REFERENCES class (id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_class_teacher_teacher FOREIGN KEY (teacher_id) REFERENCES teacher (id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- 12. Bảng teacher_availability (phụ thuộc teacher)
CREATE TABLE teacher_availability
(
    id              INT AUTO_INCREMENT PRIMARY KEY,
    teacher_id      CHAR(11) NOT NULL,
    day_of_week     ENUM('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday') NOT NULL,
    start_time      TIME NOT NULL,
    end_time        TIME NOT NULL,
    is_available    BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_availability_teacher FOREIGN KEY (teacher_id) REFERENCES teacher (id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- 13. Bảng grade_type (không phụ thuộc bảng nào)
CREATE TABLE grade_type
(
    id          INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(255) NOT NULL,
    description TEXT,
    weight      DECIMAL(3,2) NOT NULL CHECK (weight > 0 AND weight <= 1)
);

-- 14. Bảng registration_period (không phụ thuộc bảng nào)
CREATE TABLE registration_period
(
    id              INT AUTO_INCREMENT PRIMARY KEY,
    semester        VARCHAR(20) NOT NULL,
    academic_year   VARCHAR(10) NOT NULL,
    start_date      DATETIME NOT NULL,
    end_date        DATETIME NOT NULL,
    type            ENUM('normal', 'additional') DEFAULT 'normal',
    status          ENUM('pending', 'active', 'closed') DEFAULT 'pending',
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT unique_period UNIQUE (semester, academic_year, type)
);

-- 15. Bảng class_registration (phụ thuộc student, class, teacher, registration_period)
CREATE TABLE class_registration
(
    id              INT AUTO_INCREMENT PRIMARY KEY,
    student_id      CHAR(11) NOT NULL,
    class_id        INT NOT NULL,
    status          ENUM('pending', 'approved', 'rejected', 'cancelled') DEFAULT 'pending',
    registered_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    approved_at     TIMESTAMP NULL,
    approved_by     CHAR(11),
    registration_period_id INT,
    CONSTRAINT fk_registration_student FOREIGN KEY (student_id) REFERENCES student (id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_registration_class FOREIGN KEY (class_id) REFERENCES class (id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_registration_teacher FOREIGN KEY (approved_by) REFERENCES teacher (id) ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_registration_period FOREIGN KEY (registration_period_id) REFERENCES registration_period(id) ON DELETE SET NULL ON UPDATE CASCADE
);

-- 16 Bảng class_feedback (phụ thuộc class_student)
CREATE TABLE teacher_feedback (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    content      TEXT DEFAULT NULL,
    student_id   CHAR(11) NOT NULL,
    class_id     INT NOT NULL,
    teacher_id   CHAR(11) NOT NULL,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    start_date   DATE,
    end_date     DATE,
    sentiment    ENUM ('negative', 'neutral', 'positive') DEFAULT 'neutral' NOT NULL,
    CONSTRAINT fk_teacher_feedback_student FOREIGN KEY (student_id, class_id) REFERENCES class_student (student_id, class_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_teacher_feedback_teacher FOREIGN KEY (teacher_id, class_id) REFERENCES class_teacher (teacher_id, class_id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- 17. Bảng classroom_feedback (phụ thuộc class_student và classroom)
CREATE TABLE classroom_feedback (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    content      TEXT DEFAULT NULL,
    student_id   CHAR(11) NOT NULL,
    class_id     INT NOT NULL,
    classroom_id INT NOT NULL,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    start_date   DATE,
    end_date     DATE,
    sentiment    ENUM ('negative', 'neutral', 'positive') DEFAULT 'neutral' NOT NULL,
    CONSTRAINT fk_room_feedback_student FOREIGN KEY (student_id, class_id) REFERENCES class_student (student_id, class_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_room_feedback_classroom FOREIGN KEY (classroom_id) REFERENCES classroom (id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- 18. Bảng grade (phụ thuộc class_student và grade_type)
CREATE TABLE grade
(
    id           INT AUTO_INCREMENT PRIMARY KEY,
    student_id   CHAR(11) NOT NULL,
    class_id     INT NOT NULL,
    grade_type_id INT NOT NULL,
    score        DECIMAL(4,2) CHECK (score >= 0 AND score <= 10),
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_grade_student FOREIGN KEY (student_id, class_id) REFERENCES class_student (student_id, class_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_grade_type FOREIGN KEY (grade_type_id) REFERENCES grade_type (id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- 19. Bảng attendance (phụ thuộc class_student và class_schedule)
CREATE TABLE attendance
(
    id              INT AUTO_INCREMENT PRIMARY KEY,
    class_id        INT NOT NULL,
    student_id      CHAR(11) NOT NULL,
    schedule_id     INT NOT NULL,
    status          ENUM('present', 'absent', 'late') NOT NULL,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_attendance_student FOREIGN KEY (student_id, class_id) REFERENCES class_student (student_id, class_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_attendance_schedule FOREIGN KEY (schedule_id) REFERENCES class_schedule (id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- 20. Bảng notification (phụ thuộc account)
CREATE TABLE notification
(
    id          INT AUTO_INCREMENT PRIMARY KEY,
    title       VARCHAR(255) NOT NULL,
    content     TEXT NOT NULL,
    type        ENUM('system', 'class', 'grade', 'attendance', 'announcement') NOT NULL,
    priority    ENUM('low', 'medium', 'high') DEFAULT 'medium',
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at  TIMESTAMP NULL,
    is_read     BOOLEAN DEFAULT FALSE,
    recipient_id INT NOT NULL,
    recipient_role ENUM('admin', 'student', 'teacher') NOT NULL,
    CONSTRAINT fk_notification_account FOREIGN KEY (recipient_id) REFERENCES account (id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- 21. Bảng class_material (phụ thuộc class và teacher)
CREATE TABLE class_material
(
    id          INT AUTO_INCREMENT PRIMARY KEY,
    class_id    INT NOT NULL,
    title       VARCHAR(255) NOT NULL,
    description TEXT,
    file_path   VARCHAR(255) NOT NULL,
    file_type   VARCHAR(50) NOT NULL,
    file_size   BIGINT NOT NULL,
    uploaded_by CHAR(11) NOT NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_material_class FOREIGN KEY (class_id) REFERENCES class (id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_material_teacher FOREIGN KEY (uploaded_by) REFERENCES teacher (id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- 22. Bảng class_announcement (phụ thuộc class và teacher)
CREATE TABLE class_announcement
(
    id          INT AUTO_INCREMENT PRIMARY KEY,
    class_id    INT NOT NULL,
    title       VARCHAR(255) NOT NULL,
    content     TEXT NOT NULL,
    created_by  CHAR(11) NOT NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_pinned   BOOLEAN DEFAULT FALSE,
    CONSTRAINT fk_announcement_class FOREIGN KEY (class_id) REFERENCES class (id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_announcement_teacher FOREIGN KEY (created_by) REFERENCES teacher (id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- 23. Bảng student_leave_request (phụ thuộc class_student, class_schedule và teacher)
CREATE TABLE student_leave_request
(
    id              INT AUTO_INCREMENT PRIMARY KEY,
    student_id      CHAR(11) NOT NULL,
    class_id        INT NOT NULL,
    schedule_id     INT NOT NULL,
    reason          TEXT NOT NULL,
    status          ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    approved_by     CHAR(11),
    CONSTRAINT fk_leave_student FOREIGN KEY (student_id, class_id) REFERENCES class_student (student_id, class_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_leave_schedule FOREIGN KEY (schedule_id) REFERENCES class_schedule (id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_leave_teacher FOREIGN KEY (approved_by) REFERENCES teacher (id) ON DELETE SET NULL ON UPDATE CASCADE
);

-- 24. Bảng class_prerequisite (phụ thuộc class và subject)
CREATE TABLE class_prerequisite
(
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    class_id            INT NOT NULL,
    prerequisite_id     INT NOT NULL,
    is_required         BOOLEAN DEFAULT TRUE,
    CONSTRAINT fk_prerequisite_class FOREIGN KEY (class_id) REFERENCES class (id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_prerequisite_subject FOREIGN KEY (prerequisite_id) REFERENCES subject (id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- 25. Bảng student_subject_history (phụ thuộc student và subject)
CREATE TABLE student_subject_history
(
    id              INT AUTO_INCREMENT PRIMARY KEY,
    student_id      CHAR(11) NOT NULL,
    subject_id      INT NOT NULL,
    status          ENUM('passed', 'failed', 'in_progress') NOT NULL,
    completed_at    TIMESTAMP NULL,
    final_grade     DECIMAL(4,2) CHECK (final_grade >= 0 AND final_grade <= 10),
    CONSTRAINT fk_history_student FOREIGN KEY (student_id) REFERENCES student (id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_history_subject FOREIGN KEY (subject_id) REFERENCES subject (id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- 26. Bảng registration_rule (không phụ thuộc bảng nào)
CREATE TABLE registration_rule
(
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    name                VARCHAR(255) NOT NULL,
    description         TEXT,
    min_credits         INT DEFAULT 0,
    max_credits         INT DEFAULT 30,
    min_courses         INT DEFAULT 0,
    max_courses         INT DEFAULT 10,
    allow_time_conflict BOOLEAN DEFAULT FALSE,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);