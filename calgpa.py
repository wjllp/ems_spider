def calgpa(grade):
    gpa = 0.0
    if grade == '优':
        gpa = 4.0
    elif grade == '良':
        gpa = 3.3
    elif grade == '中':
        gpa = 2.3
    elif grade == '及格':
        gpa = 1.7
    elif grade == '不及格':
        gpa = 0.0
    elif grade == '未评教':
        gpa = 0.0
    else:
        grade = int(grade)
        if grade >= 95:
            gpa = 4.0
        elif grade >= 90 and grade <= 94:
            gpa = 3.7
        elif grade >= 87 and grade <= 89:
            gpa = 3.3
        elif grade >= 83 and grade <= 86:
            gpa = 3.0
        elif grade >= 80 and grade <= 82:
            gpa = 2.7
        elif grade >= 77 and grade <= 79:
            gpa = 2.3
        elif grade >= 73 and grade <= 76:
            gpa = 2.0
        elif grade >= 70 and grade <= 72:
            gpa = 1.7
        elif grade >= 68 and grade <= 69:
            gpa = 1.6
        elif grade >= 66 and grade <= 67:
            gpa = 1.5
        elif grade >= 64 and grade <= 65:
            gpa = 1.4
        elif grade >= 62 and grade <= 63:
            gpa = 1.3
        elif grade == 61:
            gpa = 1.2
        elif grade == 60:
            gpa = 1.0
    return gpa
