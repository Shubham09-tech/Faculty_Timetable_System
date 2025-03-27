from django.db import models  

class Section(models.Model):
    name = models.CharField(max_length=50)  # Example: A, B, C

    def __str__(self):
        return self.name

class Semester(models.Model):
    number = models.IntegerField()  # Example: 1 to 8

    def __str__(self):
        return f"Semester {self.number}"
    
class Branch(models.Model):
    name = models.CharField(max_length=100)  # Example: Mechanical, Electrical, etc.

    def __str__(self):
        return self.name

class Teacher(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Subject(models.Model):
    STUDENTS_TYPE_CHOICES = [
        ('boys', 'Only Boys'),
        ('girls', 'Only Girls'),
        ('combine', 'Combine'),
    ]

    CLASS_TYPE_CHOICES = [
        ('theory', 'Theory'),
        ('practical', 'Practical'),
    ]

    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, null=True)  # Subject Code
    section = models.ForeignKey(Section, on_delete=models.CASCADE, null=True, blank=True)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, null=True, blank=True)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    teacher = models.ManyToManyField(Teacher, blank=True)  # Changed "teachers" to "teacher"
    no_of_classes = models.IntegerField(null=True)  # Total number of classes per week
    hours = models.IntegerField(default=1)  # Duration of each class in hours
    students_in_class = models.CharField(
        max_length=10, 
        choices=STUDENTS_TYPE_CHOICES, 
        default='combine'
    )
    Type_of_class = models.CharField(
        max_length=10, 
        choices=CLASS_TYPE_CHOICES, 
        default='Theory'
    )

    def __str__(self):
       return f"{self.name} ({self.code})"


class Faculty (models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name
    
class Class_Room(models.Model):
    name = models.CharField(max_length=100)
    Faculty_name = models.ForeignKey(Faculty, on_delete=models.CASCADE, null= True, blank=True)

    def __str__(self):
        return f"{self.name}-{self.Faculty_name}"
    

class Timetable(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, null=True, blank=True)
    section = models.ForeignKey(Section, on_delete=models.CASCADE, null=True, blank=True)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    day = models.CharField(max_length=20)  # E.g., 'Monday', 'Tuesday'
    time_slot = models.CharField(max_length=20)  # E.g., '7:00', '7:55'
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, null=True, blank=True)
    room = models.ForeignKey(Class_Room, on_delete=models.CASCADE, null=True, blank=True)
    teacher = models.ManyToManyField(Teacher, blank=True)  # Changed "teachers" to "teacher"

    def __str__(self):
        teacher_names = ", ".join([teacher.name for teacher in self.teacher.all()])
        return f"{self.day} {self.time_slot} - {self.subject} ({self.branch or self.section})"





































# from django.db import models 


    
# class Section(models.Model):
#     name = models.CharField(max_length=50)  # Example: A, B, C

#     def __str__(self):
#         return self.name

# class Semester(models.Model):
#     number = models.IntegerField()  # Example: 1 to 8

#     def __str__(self):
#         return f"Semester {self.number}"
    
# class Branch(models.Model):
#     name = models.CharField(max_length=100)  # Example: Mechanical, Electrical, etc.

#     def __str__(self):
#         return self.name

# class Teacher(models.Model):
#     name = models.CharField(max_length=100)

#     def __str__(self):
#         return self.name

# class Subject(models.Model):
#     STUDENTS_TYPE_CHOICES = [
#         ('boys', 'Only Boys'),
#         ('girls', 'Only Girls'),
#         ('combine', 'Combine'),
#     ]

#     CLASS_TYPE_CHOICES = [
#         ('theory', 'Theory'),
#         ('practical', 'Practical'),
#     ]

#     name = models.CharField(max_length=100)
#     code = models.CharField(max_length=20, null=True)  # Subject Code
#     section = models.ForeignKey(Section, on_delete=models.CASCADE, null=True, blank=True)
#     branch = models.ForeignKey(Branch, on_delete=models.CASCADE, null=True, blank=True)
#     semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
#     teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True)  # Optional field
#     no_of_classes = models.IntegerField(null=True)  # Total number of classes per week
#     hours = models.IntegerField(default=1)  # Duration of each class in hours
#     students_in_class = models.CharField(
#         max_length=10, 
#         choices=STUDENTS_TYPE_CHOICES, 
#         default='combine'
#     )
#     Type_of_class = models.CharField(
#         max_length=10, 
#         choices=CLASS_TYPE_CHOICES, 
#         default='Theory'
#     )

#     def __str__(self):
#        return f"{self.name} ({self.code})"
        

# class Class_Room(models.Model):
#     name = models.CharField(max_length=100)
#     Faculty_name = models.CharField(max_length=100,blank=True)

#     def __str__(self):
#         return self.name
    

# class Timetable(models.Model):
#     branch = models.ForeignKey(Branch, on_delete=models.CASCADE, null=True, blank=True)
#     section = models.ForeignKey(Section, on_delete=models.CASCADE, null=True, blank=True)
#     semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
#     day = models.CharField(max_length=20)  # E.g., 'Monday', 'Tuesday'
#     time_slot = models.CharField(max_length=20)  # E.g., '7:00', '7:55'
#     subject = models.ForeignKey(Subject, on_delete=models.CASCADE, null=True, blank=True)
#     # code = models.CharField(max_length=20, null=True)
#     room = models.ForeignKey(Class_Room, on_delete=models.CASCADE, null=True, blank=True)
#     teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True)  # Optional field

#     def __str__(self):
#         return f"{self.day} {self.time_slot} - {self.subject} ({self.branch or self.section})"