# ACMST Admission Management - Security Overview

## Overview

This document provides a comprehensive overview of the security architecture implemented in the ACMST Admission Management System. The system has been designed with multiple layers of security to ensure proper access control, data protection, and role-based permissions.

## Security Groups and Categories

### Admission Management Categories

The system is organized into three main security categories:

#### 1. Admission Administration
- **Admission Administrator**: Full system access, configuration, and administration
- **Workflow Administrator**: Workflow engine and rule management
- **Audit Viewer**: Audit log viewing and system monitoring

#### 2. Admission Approvals
- **Admission Manager**: Final approval authority and oversight
- **Program Coordinator**: Academic approval and program-specific reviews
- **Health Officer**: Medical assessment and health check approvals

#### 3. Admission Operations
- **Admission Officer**: Daily operational tasks and document management
- **University ID Updater**: Specialized role for sensitive University ID updates
- **Document Manager**: Document attachment management and approvals

### Additional Security Groups

#### 4. Specialized Access
- **Portal User**: Limited access to own applications
- **Reports Viewer**: Read-only access to reports and analytics
- **Read-Only User**: Basic read-only access to system data

## Model Access Control

### Core Models

#### AcmstDocument (New)
- **Admin**: Full CRUD access
- **Manager**: Full access except delete
- **Document Manager**: Full access except delete
- **Officer**: Full access except delete
- **Portal**: Limited access to own documents
- **Read-Only**: Read-only access

#### AcmstAdmissionFile
- **Admin**: Full access
- **Manager**: Full access except delete
- **Coordinator**: Access to assigned files and coordinator review state
- **Health**: Access to health-related states
- **Officer**: Full access except delete
- **University ID Updater**: Full access except delete (for sensitive operations)

#### AcmstPortalApplication
- **Admin**: Full access
- **Manager**: Full access except delete
- **Officer**: Full access except delete
- **Portal**: Access to own applications only

### Support Models

#### AcmstHealthCheck
- **Admin**: Full access
- **Health**: Full access except delete
- **Manager**: Read-only access

#### AcmstCoordinatorCondition
- **Admin**: Full access
- **Coordinator**: Access to assigned conditions
- **Manager**: Read-only access

#### AcmstPendingEmail
- **Admin**: Full access
- **Manager**: Full access except delete
- **Officer**: Full access except delete

#### AcmstPerformanceOptimization
- **Admin**: Full access
- **Workflow Admin**: Full access except delete

#### AcmstDashboard
- **Admin**: Full access
- **Manager**: Full access except delete
- **Reports Viewer**: Read-only access

#### AcmstAuditLog
- **Admin**: Full access
- **Manager**: Full access except delete
- **Officer**: Read-only access
- **Audit Viewer**: Read-only access

## Wizard Access Control

### Document Management Wizards
- **Document Rejection Wizard**: Admin, Manager, Document Manager access

### Workflow Wizards
- **Coordinator Condition Wizard**: Admin, Coordinator, Manager access
- **Ministry Approval Wizard**: Admin, Manager, Officer access
- **University ID Update Wizard**: Admin, Manager, Officer, University ID Updater access

## Record Rules

### Data Access Restrictions

#### Admission Files
- **Coordinators**: Can only access files assigned to them or in coordinator review states
- **Health Officers**: Can only access files in health-related states
- **Portal Users**: Can only access their own applications
- **University ID Updaters**: Can access all files for University ID operations

#### Documents
- **Portal Users**: Can only access documents attached to their own applications
- **Coordinators**: Can only access documents attached to files assigned to them

#### Conditions
- **Coordinators**: Can only access conditions assigned to them
- **Wizard Lines**: Can only access lines for conditions assigned to them

## Security Features

### 1. Hierarchical Access Control
- **Admin** > **Manager** > **Specialized Roles** > **Operations** > **Portal Users**
- Each level inherits appropriate permissions from lower levels

### 2. Context-Aware Access
- Record rules ensure users only see data relevant to their role
- Portal users can only access their own data
- Coordinators can only access files assigned to them

### 3. Sensitive Operation Protection
- University ID updates require special permissions
- Document management has specialized roles
- Audit logs are protected with restricted access

### 4. Flexible Role Management
- Multiple roles can be assigned to users
- Roles can be combined for flexible permissions
- Easy to extend with new roles as needed

## Configuration in Settings

### How to Manage Roles

1. **Go to Settings > Users & Companies > Users**
2. **Select a user** or create a new one
3. **Go to the Access Rights tab**
4. **Assign appropriate security groups**:

#### Basic Setup
- **Portal Users**: Assign only "Portal User" group
- **Admission Staff**: Assign "Admission Officer" + "Document Manager" groups
- **Coordinators**: Assign "Program Coordinator" group
- **Health Staff**: Assign "Health Officer" group
- **Managers**: Assign "Admission Manager" group
- **Administrators**: Assign "Admission Administrator" group

#### Advanced Setup
- **University ID Updates**: Assign "University ID Updater" to trusted staff
- **Workflow Management**: Assign "Workflow Administrator" to technical staff
- **Reporting**: Assign "Reports Viewer" to management for read-only access
- **Auditing**: Assign "Audit Viewer" to compliance officers

### Best Practices

1. **Principle of Least Privilege**: Assign only necessary permissions
2. **Role Separation**: Use specialized roles for specific functions
3. **Regular Review**: Regularly audit user permissions
4. **Sensitive Operations**: Restrict University ID and document rejection to authorized personnel

## Security Monitoring

### Audit Logs
- All system activities are logged
- Role-based access to audit logs
- Track user actions and system changes

### Performance Monitoring
- System performance tracking
- Access to performance data restricted to administrators

### Document Management
- Document approval workflows
- Rejection reasons tracked
- File size and type validation

## Future Enhancements

1. **Advanced Permissions**: Field-level security for sensitive data
2. **Time-based Access**: Temporary permissions for specific operations
3. **Multi-tenant Support**: Organization-based data isolation
4. **API Security**: Secure external system integrations
5. **Compliance Reporting**: Automated security compliance reports

---

This security architecture ensures that the ACMST Admission Management System maintains data integrity, protects sensitive information, and provides flexible role-based access control suitable for a complex educational institution environment.
