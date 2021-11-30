DROP TABLE if exists Appointments;
DROP TABLE if exists Faculty;
DROP TABLE if exists Student;
DROP TABLE if exists Admin;
DROP TABLE if exists Departments;
DROP TABLE if exists Users;

CREATE TABLE Users (
  u_id serial primary key,
  uname text not null,
  email text not null,
  pwd text not null,
  mobileno text not null
);

CREATE TABLE Departments (
	department_id serial primary key,
  dname text not null
);

CREATE TABLE Admin (
	admin_id serial references Users(u_id)
);

CREATE TABLE Faculty (
	ssn serial references Users(u_id) PRIMARY KEY,
  deptid serial references Departments(department_id)
);

CREATE TABLE Student (
	roll_no serial references Users(u_id) PRIMARY KEY, /* so this rollnumber is not your college rollnumber 
  																				this is one that our database gives you */
  deptid serial references Departments(department_id)
);

CREATE TABLE Appointments(
	appointment_id serial primary key,
  status text,
	date_created text,
  date_scheduled text,
  title text,
	decription text,
  stu_id serial references Student(roll_no),
	fac_id serial references Faculty(ssn),
	suggested_date text DEFAULT '-1',/*default -1 : */
	faculty_message text 
);

/*----------------------------INSERT STUFF------------------------------------------------*/
INSERT INTO Users(uname, email, pwd, mobileno) values ('ftp101','ftp@gmail.com','pwd', '1234567890');
INSERT INTO Departments(dname) values ('ECE');
INSERT INTO Student(roll_no, deptid) values ('3','1');
select * from admin;
select * from users;
select * from student;
select * from faculty;

insert into  Appointments(
  status,
	date_created,
  date_scheduled,
  title,
	decription,
  stu_id,
	fac_id
)
values (
'test', '27-november-2021', '29-november-2021', '<insert-title>', '<insert-decription>', '3', '6'
);




