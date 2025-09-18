# ACMST College Odoo Management System

A comprehensive Odoo-based management system for Al Madain College for Medical Science & Technology (ACMST), designed to handle all aspects of college administration, student management, and academic operations.

## 🏥 About ACMST College

Al Madain College for Medical Science & Technology is a leading medical education institution committed to providing high-quality medical education and training. This Odoo system is specifically designed to meet the unique needs of medical education institutions.

## 🚀 Features

### Core Settings Module (`acmst_core_settings`)
- **University Management**: Complete university/institution management
- **College Structure**: Department and college hierarchy management
- **Academic Programs**: Comprehensive program type and program management
- **Batch Management**: Advanced batch creation and management with wizard
- **Academic Years**: Academic year configuration and management
- **Academic Rules**: Configurable academic rules and policies

### Key Capabilities
- **Batch Creation Wizard**: Create multiple batches with predefined templates
- **Hierarchical Structure**: University → College → Program → Batch
- **Code Generation**: Automatic code generation for all entities
- **Security Groups**: Role-based access control
- **Data Validation**: Comprehensive validation rules
- **Reporting**: Built-in reporting and analytics

## 📋 System Requirements

- **Odoo Version**: 17.0+
- **Python**: 3.8+
- **Database**: PostgreSQL 12+
- **Docker**: For containerized deployment

## 🛠️ Installation

### Using Docker (Recommended)

1. **Clone the repository**:
   ```bash
   git clone https://github.com/AhmedElbashier/acmst-college-odoo.git
   cd acmst-college-odoo
   ```

2. **Configure environment**:
   ```bash
   cp env.example .env
   # Edit .env with your database credentials
   ```

3. **Start the services**:
   ```bash
   docker-compose up -d
   ```

4. **Access Odoo**:
   - Open your browser and go to `http://localhost:8069`
   - Create a new database
   - Install the ACMST Core Settings module

### Manual Installation

1. **Install Odoo 17** following the [official documentation](https://www.odoo.com/documentation/17.0/administration/install.html)

2. **Copy the addons**:
   ```bash
   cp -r addons/* /path/to/odoo/addons/
   ```

3. **Update the addons list** in Odoo and install the module

## 📁 Project Structure

```
acmst-college-odoo/
├── addons/
│   └── acmst_core_settings/          # Main core settings module
│       ├── models/                   # Data models
│       ├── views/                    # User interface views
│       ├── wizards/                  # Interactive wizards
│       ├── security/                 # Access rights and groups
│       ├── data/                     # Initial data and sequences
│       ├── static/                   # CSS, JS, and images
│       └── tests/                    # Unit and integration tests
├── config/                          # Odoo configuration files
├── data/                           # Database and filestore
├── logs/                           # Application logs
├── scripts/                        # Utility scripts
├── docker-compose.yml              # Docker configuration
└── README.md                       # This file
```

## 🎯 Module Overview

### ACMST Core Settings

The foundation module that provides:

- **University Management** (`acmst.university`)
  - University information and configuration
  - Code generation and validation
  - College relationships

- **College Management** (`acmst.college`)
  - College/department structure
  - University associations
  - Program relationships

- **Program Type Management** (`acmst.program.type`)
  - Academic program categories
  - Degree types (Bachelor's, Master's, etc.)

- **Program Management** (`acmst.program`)
  - Individual academic programs
  - College and program type associations
  - Batch relationships

- **Batch Management** (`acmst.batch`)
  - Student batch management
  - Registration periods
  - Academic year associations
  - Batch creation wizard

- **Academic Year Management** (`acmst.academic.year`)
  - Academic year configuration
  - Semester management
  - Current year tracking

- **Academic Rules Management** (`acmst.academic.rules`)
  - Configurable academic policies
  - Rule levels and categories
  - Compliance tracking

## 🔧 Configuration

### Initial Setup

1. **Create Universities**: Add your university/institution information
2. **Create Colleges**: Set up college/department structure
3. **Create Program Types**: Define academic program categories
4. **Create Programs**: Add specific academic programs
5. **Create Academic Years**: Configure academic year periods
6. **Set Up Academic Rules**: Define institutional policies

### Batch Creation Wizard

The batch creation wizard allows you to:
- Create multiple batches at once
- Set batch parameters (duration, registration periods, etc.)
- Preview batches before creation
- Generate batch codes automatically

## 👥 User Roles

The system includes predefined user roles:

- **Administrator**: Full system access
- **Manager**: College and program management
- **Coordinator**: Batch and student management
- **Dean**: Academic oversight
- **Viewer**: Read-only access

## 🧪 Testing

Run the test suite:

```bash
# Using Docker
docker-compose exec odoo python -m pytest addons/acmst_core_settings/tests/

# Or using Odoo's test framework
# Access Odoo → Apps → Update Apps List → Install Test Framework
```

## 📊 Database Schema

The system uses a hierarchical structure:

```
University
├── College
│   └── Program
│       └── Batch
│           └── Student (future module)
└── Academic Year
    └── Academic Rules
```

## 🔒 Security

- Role-based access control
- Field-level security
- Record-level security
- Audit trails for all changes

## 🚀 Future Modules

Planned modules for the complete system:

- **Student Management** (`acmst_student`)
- **Faculty Management** (`acmst_faculty`)
- **Course Management** (`acmst_course`)
- **Examination System** (`acmst_examination`)
- **Fee Management** (`acmst_fees`)
- **Library Management** (`acmst_library`)
- **Hostel Management** (`acmst_hostel`)

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