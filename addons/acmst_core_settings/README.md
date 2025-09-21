# ACMST Core Settings Module

A comprehensive Odoo 17 module for managing university, college, and academic program settings. This module serves as the foundation for the ACMST College management system.

## 🚀 Features

### Core Functionality
- **University Management** (`acmst.university`): Complete university/institution management with contact information, branding, and statistics
- **College Management** (`acmst.college`): Department/college management with dean assignment and program tracking
- **Program Types** (`acmst.program.type`): Flexible program type system (Certificate, Diploma, Bachelor's, Master's, PhD)
- **Academic Programs** (`acmst.program`): Comprehensive program management with managers and coordinators
- **Batch Management** (`acmst.batch`): Program batch creation and management with student capacity tracking
- **Academic Years** (`acmst.academic.year`): Academic year management with semester support
- **Academic Rules** (`acmst.academic.rules`): Configurable academic policies and regulations system

### Advanced Features
- **Role-Based Access Control**: 5 security groups with hierarchical permissions
- **Batch Creation Wizard**: Efficient creation of multiple batches with predefined templates
- **Automatic Code Generation**: Intelligent code generation for all entities
- **Hierarchical Structure**: University → College → Program → Batch relationships
- **Data Validation**: Comprehensive field validation and business rules
- **Performance Optimization**: Database indexing and query optimization
- **Audit Trail**: Complete tracking of all changes and modifications

## 📋 Requirements

- **Odoo Version**: 17.0+
- **Python**: 3.8+
- **PostgreSQL**: 12+
- **Required Odoo modules**: base, mail, portal, web
- **Memory**: Minimum 4GB RAM recommended
- **Disk Space**: 10GB free space recommended

## 🛠️ Installation

### Method 1: Docker Installation (Recommended)

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
   - Open browser and go to `http://localhost:8069`
   - Create a new database
   - Install the ACMST Core Settings module

### Method 2: Manual Installation

1. **Copy the module**:
   ```bash
   cp -r acmst_core_settings /path/to/odoo/addons/
   ```

2. **Set proper permissions**:
   ```bash
   chown -R odoo:odoo /path/to/odoo/addons/acmst_core_settings
   chmod -R 755 /path/to/odoo/addons/acmst_core_settings
   ```

3. **Install the module**:
   - Login to Odoo as administrator
   - Go to **Apps** menu
   - Click **Update Apps List**
   - Search for "ACMST Core Settings"
   - Click **Install**

## 🔧 Configuration

### Security Groups
The module creates 5 security groups:
- **ACMST Core Settings Admin**: Full access to all functionality
- **ACMST Manager**: Management access with limited deletion rights
- **ACMST Coordinator**: Program coordination access
- **ACMST Dean**: College dean access
- **ACMST Viewer**: Read-only access

### Initial Setup
1. Create your first university
2. Set up colleges under the university
3. Define program types
4. Create academic programs
5. Set up academic years
6. Configure academic rules

## 📚 Usage

### University Management
1. Navigate to **ACMST Core Settings > Configuration > Universities**
2. Create a new university with basic information
3. Set contact details, address, and branding
4. Mark as main university if applicable

### College Management
1. Navigate to **ACMST Core Settings > Configuration > Colleges**
2. Create colleges under universities
3. Assign deans to colleges
4. Set up college-specific information

### Program Management
1. Navigate to **ACMST Core Settings > Programs**
2. Create programs under colleges
3. Assign program types, managers, and coordinators
4. Set academic requirements and duration

### Batch Management
1. Navigate to **ACMST Core Settings > Batches**
2. Create batches for programs
3. Set capacity and dates
4. Use the batch creation wizard for multiple batches

### Academic Rules
1. Navigate to **ACMST Core Settings > Academic Rules**
2. Create rules at university, college, or program level
3. Set rule types, priorities, and effective dates
4. Configure rule hierarchy and relationships

## 🧪 Testing

### Running Tests
```bash
# Run all tests
python addons/acmst_core_settings/tests/test_runner.py --all

# Run specific test types
python addons/acmst_core_settings/tests/test_runner.py --unit
python addons/acmst_core_settings/tests/test_runner.py --performance
python addons/acmst_core_settings/tests/test_runner.py --security

# Run with verbose output
python addons/acmst_core_settings/tests/test_runner.py --all --verbose
```

### Test Coverage
- **Unit Tests**: Model validation, business logic, and computed fields
- **Performance Tests**: Large dataset handling and query optimization
- **Security Tests**: Access control and record rules validation
- **Integration Tests**: Cross-model functionality and workflows

## 🔒 Security

### Access Control
- Hierarchical permissions based on organizational structure
- Record-level security with context-aware access
- Role-based access control with 5 security groups
- Field-level security for sensitive information

### Data Protection
- Input validation and sanitization
- SQL injection prevention
- XSS protection in HTML fields
- Secure password handling

## 📊 Performance

### Optimization Features
- Database indexing on frequently queried fields
- Computed field caching
- Efficient search and filtering
- Memory usage optimization
- Query performance monitoring

### Performance Benchmarks
- University search: < 1 second for 1000 records
- College search: < 1 second for 1000 records
- Program search: < 1 second for 1000 records
- Batch creation: < 5 seconds for 50 batches
- Memory usage: < 100MB increase for large datasets

## 🐛 Troubleshooting

### Common Issues

#### Installation Issues
- **Module not found**: Ensure the module is in the correct addons directory
- **Dependencies missing**: Install required Odoo modules first
- **Permission errors**: Check file permissions and ownership

#### Runtime Issues
- **Validation errors**: Check field constraints and business rules
- **Access denied**: Verify user permissions and security groups
- **Performance issues**: Check database indexes and query optimization

#### Data Issues
- **Missing relationships**: Ensure foreign key constraints are satisfied
- **Invalid dates**: Check date format and business logic validation
- **Duplicate codes**: Ensure unique constraints are respected

### Debug Mode
Enable debug mode in Odoo to see detailed error messages:
```python
# In odoo.conf
debug = True
log_level = debug
```

## 📈 Monitoring

### Log Files
- Application logs: `/var/log/odoo/odoo.log`
- Database logs: PostgreSQL logs
- Module logs: Check Odoo log for module-specific messages

### Performance Monitoring
- Database query performance
- Memory usage tracking
- Response time monitoring
- Error rate tracking

## 🔄 Updates

### Version History
- **v17.0.1.0.0**: Current stable release
  - Complete hierarchical structure implementation
  - Batch creation wizard with templates
  - Advanced security groups and permissions
  - Comprehensive testing suite
  - Performance optimizations and indexing
  - Audit trail functionality

### Module Structure
```
acmst_core_settings/
├── models/              # Core business logic
├── views/               # User interface views
├── wizards/             # Interactive wizards
├── security/            # Access rights and groups
├── data/                # Initial data and sequences
├── static/              # CSS, JS, and assets
└── tests/               # Comprehensive test suite
```

### Upgrade Process
1. Backup your database
2. Update the module files
3. Run the upgrade from Odoo Apps menu
4. Verify functionality with test data
5. Check security group assignments

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

### Code Standards
- Follow Odoo coding standards
- Add comprehensive tests
- Document new features
- Maintain backward compatibility

## 📞 Support

### Getting Help
- Check the troubleshooting section
- Review the test cases for examples
- Check Odoo documentation
- Contact the development team

### Reporting Issues
- Use the issue tracker
- Provide detailed error messages
- Include steps to reproduce
- Attach relevant log files

## 📄 License

This project is proprietary software for ACMST College. All rights reserved.

## 🙏 Acknowledgments

- Odoo Community for the excellent framework
- ACMST College for the requirements and testing
- Development team for the implementation

---

**Note**: This is a production system. Always backup your data before making changes.
