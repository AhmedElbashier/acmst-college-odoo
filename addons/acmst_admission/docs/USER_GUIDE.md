# ACMST Admission Module - User Guide

## Table of Contents
1. [Overview](#overview)
2. [Getting Started](#getting-started)
3. [Portal Access](#portal-access)
4. [Admission Process](#admission-process)
5. [Health Check System](#health-check-system)
6. [Coordinator Conditions](#coordinator-conditions)
7. [Manager Approval](#manager-approval)
8. [Processing Students](#processing-students)
9. [Reports and Analytics](#reports-and-analytics)
10. [Troubleshooting](#troubleshooting)

## Overview

The ACMST Admission Module is a comprehensive system for managing college admissions. It provides:

- **Online Application Portal**: Students can submit applications online
- **Health Check System**: Medical assessment and fitness evaluation
- **Coordinator Conditions**: Program-specific requirements management
- **Manager Approval**: Multi-level approval workflow
- **Processing Students Management**: Students approved without university ID (من طلاب المعالجات)
- **Progress Tracking**: Real-time status updates
- **Document Management**: Secure file upload and storage
- **Email Notifications**: Automated communication
- **Reporting**: Analytics and performance monitoring

## Getting Started

### Accessing the System

#### For Administrators
1. Log in to Odoo with admin credentials
2. Navigate to **Admission** menu
3. Access all admission management features

#### For Students/Applicants
1. Visit the portal URL: `https://your-domain.com/my/admission`
2. Create an account or log in
3. Submit your application

### User Roles

#### Administrator
- Full system access
- User management
- System configuration
- Performance monitoring

#### Manager
- View all applications
- Approve/reject applications
- Generate reports
- Monitor performance

#### Coordinator
- Set program conditions
- Review applications
- Manage requirements
- Track progress

#### Health Staff
- Conduct health checks
- Manage medical records
- Generate health reports
- Update fitness status

#### Officer
- Process applications
- Manage documents
- Update application status
- Communicate with applicants

#### Student/Applicant
- Submit applications
- Upload documents
- Track application status
- Receive notifications

## Processing Students

### Overview

Processing Students (من طلاب المعالجات) are students who have been approved by the ministry but do not yet have a university ID. These students are marked with a special status and appear with muted styling in the admission system.

### For Officers and Managers

#### Viewing Processing Students
1. Go to **Applications** → **Processing Students (من طلاب المعالجات)**
2. Use the filter "⏳ Processing Students" in any admission file view
3. Look for records with muted/gray styling

#### Managing Processing Students
1. **Update University ID**: Use the "Update University ID" button when available
2. **Track Status**: Monitor students waiting for university ID assignment
3. **Generate Reports**: Include processing students in admission reports

### For Students

Students approved without university ID:
- Are marked as "Processing Students" in the system
- Can continue with other admission requirements
- Will be updated when university ID becomes available
- Receive notifications when their status changes

### Processing Student Workflow

1. **Ministry Approval**: Student approved by ministry
2. **No University ID**: Marked as processing student if no ID provided
3. **Health Check**: Continue with medical assessment
4. **Coordinator Review**: Academic evaluation continues
5. **University ID Update**: ID added when available
6. **Final Approval**: Complete admission process

## Portal Access

### Creating an Account
1. Visit the portal URL
2. Click **Sign Up**
3. Fill in your details:
   - Full Name
   - Email Address
   - Phone Number
   - Password
4. Verify your email
5. Log in to your account

### Portal Dashboard
The portal dashboard shows:
- **Application Status**: Current stage of your application
- **Required Documents**: Documents you need to upload
- **Health Check Status**: Medical assessment progress
- **Coordinator Conditions**: Program-specific requirements
- **Notifications**: Important updates and messages

### Submitting an Application
1. Click **New Application**
2. Fill in the application form:
   - Personal Information
   - Academic Background
   - Program Selection
   - Contact Details
3. Upload required documents
4. Review and submit
5. Receive confirmation email

## Admission Process

### Application States

#### 1. Draft
- Application is being prepared
- Can be edited and saved
- Not yet submitted

#### 2. Submitted
- Application has been submitted
- Under initial review
- Cannot be edited

#### 3. Under Review
- Application is being evaluated
- Additional information may be requested
- Status updates provided

#### 4. Health Check Required
- Medical assessment needed
- Health check form available
- Upload medical documents

#### 5. Coordinator Review
- Program coordinator evaluation
- Conditions may be set
- Additional requirements

#### 6. Manager Approval
- Final approval process
- Manager decision required
- Approval or rejection

#### 7. Approved
- Application approved
- Student record created
- Welcome email sent

#### 8. Rejected
- Application rejected
- Reason provided
- Appeal process available

### Document Upload
1. Go to **My Applications**
2. Select your application
3. Click **Upload Documents**
4. Choose file type:
   - Academic Transcripts
   - Identity Documents
   - Medical Certificates
   - Other Supporting Documents
5. Upload files (max 10MB each)
6. Verify uploads

## Health Check System

### Accessing Health Check
1. Log in to the portal
2. Go to **My Applications**
3. Click **Health Check** for your application
4. Fill in the health questionnaire

### Health Questionnaire
The questionnaire includes:
- **Personal Health History**
- **Family Medical History**
- **Current Medications**
- **Allergies and Conditions**
- **Lifestyle Information**
- **Emergency Contacts**

### Medical Assessment
After submitting the questionnaire:
1. Health staff will review your information
2. Additional tests may be required
3. Medical fitness status will be determined
4. You'll receive notification of the result

### Health Check Status
- **Pending**: Assessment not yet completed
- **In Progress**: Under medical review
- **Approved**: Medically fit for admission
- **Rejected**: Medical concerns identified
- **Additional Tests Required**: More information needed

## Coordinator Conditions

### Understanding Conditions
Coordinator conditions are program-specific requirements set by academic coordinators. They may include:
- **Academic Prerequisites**
- **Language Requirements**
- **Portfolio Submissions**
- **Interview Requirements**
- **Additional Certifications**

### Viewing Conditions
1. Log in to the portal
2. Go to **My Applications**
3. Click **Coordinator Conditions**
4. View all requirements for your program

### Meeting Conditions
1. Review each condition carefully
2. Complete required tasks
3. Upload supporting documents
4. Mark conditions as completed
5. Wait for coordinator approval

### Condition Status
- **Pending**: Not yet started
- **In Progress**: Working on requirement
- **Completed**: Requirement fulfilled
- **Approved**: Coordinator approved
- **Rejected**: Requirement not met

## Manager Approval

### Final Review Process
1. Application reaches manager for final review
2. Manager evaluates:
   - Academic qualifications
   - Health check results
   - Coordinator conditions
   - Overall suitability
3. Manager makes approval decision
4. Applicant receives notification

### Approval Criteria
Managers consider:
- **Academic Performance**
- **Health Fitness**
- **Program Suitability**
- **Documentation Completeness**
- **Coordinator Recommendations**

### After Approval
If approved:
1. Student record is created
2. Student ID is generated
3. Welcome email is sent
4. Access to student portal is provided
5. Enrollment process begins

If rejected:
1. Rejection reason is provided
2. Appeal process is explained
3. Reapplication options are offered

## Reports and Analytics

### Available Reports

#### Application Summary
- Total applications received
- Applications by program
- Status distribution
- Processing times

#### Health Check Report
- Health check completion rates
- Medical fitness statistics
- Common health issues
- Assessment timelines

#### Coordinator Conditions Report
- Condition completion rates
- Average processing time
- Common requirements
- Coordinator performance

#### Performance Dashboard
- System performance metrics
- Query response times
- User activity statistics
- Optimization status

### Generating Reports
1. Go to **Admission** > **Reports**
2. Select report type
3. Set date range and filters
4. Click **Generate Report**
5. Download or view results

### Exporting Data
1. Select the data to export
2. Choose export format (PDF, Excel, CSV)
3. Click **Export**
4. Download the file

## Troubleshooting

### Common Issues

#### Cannot Access Portal
**Problem**: Portal login fails or access denied
**Solutions**:
1. Check your email and password
2. Verify account activation
3. Contact support if issues persist

#### Document Upload Fails
**Problem**: Cannot upload documents
**Solutions**:
1. Check file size (max 10MB)
2. Verify file format (PDF, JPG, PNG)
3. Check internet connection
4. Try uploading one file at a time

#### Application Status Not Updating
**Problem**: Application status appears stuck
**Solutions**:
1. Refresh the page
2. Check for notifications
3. Contact admission office
4. Verify all requirements are met

#### Email Notifications Not Received
**Problem**: Not receiving email updates
**Solutions**:
1. Check spam folder
2. Verify email address
3. Update email preferences
4. Contact technical support

### Getting Help

#### Self-Service
1. Check this user guide
2. Review FAQ section
3. Search knowledge base
4. Check system status

#### Contact Support
- **Email**: admission@acmst.edu
- **Phone**: +1-555-0123
- **Portal**: Submit support ticket
- **Office Hours**: Monday-Friday, 9 AM - 5 PM

#### Emergency Support
For urgent issues:
- **Phone**: +1-555-0124
- **Email**: emergency@acmst.edu
- **Available**: 24/7

## Best Practices

### For Applicants
1. **Complete Applications Thoroughly**: Fill in all required fields
2. **Upload Clear Documents**: Ensure documents are legible
3. **Check Status Regularly**: Monitor your application progress
4. **Respond Promptly**: Reply to requests quickly
5. **Keep Records**: Save confirmation emails and receipts

### For Staff
1. **Process Applications Timely**: Review applications promptly
2. **Communicate Clearly**: Provide clear instructions and feedback
3. **Maintain Records**: Keep accurate documentation
4. **Follow Procedures**: Adhere to established workflows
5. **Monitor Performance**: Use analytics to improve processes

## Security and Privacy

### Data Protection
- All personal data is encrypted
- Access is restricted to authorized personnel
- Regular security audits are conducted
- Data retention policies are followed

### Privacy Rights
- You can request your data
- You can update your information
- You can delete your account
- You can opt out of communications

### Compliance
The system complies with:
- **GDPR** (General Data Protection Regulation)
- **FERPA** (Family Educational Rights and Privacy Act)
- **COPPA** (Children's Online Privacy Protection Act)
- **Institutional Privacy Policies**

---

**Note**: This user guide is regularly updated. Check for the latest version on the portal or contact support for updates.
