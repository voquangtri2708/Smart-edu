-- Tạo cơ sở dữ liệu
CREATE DATABASE IF NOT EXISTS sedu;
USE sedu;

-- Tạo bảng student
CREATE TABLE student
(
    id              CHAR(11) PRIMARY KEY, -- Dùng ID làm khóa chính
    identity_number CHAR(12) UNIQUE NOT NULL,
    email           VARCHAR(255) UNIQUE,
    phone_number    CHAR(10) UNIQUE,
    first_name      VARCHAR(255)    NOT NULL,
    last_name       VARCHAR(255)    NOT NULL,
    birthday        DATE            NOT NULL,
    address         VARCHAR(255)    NOT NULL,
    CONSTRAINT check_email_phone_student CHECK (email IS NOT NULL OR phone_number IS NOT NULL)
);

-- Tạo bảng teacher
CREATE TABLE teacher
(
    id              CHAR(11) PRIMARY KEY, -- Dùng ID làm khóa chính
    identity_number CHAR(12) UNIQUE NOT NULL,
    email           VARCHAR(255) UNIQUE,
    phone_number    CHAR(10) UNIQUE,
    first_name      VARCHAR(255)    NOT NULL,
    last_name       VARCHAR(255)    NOT NULL,
    birthday        DATE            NOT NULL,
    address         VARCHAR(255)    NOT NULL,
    CONSTRAINT check_email_phone_teacher CHECK (email IS NOT NULL OR phone_number IS NOT NULL)
);

-- Tạo bảng account (quản lý đăng nhập)
CREATE TABLE account
(
    id           INT PRIMARY KEY AUTO_INCREMENT,
    username     VARCHAR(255) UNIQUE                  NOT NULL,
    email        VARCHAR(255) UNIQUE,
    phone_number VARCHAR(15) UNIQUE,
    password     VARCHAR(255)                         NOT NULL, -- Mật khẩu đã hash (Bcrypt)
    role         ENUM ('admin', 'student', 'teacher') NOT NULL, -- Quyền tài khoản
    student_id   CHAR(11)                             NULL,     -- Chỉ dùng nếu là sinh viên
    teacher_id   CHAR(11)                             NULL,     -- Chỉ dùng nếu là giáo viên
    is_active    TINYINT(1) DEFAULT 1                 NOT NULL, -- 1 = Active, 0 = Inactive
    created_at   TIMESTAMP  DEFAULT CURRENT_TIMESTAMP,
    updated_at   TIMESTAMP  DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    -- Ràng buộc khóa ngoại
    CONSTRAINT fk_account_student FOREIGN KEY (student_id) REFERENCES student (id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_account_teacher FOREIGN KEY (teacher_id) REFERENCES teacher (id) ON DELETE CASCADE ON UPDATE CASCADE
);


-- Tạo bảng subject
CREATE TABLE subject
(
    id          INT PRIMARY KEY AUTO_INCREMENT,
    code        VARCHAR(10) UNIQUE NOT NULL,
    name        VARCHAR(255)       NOT NULL,
    credit      TINYINT UNSIGNED   NOT NULL,
    description TEXT DEFAULT NULL
);
-- Tạo bảng class
CREATE TABLE class
(
    id          CHAR(11) PRIMARY KEY, -- Dùng ID làm khóa chính
    code        CHAR(6) UNIQUE NOT NULL,
    max_student INT            NOT NULL,
    start_date  DATE           NOT NULL,
    end_date    DATE           NOT NULL,
    subject_id  INT            NOT NULL
);

-- Tạo bảng class_student
CREATE TABLE class_student
(
    class_id   CHAR(11),
    student_id CHAR(11),
    PRIMARY KEY (class_id, student_id),
    CONSTRAINT fk_class_student_class FOREIGN KEY (class_id) REFERENCES class (id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_class_student_student FOREIGN KEY (student_id) REFERENCES student (id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE class_teacher
(
    class_id   CHAR(11),
    teacher_id CHAR(11),
    PRIMARY KEY (class_id, teacher_id),
    CONSTRAINT fk_class_teacher_class FOREIGN KEY (class_id) REFERENCES class (id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_class_teacher_teacher FOREIGN KEY (teacher_id) REFERENCES teacher (id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Tạo bảng campus
CREATE TABLE campus
(
    id      INT AUTO_INCREMENT PRIMARY KEY, -- Dùng ID làm khóa chính
    name    VARCHAR(255) UNIQUE NOT NULL,
    address VARCHAR(255)        NOT NULL
);

-- Tạo bảng building
CREATE TABLE building
(
    id        INT AUTO_INCREMENT PRIMARY KEY, -- Dùng ID làm khóa chính
    name      VARCHAR(255) UNIQUE NOT NULL,
    campus_id INT                 NOT NULL,
    CONSTRAINT fk_building_campus FOREIGN KEY (campus_id) REFERENCES campus (id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Tạo bảng classroom
CREATE TABLE classroom
(
    id          INT AUTO_INCREMENT PRIMARY KEY, -- Dùng ID làm khóa chính
    room_number VARCHAR(10) UNIQUE NOT NULL,
    capacity    INT                NOT NULL,
    building_id INT                NOT NULL,
    CONSTRAINT fk_classroom_building FOREIGN KEY (building_id) REFERENCES building (id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Tạo bảng feedback
CREATE TABLE feedback
(
    id         INT AUTO_INCREMENT PRIMARY KEY, -- Dùng ID làm khóa chính
    content    TEXT                                       DEFAULT NULL,
    student_id CHAR(11)                                                       NOT NULL,
    classroom_id INT                                                          NOT NULL,
    teacher_id CHAR(11)                                                       NOT NULL,
    created_at TIMESTAMP                                  DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP                                  DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    sentiment  ENUM ('Tiêu cực', 'Trung lập', 'Tích cực') DEFAULT 'Trung lập' NOT NULL,
    CONSTRAINT fk_feedback_student FOREIGN KEY (student_id) REFERENCES student (id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_feedback_classroom FOREIGN KEY (classroom_id) REFERENCES classroom (id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_feedback_teacher FOREIGN KEY (teacher_id) REFERENCES teacher (id) ON DELETE CASCADE ON UPDATE CASCADE
);