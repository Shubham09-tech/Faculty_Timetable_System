from django.http import HttpResponse
from django.shortcuts import render  #for rendering the templates
from django.template.loader import get_template
from xhtml2pdf import pisa
from allotments.models import Teacher, Timetable, Class_Room

def index(request):
    return render(request,'index.html')
    
    


def teachers_timetables(request):
    teachers = Teacher.objects.all()
    selected_teacher_id = request.GET.get('teacher')
    selected_teacher = Teacher.objects.filter(id=selected_teacher_id).first()
    
    timetable_data = []
    rooms = Class_Room.objects.all()
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    time_slots =['7:00', '7:55', '8:50', '10:00', '10:30', '11:25', '12:20', '1:15', '2:10', '3:05', '4:00']
    
    if selected_teacher:
        timetable_data = Timetable.objects.filter(teacher=selected_teacher)
    
    context = {
        'teachers': teachers,
        'selected_teacher': selected_teacher,
        'selected_teacher_id': selected_teacher_id,
        'timetable_data': timetable_data,
        'rooms': rooms,
        'days': days,
        'time_slots': time_slots,
    }
    
    return render(request, 'Teachers_tt_show.html', context)



def generate_pdf(request):
    selected_teacher_id = request.GET.get('teacher')
    teacher = Teacher.objects.filter(id=selected_teacher_id).first()

    if not teacher:
        return HttpResponse("Teacher not found", content_type="text/plain")

    timetable_entries = Timetable.objects.filter(teacher=teacher)
    rooms = Class_Room.objects.all()
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    time_slots = ['7:00', '7:55', '8:50', '10:00', '10:30', '11:25', '12:20', '1:15', '2:10', '3:05', '4:00']
    template = get_template('teacher_timetable_pdf.html')
    html = template.render({'teacher': teacher, 'timetable_entries': timetable_entries, 'rooms': rooms, 'days': days, 'time_slots': time_slots})

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="timetable.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Error generating PDF', content_type='text/plain')

    return response