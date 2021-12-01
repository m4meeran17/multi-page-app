import streamlit as st
import pandas as pd
from pymongo import MongoClient
from io import BytesIO
from pyxlsb import open_workbook as open_xlsb

Subjects_columns=['subjectRefId','isActive','isDeleted','slug','name','globalScore']


def con():
    #mongodb connection
    client = MongoClient()
    #point the client at mongo URI
    client = MongoClient('mongodb+srv://dev_dat_2020:dev_dat_2020@cluster0-d2mfc.mongodb.net')
    #select database
    return client['dat-dev']

def getInstitutionsDF(db,slug=None):
    if slug:    
        institutions_details = db.institutions
        institutions_df_mongo = pd.DataFrame(list(institutions_details.find({'institutionRefId':{'$regex':slug},'isActive':'True'})))
        return institutions_df_mongo
    else:
        institutions_details = db.institutions
        institutions_df_mongo = pd.DataFrame(list(institutions_details.find({'isActive':'True'})))
        return institutions_df_mongo

def getCampusByInstitutionsDF(db,slug):    
    campus_details = db.campus
    campus_df_mongo = pd.DataFrame(list(campus_details.find({'institutionRefId':{'$regex':slug},'isActive':'True'})))
    return campus_df_mongo

def getSubjectsDF(db):
    subjects_details = db.subjects
    subjects_df_mongo = pd.DataFrame(list(subjects_details.find({'isActive':'True'})))
    return subjects_df_mongo
    
def filterSubjectsCollection(coursesDF,subjects_df_mongo):
    subs = coursesDF.subjectRefIds.unique().tolist()
    subDF = pd.DataFrame(columns=Subjects_columns)
    subjectsList = []
    for sub in subs:
        if "," in sub:
            sub = sub.split(",")
            subjectsList.extend(sub)
        else:
            subjectsList.append(sub)
    sortedSubjectsList = sorted(set(subjectsList))
    return subjects_df_mongo.loc[subjects_df_mongo.subjectRefId.isin(sortedSubjectsList),Subjects_columns]

def getCourseDetailsDF(db,slug):    
    courses_details = db.courses
    courses_df_mongo = pd.DataFrame(list(courses_details.find({'courseRefId':{'$regex':slug},'isActive':'True'})))
    intakes_details = db.intakes
    intakes_df_mongo = pd.DataFrame(list(intakes_details.find({'intakeRefId':{'$regex':slug},'isActive':'True'})))
    attendances_details = db.attendances
    attendances_df_mongo = pd.DataFrame(list(attendances_details.find({'attendanceRefId':{'$regex':slug},'isActive':'True'})))
    durations_details = db.durations
    durations_df_mongo = pd.DataFrame(list(durations_details.find({'durationRefId':{'$regex':slug},'isActive':'True'})))
    return courses_df_mongo, intakes_df_mongo, attendances_df_mongo, durations_df_mongo

def courseConcat(element):
    return 'C~'+ element
def intakeConcat(element):
    return 'I~'+element
def attendanceConcat(element):
    return 'A~'+element
def durationConcat(element):
    return 'D~'+element

def app():
    st.title('Data Exporter')
    st.write("Export the raw Data from Mongo")

    db = con()
    activeInstitutions = getInstitutionsDF(db)
    activeInstitutionsList = ['None']
    activeInstitutionsList.extend(activeInstitutions.slug.to_list())
    InstitutionsOption = st.selectbox(
            'Select an institution to export',
            activeInstitutionsList
            )

    coursesFilteredByInstitution,intakesFilteredByInstitution,attendancesFilteredByInstitution,durationsFilteredByInstitution = getCourseDetailsDF(db,InstitutionsOption)
    coursesFilteredByInstitutionColumns = coursesFilteredByInstitution.columns.tolist()
    intakesFilteredByInstitutionColumns = intakesFilteredByInstitution.columns.tolist()
    attendancesFilteredByInstitutionColumns = attendancesFilteredByInstitution.columns.tolist()
    durationsFilteredByInstitutionColumns = durationsFilteredByInstitution.columns.tolist()
    coursesFilteredByInstitutionColumnsMap = map(courseConcat,coursesFilteredByInstitutionColumns)
    intakesFilteredByInstitutionColumnsMap = map(intakeConcat,intakesFilteredByInstitutionColumns)
    attendancesFilteredByInstitutionColumnsMap = map(attendanceConcat,attendancesFilteredByInstitutionColumns)
    durationsFilteredByInstitutionColumnsMap = map(durationConcat,durationsFilteredByInstitutionColumns)
    
    columnsFilter = list(coursesFilteredByInstitutionColumnsMap) + list(intakesFilteredByInstitutionColumnsMap) + list(attendancesFilteredByInstitutionColumnsMap) + list(durationsFilteredByInstitutionColumnsMap)
    st.write(f'{InstitutionsOption} has: {coursesFilteredByInstitution.shape[0]} courses')
            
    if InstitutionsOption != "None":
        ColumnOptions = st.multiselect(
            'Select columns',
            columnsFilter,
            columnsFilter
        )
    
    # options = [i.replace("C~","").replace("~I","").replace("A~","").replace("~D","") for i in options]
        courseOptions = [i.replace("C~","") for i in ColumnOptions if "C~" in i]
        intakeOptions = [i.replace("I~","") for i in ColumnOptions if "I~" in i]
        attendanceOptions = [i.replace("A~","") for i in ColumnOptions if "A~" in i]
        durationOptions = [i.replace("D~","") for i in ColumnOptions if "D~" in i]
        
        institutionDF = getInstitutionsDF(db,InstitutionsOption)
        campusDF = getCampusByInstitutionsDF(db,InstitutionsOption)
        coursesDF, intakesDF, attendancesDF, durationDF = getCourseDetailsDF(db,InstitutionsOption)
        subjects_df_mongo = getSubjectsDF(db)
        subjectsDF = filterSubjectsCollection(coursesDF=coursesDF,subjects_df_mongo=subjects_df_mongo)
        
        coursesDF = coursesDF[courseOptions]
        intakesDF = intakesDF[intakeOptions]
        attendancesDF = attendancesDF[attendanceOptions]
        durationDF = durationDF[durationOptions]
        
        output = BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        institutionDF.to_excel(writer, sheet_name='Institutions',index=False)
        campusDF.to_excel(writer, sheet_name='Campus',index=False)
        coursesDF.to_excel(writer, sheet_name='Courses',index=False)
        intakesDF.to_excel(writer, sheet_name='Intakes',index=False)
        attendancesDF.to_excel(writer, sheet_name='Attendances',index=False)
        durationDF.to_excel(writer, sheet_name='Durations',index=False)
        subjectsDF.to_excel(writer, sheet_name='Subjects',index=False)
        writer.save()
        processed_data = output.getvalue()
        onSuccess = st.download_button(label=f'📥 Download the {InstitutionsOption} courses',
            data=processed_data,
            file_name= f'{InstitutionsOption}.xlsx')