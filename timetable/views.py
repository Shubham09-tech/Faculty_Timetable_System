from django.shortcuts import render, redirect, get_object_or_404,HttpResponse
from allotments.models import Subject, Branch, Section, Semester , Class_Room, Timetable,Teacher, Faculty
from django import template
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.db.models import Q
from django.db.models import Count
from collections import defaultdict
from django.template.loader import get_template
from xhtml2pdf import pisa
# Create your views here.
register = template.Library()

@register.filter
def to(value):
    return range(1, value + 1)
# -----------------------------------------------------

def home(request):
    branches = Branch.objects.all()
    sections = Section.objects.all()
    return render(request, 'timetable/tt_home.html', {'branches': branches, 'sections': sections})

def select_semester(request, entity_type, entity_id):
    if entity_type == 'section':
        section = get_object_or_404(Section, id=entity_id)
        semesters = [1, 2]
        return render(request, 'timetable/tt_sec.html', {'section': section, 'semesters': semesters})
    elif entity_type == 'branch':
        branch = get_object_or_404(Branch, id=entity_id)
        semesters = range(3, 9)
        return render(request, 'timetable/tt_sec.html', {'branch': branch, 'semesters': semesters})
    else:
        return render(request, 'timetable/error.html', {'message': 'Invalid entity type'})



def dashboard(request, entity_type, entity_id, semester): 
    # Check if the entity type is branch or section and filter subjects accordingly
    if entity_type == 'section':
        entity = get_object_or_404(Section, id=entity_id)
        subjects = Subject.objects.filter(section=entity, semester=semester)
        timetable_entries = Timetable.objects.filter(section_id=entity_id, semester=semester)    
    elif entity_type == 'branch':
        entity = get_object_or_404(Branch, id=entity_id)
        subjects = Subject.objects.filter(branch=entity, semester=semester)
        timetable_entries = Timetable.objects.filter(branch_id=entity_id, semester=semester)
    else:
        return render(request, 'timetable/error.html', {'error': 'Invalid entity type'})

    # Retrieve all rooms
    rooms = Class_Room.objects.all()

    # Prepare subject data for HTML, now correctly passing multiple teachers
    subjects_data = [
        {
            "id": subject.id,
            "name": subject.name,
            "teachers": [teacher.name for teacher in subject.teacher.all()],  # List of teacher names
            "code": subject.code,
            "classes_per_week": subject.no_of_classes,
            "class_type": subject.Type_of_class,
            "students_in_class": subject.students_in_class,
            "hours": subject.hours,
        }
        for subject in subjects
    ]

    # Prepare timetable data for HTML, ensuring multiple teachers are handled
    timetable_data = [
        {
            "day": entry.day,
            "time_slot": entry.time_slot,
            "subject_id": entry.subject.id if entry.subject else None,
            "subject_name": entry.subject.name if entry.subject else None,
            "subject_code": entry.subject.code if entry.subject else None,
            "teacher": [teacher.name for teacher in entry.teacher.all()] if entry.teacher.exists() else None,  
            "room_id": entry.room.id if entry.room else None,
            "room_name": entry.room.name if entry.room else None,
        }
        for entry in timetable_entries
    ]

    # Render the dashboard HTML with the necessary data
    return render(request, 'timetable/dashboard.html', {
        'entity': entity,
        'entity_id': entity_id,
        'entity_type': entity_type,
        'semester': semester,
        'subjects': subjects_data,
        'rooms': rooms,
        'days': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'],
        'Time_slots': ['7:00', '7:55', '8:50', '10:00', '10:30', '11:25', '12:20', '1:15', '2:10', '3:05', '4:00'],
        'timetable_data': timetable_data,
    })





@csrf_exempt     
def save_timetable(request, entity_type, entity_id, semester):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print(f"📥 Received Data: {data}")  # Debugging received data
            timetable_entries = data.get('timetable', [])

            if not timetable_entries:
                return JsonResponse({'error': 'Timetable data is missing.'}, status=400)

            semester_instance = get_object_or_404(Semester, number=semester)

            # Delete existing timetable entries for the section or branch
            if entity_type == "section":
                Timetable.objects.filter(semester=semester_instance, section_id=entity_id).delete()
            elif entity_type == "branch":
                Timetable.objects.filter(semester=semester_instance, branch_id=entity_id).delete()
            
            # Save new timetable entries
            for entry in timetable_entries:
                day = entry.get('day')
                time_slot = entry.get('time_slot')
                subject_ids = entry.get('subject_ids', [])  # Handle multiple subjects
                room_id = entry.get('room_id')
                teacher_names = entry.get('teacher', [])

                # ✅ Convert `teacher_names` from string to list (Fix for your issue)
                if isinstance(teacher_names, str):  
                    try:
                        import ast  # Safe way to convert string to list
                        teacher_names = ast.literal_eval(teacher_names)
                    except (SyntaxError, ValueError):
                        teacher_names = []

                if not all([day, time_slot, subject_ids, room_id]):
                    print("⚠️ Missing required timetable data, skipping entry!")
                    continue

                # Fetch required objects
                room = get_object_or_404(Class_Room, id=room_id)

                # ✅ Fetch teachers with exact full names
                teachers = []
                for name in teacher_names:
                    try:
                        teacher = Teacher.objects.get(name=name.strip())  # Strip spaces & match full name
                        teachers.append(teacher)
                    except Teacher.DoesNotExist:
                        print(f"⚠️ Teacher '{name}' not found in the database!")

                if not teachers:
                    print(f"⚠️ No valid teachers found for names: {teacher_names}")

                for subject_id in subject_ids:
                    subject = get_object_or_404(Subject, id=subject_id)

                    # Debugging: Print fetched data
                    print(f"📌 Subject: {subject.name}, Day: {day}, Time Slot: {time_slot}, Room: {room.name}")
                    print(f"👨‍🏫 Assigned Teachers: {[teacher.name for teacher in teachers]}")

                    # Save or update the timetable entry
                    timetable_entry, created = Timetable.objects.update_or_create(
                        day=day,
                        time_slot=time_slot,
                        semester=semester_instance,
                        section_id=entity_id if entity_type == "section" else None,
                        branch_id=entity_id if entity_type == "branch" else None,
                        subject=subject,
                        room=room,
                    )

                    # Assign multiple teachers safely in ManyToMany field
                    timetable_entry.teacher.set(teachers)  # Efficiently set all teachers at once
                    print(f"✅ Teachers saved for {subject.name}")

            return JsonResponse({'message': 'Timetable saved successfully!'})

        except Exception as e:
            print(f"❌ Error saving timetable: {str(e)}")  # Debugging logs
            return JsonResponse({'error': str(e)}, status=500)

                                       
                         

        
def validation_home(request):
    semesters= Semester.objects.all()
   
        
    return render(request,'timetable/validation_home.html',{'semesters': semesters})      


def validation_compare(request):   
    selected_semesters = request.GET.getlist('semesters') 

    if not selected_semesters:
        return render(request, 'timetable/validation_compare.html', {
            'selected_semesters': None,
            'timetable_data': {},
            'conflicts': [],
        })

    all_timetable_data = Timetable.objects.filter(
        semester__id__in=selected_semesters
    ).order_by('branch', 'semester', 'section', 'day', 'time_slot')

    timetable_data = defaultdict(lambda: defaultdict(list))
    conflicts = []
    schedule_map = defaultdict(lambda: {'teachers': {}, 'rooms': {}})

    # ✅ Fix: Get the Faculty ID instead of using a string
    faculty_engineering = Faculty.objects.filter(name="Faculty of Engineering").first()
    if faculty_engineering:
        faculty_engineering_rooms = {
            room.id for room in Class_Room.objects.filter(Faculty_name=faculty_engineering)
        }
    else:
        faculty_engineering_rooms = set()  # If faculty not found, use an empty set

    # ✅ Track class details per day for Faculty of Engineering
    eng_faculty_daywise_classes = defaultdict(lambda: {'girls': set(), 'boys': set()})

    for entry in all_timetable_data:
        branch_name = entry.branch.name if entry.branch else ""
        section_name = entry.section.name if entry.section else ""
        semester_value = f"Sem {entry.semester.number}"

        branch_section_key = f"{branch_name} {section_name}"
        semester_key = f"Semester {entry.semester.number}"

        timetable_data[branch_section_key][semester_key].append(entry)

        key = (entry.day, entry.time_slot)
        room = entry.room

        # ✅ Apply check only for Faculty of Engineering and specific time slots
        if room and room.id in faculty_engineering_rooms and entry.time_slot in ["7:00", "7:55", "8:50"]:
            class_info = f"{entry.subject.name} ({entry.time_slot})"

            if entry.subject.students_in_class == "girls":
                eng_faculty_daywise_classes[entry.day]['girls'].add(class_info)
            elif entry.subject.students_in_class == "boys":
                eng_faculty_daywise_classes[entry.day]['boys'].add(class_info)

        # ✅ Teacher Conflict Check
        teacher_ids = list(entry.teacher.values_list('id', flat=True)) 
        room_id = entry.room.id if entry.room else None

        for teacher_id in teacher_ids:
            if teacher_id in schedule_map[key]['teachers']:
                existing_entry = schedule_map[key]['teachers'][teacher_id]
                existing_branch = existing_entry.branch.name if existing_entry.branch else ""
                existing_section = existing_entry.section.name if existing_entry.section else ""
                existing_sem = f"Sem {existing_entry.semester.number}"
                teacher_name = entry.teacher.filter(id=teacher_id).first().name

                conflicts.append(
                    f"❌ Teacher {teacher_name} has multiple classes on {entry.day} at {entry.time_slot} in: "
                    f"{existing_branch} {existing_section} ({existing_sem}) and {branch_name} {section_name} ({semester_value})"
                )
            else:
                schedule_map[key]['teachers'][teacher_id] = entry  

        # ✅ Room Conflict Check
        if room_id:
            if room_id in schedule_map[key]['rooms']:
                existing_entry = schedule_map[key]['rooms'][room_id]
                existing_branch = existing_entry.branch.name if existing_entry.branch else ""
                existing_section = existing_entry.section.name if existing_entry.section else ""
                existing_sem = f"Sem {existing_entry.semester.number}"

                conflicts.append(
                    f"❌ Room {entry.room.name} is double-booked on {entry.day} at {entry.time_slot} in: "
                    f"{existing_branch} {existing_section} ({existing_sem}) and {branch_name} {section_name} ({semester_value})"
                )
            else:
                schedule_map[key]['rooms'][room_id] = entry  

    # ✅ Engineering Faculty Room Conflicts (Check if both Boys & Girls classes exist on the same day)
    for day, classes in eng_faculty_daywise_classes.items():
        girls_classes = classes['girls']
        boys_classes = classes['boys']

        if girls_classes and boys_classes:  # Conflict only if both exist on the same day
            conflicts.append(
                f"⚠️ Conflict in 'Faculty of Engineering' on {day}: "
                f"Girls-Only Classes → {', '.join(girls_classes)} | "
                f"Boys-Only Classes → {', '.join(boys_classes)}"
            )

    # Remove duplicate conflicts
    conflicts = list(set(conflicts))

    sorted_timetable_data = {k: dict(sorted(v.items())) for k, v in sorted(timetable_data.items())}

    return render(request, 'timetable/validation_compare.html', {
        'selected_semesters': selected_semesters,
        'timetable_data': sorted_timetable_data,  
        'days': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'],
        'time_slots': ['7:00', '7:55', '8:50', '10:00', '10:30', '11:25', '12:20', '1:15', '2:10', '3:05', '4:00'],
        'conflicts': conflicts,  
    })

   
def download_home(request):
    
    branches = Branch.objects.all()  # Fetch all branches
    sections = Section.objects.all()  # Fetch all sections
    semesters = Semester.objects.all()  # Fetch all semesters

    if request.method == "POST":
        selected_branch = request.POST.get("branch")  # Can be empty
        selected_section = request.POST.get("section")  # Can be empty
        selected_semester = request.POST.get("semester")

        if selected_semester:
            if selected_branch:
                return redirect('timetable_download', branch_id=selected_branch, section_id=0, semester_id=selected_semester)
            elif selected_section:
                return redirect('timetable_download', branch_id=0, section_id=selected_section, semester_id=selected_semester)

    return render(request, 'timetable/download_home.html', {'branches': branches, 'sections': sections, 'semesters': semesters})
    

def timetable_download(request, branch_id, section_id, semester_id):
    semester = get_object_or_404(Semester, id=semester_id)

    # Initialize variables
    branch = None
    section = None
    timetable_entries = []

    # Fetch branch and section based on the given IDs
    if branch_id != 0:  # Branch is selected
        branch = get_object_or_404(Branch, id=branch_id)
        timetable_entries = Timetable.objects.filter(branch=branch, semester=semester)
    elif section_id != 0:  # Section is selected
        section = get_object_or_404(Section, id=section_id)
        timetable_entries = Timetable.objects.filter(section=section, semester=semester)
    else:
        return HttpResponse('Invalid Selection', status=400)

    # Example: Get all days and time slots (assuming these are predefined)
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    time_slots = ["7:00", "7:55", "8:50", "10:00", "10:30", "11:25", "12:20", "1:15", "2:10", "3:05", "4:00"]

    # Prepare the timetable data
    timetable_data = []
    for entry in timetable_entries:
        timetable_data.append({
            'day': entry.day,
            'time_slot': entry.time_slot,
            'subject_name': entry.subject.name,
            'subject_code': entry.subject.code,
            'teacher_names': ', '.join([teacher.name for teacher in entry.teacher.all()]) if entry.teacher.exists() else "N/A",
            'room_name': entry.room,
        })

    # Pass the data to the template
    context = {
        'branch': branch,
        'section': section,
        'semester': semester,
        'timetable_data': timetable_data,
        'days': days,
        'time_slots': time_slots,
    }

    # Render the HTML to a string
    html_content = render(request, 'timetable/download_generator.html', context).content

    # Create a response object
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="timetable.pdf"'

    # Use xml2pdf (pisa) to create the PDF from the HTML content
    pdf = pisa.pisaDocument(html_content, dest=response)

    if pdf.err:
        return HttpResponse('Error generating PDF', status=500)

    return response













































































