from django.shortcuts import render, redirect, get_object_or_404 
from .models import Branch, Semester, Subject, Teacher, Section

def home(request):
    branches = Branch.objects.all()
    sections = Section.objects.all()
    return render(request, 'allotments/home.html', {'branches': branches, 'sections': sections})

def teacher_allocation_by_branch(request, branch_id):
    branch = get_object_or_404(Branch, id=branch_id)
    semesters = Semester.objects.filter(number__gte=3, number__lte=8)
    subjects_by_semester = {
        semester: Subject.objects.filter(branch=branch, semester=semester)
        for semester in semesters
    }

    if request.method == "POST":
        for semester, subjects in subjects_by_semester.items():
            for subject in subjects:
                teacher_ids = request.POST.getlist(f'teacher_{subject.id}')  # Get multiple teacher IDs
                
                if teacher_ids:
                    teacher = Teacher.objects.filter(id__in=teacher_ids)
                    subject.teacher.set(teacher)  # Update the ManyToManyField
                    subject.save()
        
        return redirect('allotment_home')  # Reload the page after saving

    context = {
        'branch': branch,
        'semesters': semesters,
        'subjects_by_semester': subjects_by_semester,
        'teacher': Teacher.objects.all(),  # Updated "teachers" to "teacher"
    }
    return render(request, 'allotments/teacher_allotment.html', context)

def teacher_allocation_by_section(request, section_id):
    section = get_object_or_404(Section, id=section_id)
    semesters = Semester.objects.filter(number__in=[1, 2])
    subjects_by_semester = {
        semester: Subject.objects.filter(section=section, semester=semester)
        for semester in semesters
    }

    if request.method == "POST":
        for semester, subjects in subjects_by_semester.items():
            for subject in subjects:
                teacher_ids = request.POST.getlist(f'teacher_{subject.id}')  # Get multiple teacher IDs
                
                if teacher_ids:
                    teacher = Teacher.objects.filter(id__in=teacher_ids)
                    subject.teacher.set(teacher)  # Update the ManyToManyField
                    subject.save()

        return redirect('allotment_home')  # Reload the page after saving

    context = {
        'section': section,
        'semesters': semesters,
        'subjects_by_semester': subjects_by_semester,
        'teacher': Teacher.objects.all(),  # Updated "teachers" to "teacher"
    }
    return render(request, 'allotments/Section_teacher_allotment.html', context)

