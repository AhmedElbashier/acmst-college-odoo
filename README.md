# ACMST College Odoo Management System

A comprehensive Odoo-based management system for Al Madain College for Medical Science & Technology (ACMST), designed to handle all aspects of college administration, student management, and academic operations.

## 🏥 About ACMST College

Al Madain College for Medical Science & Technology is a leading medical education institution committed to providing high-quality medical education and training. This Odoo system is specifically designed to meet the unique needs of medical education institutions.

## 📦 Available Modules

### 1. ACMST Core Settings (`acmst_core_settings`) - Foundation Module
**Version**: 17.0.1.0.0 | **Sequence**: 1

Core foundation module providing:
- **University Management**: Complete university/institution management with contact information and branding
- **College Structure**: Department and college hierarchy management with dean assignments
- **Academic Programs**: Comprehensive program type and program management
- **Batch Management**: Advanced batch creation and management with wizard
- **Academic Years**: Academic year configuration and semester management
- **Academic Rules**: Configurable academic policies and regulations system

### 2. ACMST Admission Management (`acmst_admission`) - Student Intake Module
**Version**: 1.0.0 | **Sequence**: 2

Advanced admission management system featuring:
- **Enhanced Application Portal**: Multi-step wizard with auto-save and real-time validation
- **Multi-Stage Workflow**: Comprehensive approval process with multiple stages
- **Health Assessment Portal**: Medical questionnaire with BMI calculator and appointment scheduling
- **Conditional Approvals**: Academic coordinator review with conditional requirements and progress tracking
- **Advanced Document Management**: Complete document tracking with workflow integration and bulk upload
- **Real-time Status Tracking**: Live status updates with timeline and notifications
- **Analytics Dashboard**: Comprehensive analytics with data visualization and reporting
- **Advanced Search**: Smart search with filtering, suggestions, and saved searches
- **API Integrations**: Third-party service management and integration monitoring

## 🚀 Key Features

### Core System Features
- **Hierarchical Structure**: University → College → Program → Batch → Student
- **Role-Based Access Control**: 5-tier security system with granular permissions
- **Automatic Code Generation**: Intelligent code generation for all entities
- **Audit Trail**: Complete tracking of all changes and modifications
- **Performance Optimization**: Database indexing and query optimization
- **Multi-Language Support**: Arabic/English interface support

### Advanced Portal Features (Recently Implemented)
- **Multi-Step Application Wizard**: Intuitive application process with progress tracking
- **Real-time Form Validation**: Instant validation with custom error messages
- **Advanced File Upload**: Drag-and-drop with preview and validation
- **Live Status Tracking**: Real-time updates with visual timeline
- **Comprehensive Notifications**: In-app, email, and SMS notifications
- **Health Check Portal**: Medical questionnaire with BMI calculator
- **Conditions Management**: Progress tracking for conditional requirements
- **Document Workflow**: Advanced document management with approval system
- **Analytics Dashboard**: Data visualization with charts and reports
- **Smart Search**: Advanced search with filtering and suggestions
- **API Integrations**: Third-party service management and monitoring

## 📋 System Requirements

- **Odoo Version**: 17.0+
- **Python**: 3.8+
- **Database**: PostgreSQL 12+
- **Memory**: Minimum 4GB RAM
- **Disk Space**: 10GB free space
- **Docker**: For containerized deployment (recommended)

## 🛠️ Installation

### Using Docker (Recommended)

1. **Clone the repository**:
   ```bash
   git clone https://github.com/AhmedElbashier/acmst-college-odoo.git
   cd acmst-college-odoo
   ```

2. **Start the services**:
   ```bash
   docker-compose up -d
   ```

3. **Access Odoo**:
   - Open your browser and go to `http://localhost:8069`
   - Create a new database
   - Install the modules in sequence:
     1. **ACMST Core Settings** (foundation module)
     2. **ACMST Admission Management** (requires core settings)

### Manual Installation

1. **Install Odoo 17** following the [official documentation](https://www.odoo.com/documentation/17.0/administration/install.html)

2. **Copy the modules**:
   ```bash
   cp -r addons/acmst_core_settings /path/to/odoo/addons/
   cp -r addons/acmst_admission /path/to/odoo/addons/
   ```

3. **Update module list** in Odoo configuration and install the modules

## 📁 Project Structure

```
acmst-college-odoo/
├── addons/
│   ├── acmst_core_settings/        # Foundation module (required first)
│   │   ├── models/                 # Core business logic models
│   │   ├── views/                  # User interface views
│   │   ├── wizards/                # Interactive wizards
│   │   ├── security/               # Access rights and groups
│   │   ├── data/                   # Initial data and sequences
│   │   ├── static/                 # CSS, JS, and assets
│   │   └── tests/                  # Comprehensive test suite
│   └── acmst_admission/            # Admission management module
│       ├── models/                 # Admission business logic
│       ├── views/                  # Admission interface views
│       ├── wizards/                # Admission wizards
│       ├── security/               # Admission security settings
│       ├── static/                 # Admission assets
│       ├── reports/                # Admission reports
│       └── tests/                  # Admission test suite
├── config/                         # Odoo configuration files
├── data/                           # Database and filestore
├── logs/                           # Application logs
├── scripts/                        # Utility scripts
├── docker-compose.yml              # Docker configuration
├── env.example                     # Environment template
└── README.md                       # This file
```

## 🎯 Module Overview

### 1. ACMST Core Settings (Foundation Module)

The foundation module that provides the core infrastructure:

- **University Management** (`acmst.university`)
  - University information and configuration
  - Contact details and branding
  - College relationships and hierarchy

- **College Management** (`acmst.college`)
  - College/department structure
  - University associations
  - Dean assignments and management

- **Program Type Management** (`acmst.program.type`)
  - Academic program categories
  - Degree types (Certificate, Diploma, Bachelor's, Master's, PhD)

- **Program Management** (`acmst.program`)
  - Individual academic programs
  - College and program type associations
  - Manager and coordinator assignments

- **Batch Management** (`acmst.batch`)
  - Student batch management
  - Registration periods and capacity
  - Academic year associations
  - Advanced batch creation wizard

- **Academic Year Management** (`acmst.academic.year`)
  - Academic year configuration
  - Semester management
  - Current year tracking

- **Academic Rules Management** (`acmst.academic.rules`)
  - Configurable academic policies
  - Rule levels and categories
  - Compliance tracking

### 2. ACMST Admission Management (Student Intake Module)

The admission management system that handles student intake:

- **Admission Files** (`acmst.admission.file`)
  - Student application management
  - Multi-stage approval workflow
  - Document tracking and management

- **Health Assessment** (`acmst.health.check`)
  - Medical questionnaire integration
  - Health officer reviews
  - Medical requirement tracking

- **Workflow Engine** (`acmst.workflow.engine`)
  - Configurable approval processes
  - State management and transitions
  - Automated workflow progression

- **Portal Integration**
  - Public application portal
  - Student dashboard
  - Application status tracking

- **Coordinator Tools**
  - Conditional approval system
  - Requirement management
  - Academic review tools

## 🔧 Configuration

### Initial Setup Sequence

1. **Install Foundation Module**: Install ACMST Core Settings first
2. **Create Universities**: Add your university/institution information
3. **Create Colleges**: Set up college/department structure
4. **Create Program Types**: Define academic program categories
5. **Create Programs**: Add specific academic programs
6. **Create Academic Years**: Configure academic year periods
7. **Set Up Academic Rules**: Define institutional policies
8. **Install Admission Module**: Install ACMST Admission Management
9. **Configure Admission Workflow**: Set up approval processes

### Batch Creation Wizard

The batch creation wizard (Core Settings module) allows you to:
- Create multiple batches at once
- Set batch parameters (duration, registration periods, capacity)
- Preview batches before creation
- Generate batch codes automatically
- Associate with programs and academic years

### Admission Workflow Configuration

The admission system (Admission Management module) provides:
- Configurable approval stages
- Health assessment integration
- Conditional approval workflows
- Portal configuration options
- Document management settings

## 👥 User Roles & Security

The system includes comprehensive role-based access control:

### Core Settings Security Groups
- **ACMST Core Settings Admin**: Full access to all core functionality
- **ACMST Manager**: College and program management with limited deletion rights
- **ACMST Coordinator**: Program coordination and batch management access
- **ACMST Dean**: College dean access with academic oversight
- **ACMST Viewer**: Read-only access to core settings

### Admission Management Security Groups
- **ACMST Admission Admin**: Full admission system access
- **ACMST Health Officer**: Medical assessment and health check access
- **ACMST Academic Coordinator**: Application review and conditional approvals
- **ACMST Admission Manager**: Admission process management
- **ACMST Portal User**: Student portal access for applications

## 🧪 Testing

Run the comprehensive test suite:

### Using Docker (Recommended)
```bash
# Run all tests for both modules
docker-compose exec odoo python -m pytest addons/acmst_core_settings/tests/ addons/acmst_admission/tests/

# Run specific module tests
docker-compose exec odoo python -m pytest addons/acmst_core_settings/tests/
docker-compose exec odoo python -m pytest addons/acmst_admission/tests/

# Run with coverage
docker-compose exec odoo python -m pytest --cov=addons/acmst_core_settings/ --cov=addons/acmst_admission/
```

### Using Odoo Test Framework
1. Access Odoo → **Apps** → **Update Apps List**
2. Install **Test Framework** if not already installed
3. Run tests from the interface

## 📊 Database Schema

The system uses a comprehensive hierarchical structure:

### Core Settings Schema
```
University
├── College
│   └── Program
│       └── Batch
└── Academic Year
    └── Academic Rules
```

### Admission Management Schema
```
Admission File (extends Batch)
├── Workflow State
├── Health Check
├── Coordinator Conditions
├── Ministry Approval
└── Document Attachments

Student Portal
└── Application Tracking
```

### Complete System Structure
```
University (Core Settings)
├── College (Core Settings)
│   └── Program (Core Settings)
│       ├── Program Type (Core Settings)
│       └── Batch (Core Settings)
│           ├── Academic Year (Core Settings)
│           └── Admission File (Admission Management)
│               ├── Workflow Engine (Admission Management)
│               ├── Health Check (Admission Management)
│               ├── Coordinator Conditions (Admission Management)
│               └── Document Management (Admission Management)
└── Academic Rules (Core Settings)
```

## 🔒 Security

### Comprehensive Security Features

- **Role-based access control** with 10+ security groups
- **Field-level security** for sensitive information
- **Record-level security** with context-aware access
- **Audit trails** for all changes and modifications
- **Hierarchical permissions** based on organizational structure
- **Portal security** for student access
- **Workflow-based approvals** with state management

### Security Groups Summary

#### Core Settings Module (5 groups)
- ACMST Core Settings Admin, Manager, Coordinator, Dean, Viewer

#### Admission Management Module (5 groups)
- ACMST Admission Admin, Health Officer, Academic Coordinator, Admission Manager, Portal User

## 🚀 Future Modules

Planned modules to complete the ACMST College management ecosystem:

### Academic Management Modules
- **Student Management** (`acmst_student`) - Complete student lifecycle management
- **Faculty Management** (`acmst_faculty`) - Faculty and staff administration
- **Course Management** (`acmst_course`) - Course catalog and scheduling
- **Examination System** (`acmst_examination`) - Exam management and grading

### Administrative Modules
- **Fee Management** (`acmst_fees`) - Tuition and fee processing
- **Library Management** (`acmst_library`) - Digital library system
- **Hostel Management** (`acmst_hostel`) - Student accommodation
- **HR Management** (`acmst_hr`) - Human resources and payroll

### Integration Modules
- **Ministry Integration** (`acmst_ministry`) - Government portal integration
- **Analytics & Reporting** (`acmst_analytics`) - Advanced reporting and dashboards
- **Mobile Application** (`acmst_mobile`) - Mobile app for students and staff

## 📚 Documentation

Comprehensive documentation is available for each module:

### ACMST Core Settings (Foundation Module)
- **[README.md](addons/acmst_core_settings/README.md)**: Overview and features
- **[DEPLOYMENT.md](addons/acmst_core_settings/DEPLOYMENT.md)**: Installation and deployment guide
- **[API_REFERENCE.md](addons/acmst_core_settings/docs/API_REFERENCE.md)**: Complete API documentation
- **[INSTALLATION_GUIDE.md](addons/acmst_core_settings/docs/INSTALLATION_GUIDE.md)**: Detailed installation instructions
- **[TECHNICAL_DOCUMENTATION.md](addons/acmst_core_settings/docs/TECHNICAL_DOCUMENTATION.md)**: Technical architecture and implementation
- **[USER_GUIDE.md](addons/acmst_core_settings/docs/USER_GUIDE.md)**: End-user guide and instructions

### ACMST Admission Management (Student Intake Module)
- **[README.md](addons/acmst_admission/README.md)**: Module overview and features
- **[API_REFERENCE.md](addons/acmst_admission/docs/API_REFERENCE.md)**: Complete API documentation
- **[INSTALLATION_GUIDE.md](addons/acmst_admission/docs/INSTALLATION_GUIDE.md)**: Installation instructions
- **[TECHNICAL_DOCUMENTATION.md](addons/acmst_admission/docs/TECHNICAL_DOCUMENTATION.md)**: Technical documentation
- **[USER_GUIDE.md](addons/acmst_admission/docs/USER_GUIDE.md)**: User guide and workflows

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the LGPL-3 License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Ahmed Elbashier**
- GitHub: [@AhmedElbashier](https://github.com/AhmedElbashier)
- Email: ahmedelbashier.2@gmail.com

## 📞 Support

For support and questions:
- Create an issue in this repository
- Contact: ahmedelbashier.2@gmail.com

## 🙏 Acknowledgments

- Odoo Community for the excellent framework
- Medical education institutions for inspiration
- Open source community for continuous support

---

**Note**: This system is specifically designed for medical education institutions and may require customization for other types of educational institutions.