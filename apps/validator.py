import streamlit as st
import pandas as pd

HEADERS = ['isActive','name','subjectRefIds','courseDurationUnit','courseDurationUnitValue','sourceUrl','attendanceType','courseLevel','intakeMonth','intakeYear','academicYear','institutionRefId','campusRefIds','global','globalFeeNotes','globalApplicationFee','eu','euFeeNotes','euApplicationFee','home','homeFeeNotes','homeApplicationFee','currency','degreeAwarded','internationalDeadlineDate','clearingDeadlineDate','clearingStatus','courseCodes','feeDurationUnit','feeDurationValue','courseFormat','placementAvailable','englishTests','coursePeriodMode','coursePeriodModeUnit','courseSummary','programOutlineSummary','programModules','careerProspectus','minimumAgeForEligibility','deliveryLanguage','complianceCheckDeadline','conditionsFulfilmentDeadline','courseDurationHoursPerWeek','courseEndDate','courseStartDate','depositDeadline','enrolmentDeadline','latestArrivalDate','scholarshipDeadline','teachingStartDate','casDeadline']
def doSchemaCheck(columnList,headers):
	return list(set(headers) - set(columnList))             

def app():
    st.title('QC Review')
    st.write('Review the data before post-processing')
    uploaded_file = st.file_uploader("Choose a file")
    if uploaded_file is not None:
        qcDF = pd.read_csv(uploaded_file)
        st.write(f"Uploaded file has {qcDF.shape[0]} rows and {qcDF.shape[1]} columns")
        st.write(f"Performing test please wait..")
        catchRes = doSchemaCheck(qcDF.columns.tolist(), HEADERS)
        if catchRes:
            st.error(f"failed test: incorrect schema or case mismatch, Missing column(s){catchRes}")
        else:
            st.balloons()
            st.success("Schema test passed")
            
        
